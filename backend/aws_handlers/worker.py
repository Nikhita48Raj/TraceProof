"""Idempotent SQS worker for synthetic deletion verification jobs."""

import json
import logging
import os
from copy import deepcopy
from datetime import datetime, timezone

from deletion_engine import get_dependency_targets, run_traceproof

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TERMINAL = {"Verified", "Incomplete", "Failed"}


def _runtime_clients():
    import boto3

    dynamodb = boto3.resource("dynamodb")
    return {
        "resources": dynamodb.Table(os.environ["RESOURCE_TABLE_NAME"]),
        "requests": dynamodb.Table(os.environ["REQUEST_TABLE_NAME"]),
        "s3": boto3.client("s3"),
        "report_bucket": os.environ["REPORT_BUCKET"],
    }


def _now():
    return datetime.now(timezone.utc).isoformat()


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


def _conditional_failure(exc):
    return getattr(exc, "response", {}).get("Error", {}).get("Code") in {
        "ConditionalCheckFailedException", "ConditionalCheckFailed"
    }


def _mark_processing(table, request_id):
    try:
        table.update_item(
            Key={"request_id": request_id},
            UpdateExpression="SET #status = :processing, updated_at = :now",
            ConditionExpression="#status IN (:pending, :processing)",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":pending": "Pending", ":processing": "Processing", ":now": _now()},
        )
        return True
    except Exception as exc:
        if not _conditional_failure(exc):
            raise
        current = table.get_item(Key={"request_id": request_id}, ConsistentRead=True).get("Item")
        return bool(current and current.get("status") not in TERMINAL)


def _write_terminal(table, request_id, result, report_key, report_created_at):
    values = {
        ":processing": "Processing",
        ":status": result["status"], ":updated": _now(), ":targets": result["targets_checked"],
        ":approach": result["approach"],
        ":tasks": result["task_results"], ":remaining": result["remaining_targets"],
        ":report_key": report_key, ":report_created": report_created_at,
    }
    try:
        table.update_item(
            Key={"request_id": request_id},
            UpdateExpression=("SET #status = :status, updated_at = :updated, approach = :approach, targets_checked = :targets, "
                              "task_results = :tasks, remaining_targets = :remaining, report_key = :report_key, "
                              "report_created_at = :report_created"),
            ConditionExpression="#status = :processing",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues=values,
        )
    except Exception as exc:
        if not _conditional_failure(exc):
            raise
        # A duplicate delivery may have completed first. Never overwrite it.
        current = table.get_item(Key={"request_id": request_id}, ConsistentRead=True).get("Item")
        if current and current.get("status") in TERMINAL:
            return
        raise


def process_request(request_id, clients):
    table = clients["requests"]
    record = table.get_item(Key={"request_id": request_id}, ConsistentRead=True).get("Item")
    if not record:
        raise ValueError("Deletion request record does not exist.")
    if record.get("status") == "Failed" and record.get("failure_message") == "The simulation job failed after its retry limit.":
        # Keep failing the delivery so SQS can move this exhausted message to its DLQ.
        raise RuntimeError("The simulation job exhausted its retry limit.")
    if record.get("status") in TERMINAL:
        logger.info("Skipping duplicate delivery for completed request %s", request_id)
        return record["status"]
    if not _mark_processing(table, request_id):
        current = table.get_item(Key={"request_id": request_id}, ConsistentRead=True).get("Item") or {}
        return current.get("status", "Failed")

    graph_items = _all_items(clients["resources"], consistent=True)
    state = {item["resource_id"]: deepcopy(item) for item in graph_items}
    root_id = record.get("resource_id")
    targets = get_dependency_targets(state, root_id)
    if record.get("simulate_failure") and len(targets) > 1:
        state[targets[-1]]["fail_delete"] = True

    result = run_traceproof(state, root_id)
    report_created_at = _now()
    report_key = f"reports/{request_id}.json"
    report = {
        "schema_version": 1,
        "request_id": request_id,
        "resource_id": root_id,
        "request_created_at": record.get("created_at"),
        "simulation_only": True,
        "scope": "Registered synthetic dependency closure",
        **result,
    }
    try:
        clients["s3"].put_object(
            Bucket=clients["report_bucket"],
            Key=report_key,
            Body=json.dumps(report, separators=(",", ":")).encode("utf-8"),
            ContentType="application/json",
            ServerSideEncryption="AES256",
            IfNoneMatch="*",
        )
    except Exception as exc:
        error = getattr(exc, "response", {}).get("Error", {})
        if error.get("Code") not in {"PreconditionFailed", "412"}:
            raise
        # A concurrent duplicate already wrote this request's deterministic report.
    _write_terminal(table, request_id, result, report_key, report_created_at)
    logger.info("Completed synthetic request %s with status %s", request_id, result["status"])
    return result["status"]


def _mark_failed(table, request_id):
    try:
        table.update_item(
            Key={"request_id": request_id},
            UpdateExpression="SET #status = :failed, updated_at = :now, failure_message = :message",
            ConditionExpression="#status IN (:pending, :processing)",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":pending": "Pending", ":processing": "Processing", ":failed": "Failed",
                                      ":now": _now(), ":message": "The simulation job failed after its retry limit."},
        )
    except Exception as exc:
        if not _conditional_failure(exc):
            logger.exception("Could not mark request %s as failed", request_id)


def handle_event(event, clients, max_receive_count=3):
    for message in event.get("Records", []):
        try:
            body = json.loads(message.get("body", "{}"))
            request_id = body.get("request_id") if isinstance(body, dict) else None
            if not request_id:
                raise ValueError("SQS message is missing request_id.")
            process_request(request_id, clients)
        except Exception:
            attributes = message.get("attributes") or {}
            try:
                receive_count = int(attributes.get("ApproximateReceiveCount", "1"))
            except (TypeError, ValueError):
                receive_count = 1
            request_id = None
            try:
                decoded = json.loads(message.get("body", "{}"))
                request_id = decoded.get("request_id") if isinstance(decoded, dict) else None
            except json.JSONDecodeError:
                pass
            if request_id and receive_count >= max_receive_count:
                _mark_failed(clients["requests"], request_id)
            logger.exception("SQS deletion job failed (receive %s)", receive_count)
            # Raising leaves the message for SQS retry and eventual DLQ redrive.
            raise
    return {"batchItemFailures": []}


def lambda_handler(event, context):
    return handle_event(event, _runtime_clients(), int(os.environ.get("MAX_RECEIVE_COUNT", "3")))
