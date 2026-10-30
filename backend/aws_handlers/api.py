"""API Gateway HTTP API adapter backed by DynamoDB, SQS, and private S3.

AWS Services used
-----------------
1. Amazon API Gateway (HTTP API)  – routes all browser requests here.
2. AWS Lambda                     – this function handles every route.
3. Amazon DynamoDB                – ResourceTable, RequestTable, ExperimentTable.
4. Amazon SQS                     – enqueues async deletion-verification jobs.
5. Amazon S3                      – stores private verification and experiment reports.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import unquote
from uuid import uuid4

from deletion_engine import SAMPLE_RESOURCES, get_dependency_targets, run_baseline, run_traceproof
from experiment_engine import (
    aggregates_csv,
    research_report,
    run_reproducible_experiment,
    trials_csv,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_BODY_BYTES = 32 * 1024
# Experiment results stored in DynamoDB expire after 7 days (TTL in epoch seconds).
EXPERIMENT_TTL_SECONDS = 7 * 24 * 60 * 60
DEFAULT_EXPERIMENT_CONFIG = {
    "num_resources": 12,
    "dependency_density": 0.15,
    "failure_rate": 0.2,
    "trials": 5,
    "random_seed": 42,
    "dependency_depth": 1,
}


def _runtime_clients():
    import boto3
    from botocore.config import Config

    region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")
    dynamodb = boto3.resource("dynamodb", region_name=region)
    s3_config = Config(region_name=region, signature_version="s3v4", s3={"addressing_style": "virtual"})
    return {
        "resources": dynamodb.Table(os.environ["RESOURCE_TABLE_NAME"]),
        "requests": dynamodb.Table(os.environ["REQUEST_TABLE_NAME"]),
        "experiments": dynamodb.Table(os.environ["EXPERIMENT_TABLE_NAME"]),
        "sqs": boto3.client("sqs", region_name=region),
        "s3": boto3.client("s3", region_name=region, config=s3_config),
        "queue_url": os.environ["DELETION_QUEUE_URL"],
        "report_bucket": os.environ["REPORT_BUCKET"],
    }


def _response(status, payload=None, headers=None, body=None):
    response_headers = {
        "Access-Control-Allow-Origin": os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173"),
        "Vary": "Origin",
    }
    if payload is not None:
        response_headers["Content-Type"] = "application/json"
        body = json.dumps(payload, separators=(",", ":"), default=_json_default)
    response_headers.update(headers or {})
    return {"statusCode": status, "headers": response_headers, "body": body or ""}


def _json_default(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError(f"Unsupported response value: {type(value).__name__}")


def _error(status, detail):
    return _response(status, {"detail": detail})


def _all_items(table, consistent=False):
    items = []
    result = table.scan(ConsistentRead=consistent) if consistent else table.scan()
    items.extend(result.get("Items", []))
    while result.get("LastEvaluatedKey"):
        scan_options = {"ExclusiveStartKey": result["LastEvaluatedKey"]}
        if consistent:
            scan_options["ConsistentRead"] = True
        result = table.scan(**scan_options)
        items.extend(result.get("Items", []))
    return items


def _seed_resources(table):
    for resource_id, resource in SAMPLE_RESOURCES.items():
        item = {"resource_id": resource_id, **resource}
        try:
            table.put_item(Item=item, ConditionExpression="attribute_not_exists(resource_id)")
        except Exception as exc:
            code = getattr(exc, "response", {}).get("Error", {}).get("Code")
            if code not in {"ConditionalCheckFailedException", "ConditionalCheckFailed"}:
                raise


def _experiment_config(payload):
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object.")
    unknown = set(payload) - set(DEFAULT_EXPERIMENT_CONFIG)
    if unknown:
        raise ValueError(f"Unknown configuration field: {sorted(unknown)[0]}")
    config = {**DEFAULT_EXPERIMENT_CONFIG, **payload}
    bounds = {
        "num_resources": (4, 100),
        "trials": (1, 100),
        "random_seed": (0, 2147483647),
        "dependency_depth": (1, 99),
    }
    for name, (minimum, maximum) in bounds.items():
        value = config[name]
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"{name} must be an integer from {minimum} to {maximum}.")
    for name in ("dependency_density", "failure_rate"):
        value = config[name]
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be a number from 0 to 1.")
        config[name] = float(value)
    if config["dependency_depth"] >= config["num_resources"]:
        raise ValueError("dependency_depth must be less than num_resources.")
    if config["num_resources"] * config["trials"] * 9 > 40000:
        raise ValueError("Experiment is too large; reduce resources or trials.")
    return config


# ── Experiment persistence helpers ────────────────────────────────────────────

def _persist_experiment(table, result):
    """Write the experiment summary and full result to DynamoDB.

    The item stores the full result as a JSON string so the export routes can
    reconstruct it without re-running the experiment.  A DynamoDB TTL attribute
    causes the item to expire automatically after EXPERIMENT_TTL_SECONDS.
    """
    ttl = int(time.time()) + EXPERIMENT_TTL_SECONDS
    # DynamoDB item size limit is 400 KB; the full result for typical configs is
    # well under that limit.  Large trial_records are stored separately in S3.
    trial_records = result.pop("trial_records", [])
    item = {
        "experiment_id": result["experiment_id"],
        "ttl": ttl,
        "result_json": json.dumps(result, separators=(",", ":"), default=str),
    }
    table.put_item(Item=item)
    return trial_records


def _persist_trial_records(s3_client, bucket, experiment_id, trial_records):
    """Upload trial-level records to S3 so trials.csv export works across invocations."""
    key = f"experiments/{experiment_id}/trial_records.json"
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(trial_records, separators=(",", ":"), default=str).encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )
    return key


def _load_experiment(table, s3_client, bucket, experiment_id):
    """Fetch the experiment summary from DynamoDB and trial records from S3.

    Returns the reconstructed result dict (with trial_records populated) or
    raises ValueError if not found.
    """
    resp = table.get_item(Key={"experiment_id": experiment_id}, ConsistentRead=True)
    item = resp.get("Item")
    if not item:
        raise ValueError("Experiment result not found.")
    result = json.loads(item["result_json"])
    # Fetch trial records from S3 for CSV exports.
    trial_key = f"experiments/{experiment_id}/trial_records.json"
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=trial_key)
        result["trial_records"] = json.loads(obj["Body"].read().decode("utf-8"))
    except Exception:
        # If trial records are unavailable (e.g. expired), return an empty list.
        result["trial_records"] = []
    return result


# ── Main request dispatcher ───────────────────────────────────────────────────

def handle_event(event, clients):
    http = event.get("requestContext", {}).get("http", {})
    method = http.get("method", "GET").upper()
    path = event.get("rawPath", "/")
    query_params = event.get("queryStringParameters") or {}
    body_text = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64
        body_text = base64.b64decode(body_text).decode("utf-8")
    if len(body_text.encode("utf-8")) > MAX_BODY_BYTES:
        return _error(413, "Request body is too large.")

    try:
        # ── Preflight CORS ────────────────────────────────────────────────────
        if method == "OPTIONS":
            return _response(200, headers={"Access-Control-Allow-Methods": "GET,POST,OPTIONS", "Access-Control-Allow-Headers": "Content-Type"})

        # ── Health check ──────────────────────────────────────────────────────
        if method == "GET" and path in {"/", "/health"}:
            return _response(200, {"name": "TraceProof API", "status": "running", "mode": "synthetic-aws", "service": "TraceProof API"})

        # ── Resource registry ─────────────────────────────────────────────────
        if method == "GET" and path == "/resources":
            _seed_resources(clients["resources"])
            items = _all_items(clients["resources"], consistent=True)
            return _response(200, [
                {"id": item["resource_id"], "name": item["name"], "type": item["type"],
                 "exists": item.get("exists", True), "depends_on": item.get("depends_on", [])}
                for item in items
            ])

        if method == "GET" and path.startswith("/resources/") and path.endswith("/dependencies"):
            resource_id = unquote(path[len("/resources/"):-len("/dependencies")].strip("/"))
            _seed_resources(clients["resources"])
            graph_items = _all_items(clients["resources"], consistent=True)
            graph = {item["resource_id"]: item for item in graph_items}
            try:
                targets = get_dependency_targets(graph, resource_id)
            except ValueError as exc:
                return _error(404, str(exc))
            return _response(200, {"root_resource": resource_id, "targets": [
                {"id": target, "name": graph[target]["name"], "type": graph[target]["type"]}
                for target in targets
            ]})

        # ── Deletion requests ─────────────────────────────────────────────────
        if method == "POST" and path == "/deletion-requests":
            if len(body_text.encode("utf-8")) > MAX_BODY_BYTES:
                return _error(413, "Request body is too large.")
            try:
                body = json.loads(body_text)
            except json.JSONDecodeError:
                return _error(400, "Request body must be valid JSON.")
            if not isinstance(body, dict) or not isinstance(body.get("resource_id"), str) or not body["resource_id"].strip() or len(body["resource_id"]) > 200:
                return _error(422, "resource_id is required and must be a non-empty string of at most 200 characters.")
            if "simulate_failure" in body and type(body["simulate_failure"]) is not bool:
                return _error(422, "simulate_failure must be a boolean.")
            if set(body) - {"resource_id", "simulate_failure"}:
                return _error(422, "Request contains an unsupported field.")

            _seed_resources(clients["resources"])
            resource_id = body["resource_id"]
            if not clients["resources"].get_item(Key={"resource_id": resource_id}, ConsistentRead=True).get("Item"):
                return _error(404, "Resource not found")

            request_id = str(uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            item = {
                "request_id": request_id,
                "resource_id": resource_id,
                "created_at": created_at,
                "updated_at": created_at,
                "status": "Pending",
                "simulation_only": True,
                "simulate_failure": body.get("simulate_failure", False),
            }
            # DynamoDB: persist the deletion request record.
            clients["requests"].put_item(Item=item, ConditionExpression="attribute_not_exists(request_id)")
            try:
                # SQS: enqueue the request ID so the WorkerFunction picks it up.
                clients["sqs"].send_message(
                    QueueUrl=clients["queue_url"],
                    MessageBody=json.dumps({"request_id": request_id}),
                )
            except Exception:
                logger.exception("Could not enqueue deletion request %s", request_id)
                clients["requests"].update_item(
                    Key={"request_id": request_id},
                    UpdateExpression="SET #status = :failed, updated_at = :now, failure_message = :message",
                    ExpressionAttributeNames={"#status": "status"},
                    ExpressionAttributeValues={":failed": "Failed", ":now": datetime.now(timezone.utc).isoformat(), ":message": "Unable to enqueue simulation job."},
                )
                return _error(503, "The deletion job could not be queued. Please retry.")
            return _response(202, {"request_id": request_id, "resource_id": resource_id,
                                   "created_at": created_at, "status": "Pending", "simulation_only": True})

        if method == "GET" and path == "/deletion-requests":
            items = _all_items(clients["requests"], consistent=True)
            items.sort(key=lambda item: item.get("created_at", ""), reverse=True)
            return _response(200, items)

        prefix = "/deletion-requests/"
        if method == "GET" and path.startswith(prefix):
            suffix = path[len(prefix):]
            is_report = suffix.endswith("/report")
            request_id = unquote(suffix[:-len("/report")].strip("/") if is_report else suffix.strip("/"))
            item = clients["requests"].get_item(Key={"request_id": request_id}, ConsistentRead=True).get("Item")
            if not item:
                return _error(404, "Deletion request not found")
            if is_report:
                report_key = item.get("report_key")
                if not report_key:
                    return _error(404, "Verification report is not ready")

                # If caller explicitly asked for a redirect / presigned download link
                redirect_param = (query_params.get("redirect") or "").lower() in {"true", "1"}
                if redirect_param:
                    url = clients["s3"].generate_presigned_url(
                        "get_object",
                        Params={
                            "Bucket": clients["report_bucket"],
                            "Key": report_key,
                            "ResponseContentDisposition": f'attachment; filename="traceproof-report-{request_id}.json"',
                        },
                        ExpiresIn=300,
                    )
                    return _response(302, headers={"Location": url, "Cache-Control": "no-store"})

                # Default: fetch directly from S3 and return the report JSON with CORS headers
                try:
                    s3_resp = clients["s3"].get_object(Bucket=clients["report_bucket"], Key=report_key)
                    raw_body = s3_resp["Body"].read()
                    if isinstance(raw_body, bytes):
                        raw_body = raw_body.decode("utf-8")
                    report_data = json.loads(raw_body)
                    return _response(200, report_data)
                except Exception as exc:
                    logger.warning("Failed to fetch report %s from S3: %s", report_key, exc)
                    fallback_report = {
                        "schema_version": 1,
                        "request_id": request_id,
                        "resource_id": item.get("resource_id"),
                        "request_created_at": item.get("created_at"),
                        "simulation_only": True,
                        "scope": "Registered synthetic dependency closure",
                        "status": item.get("status"),
                        "approach": item.get("approach", "TraceProof"),
                        "targets_checked": item.get("targets_checked", 0),
                        "task_results": item.get("task_results", {}),
                        "remaining_targets": item.get("remaining_targets", []),
                    }
                    return _response(200, fallback_report)
            return _response(200, item)

        # ── Experiment compare ────────────────────────────────────────────────
        if method == "GET" and path == "/experiments/compare":
            baseline = run_baseline(SAMPLE_RESOURCES, "student_001")
            traceproof = run_traceproof(SAMPLE_RESOURCES, "student_001")
            return _response(200, {"simulation_only": True, "baseline": baseline, "traceproof": traceproof})

        # ── Experiment run ────────────────────────────────────────────────────
        if method == "POST" and path == "/experiments/run":
            try:
                config = _experiment_config(json.loads(body_text))
            except (json.JSONDecodeError, ValueError) as exc:
                return _error(422, str(exc))
            result = run_reproducible_experiment(config)

            # Persist experiment summary to DynamoDB (ExperimentTable).
            # Trial records (potentially large) are stored separately in S3.
            try:
                trial_records = _persist_experiment(clients["experiments"], result)
                _persist_trial_records(clients["s3"], clients["report_bucket"], result["experiment_id"], trial_records)
                result["trial_records"] = trial_records
            except Exception:
                logger.exception("Failed to persist experiment %s", result.get("experiment_id"))
                # Non-fatal: the result is still returned to the caller but
                # export routes will return 404 for this experiment_id.

            result.pop("trial_records", None)
            return _response(200, result)

        # ── Experiment export routes ──────────────────────────────────────────
        # These routes reconstruct the full result from DynamoDB + S3 so they
        # work across Lambda invocations and cold starts.

        exp_prefix = "/experiments/"
        if method == "GET" and path.startswith(exp_prefix):
            suffix = path[len(exp_prefix):]
            for export_kind in ("trials.csv", "aggregates.csv", "report.md"):
                if suffix.endswith(f"/{export_kind}"):
                    experiment_id = unquote(suffix[: -len(f"/{export_kind}")].strip("/"))
                    try:
                        result = _load_experiment(
                            clients["experiments"], clients["s3"], clients["report_bucket"], experiment_id
                        )
                    except ValueError as exc:
                        return _error(404, str(exc))

                    if export_kind == "trials.csv":
                        csv_body = trials_csv(result)
                        return _response(
                            200,
                            headers={
                                "Content-Type": "text/csv",
                                "Content-Disposition": f'attachment; filename="traceproof-{experiment_id}-trials.csv"',
                            },
                            body=csv_body,
                        )
                    if export_kind == "aggregates.csv":
                        csv_body = aggregates_csv(result)
                        return _response(
                            200,
                            headers={
                                "Content-Type": "text/csv",
                                "Content-Disposition": f'attachment; filename="traceproof-{experiment_id}-aggregates.csv"',
                            },
                            body=csv_body,
                        )
                    if export_kind == "report.md":
                        md_body = research_report(result)
                        return _response(
                            200,
                            headers={
                                "Content-Type": "text/markdown; charset=utf-8",
                                "Content-Disposition": f'attachment; filename="traceproof-{experiment_id}-report.md"',
                            },
                            body=md_body,
                        )

        return _error(404, "Endpoint not found")
    except Exception:
        logger.exception("TraceProof API request failed")
        return _error(500, "The request could not be completed.")


def lambda_handler(event, context):
    try:
        return handle_event(event, _runtime_clients())
    except Exception:
        logger.exception("TraceProof API runtime initialization failed")
        return _error(500, "The request could not be completed.")
