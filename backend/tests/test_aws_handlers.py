import json
import unittest
from pathlib import Path

import yaml

from aws_handlers.api import handle_event
from aws_handlers.worker import handle_event as handle_worker_event
from deletion_engine import SAMPLE_RESOURCES


class CfnLoader(yaml.SafeLoader):
    pass


def cfn_tag(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        value = loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_sequence(node)
    else:
        value = loader.construct_mapping(node)
    return {tag_suffix: value}


CfnLoader.add_multi_constructor("!", cfn_tag)


class ConditionalError(Exception):
    def __init__(self):
        self.response = {"Error": {"Code": "ConditionalCheckFailedException"}}


class S3PreconditionError(Exception):
    def __init__(self):
        self.response = {"Error": {"Code": "PreconditionFailed"}}


class FakeTable:
    def __init__(self, key):
        self.key = key
        self.items = {}

    def put_item(self, Item, ConditionExpression=None):
        item_key = Item[self.key]
        if ConditionExpression and item_key in self.items:
            raise ConditionalError()
        self.items[item_key] = dict(Item)

    def get_item(self, Key, **kwargs):
        item = self.items.get(Key[self.key])
        return {"Item": dict(item)} if item else {}

    def scan(self, **kwargs):
        return {"Items": [dict(item) for item in self.items.values()]}

    def update_item(self, Key, UpdateExpression, ExpressionAttributeNames, ExpressionAttributeValues, ConditionExpression=None):
        item = self.items.get(Key[self.key])
        if not item:
            raise KeyError(Key[self.key])
        status_name = ExpressionAttributeNames.get("#status", "status")
        values = ExpressionAttributeValues
        if ConditionExpression and " IN " in ConditionExpression:
            allowed = {value for key, value in values.items() if key in {":pending", ":processing"}}
            if item.get(status_name) not in allowed:
                raise ConditionalError()
        elif ConditionExpression and item.get(status_name) != values.get(":processing"):
            raise ConditionalError()
        expression = UpdateExpression.removeprefix("SET ")
        for assignment in expression.split(", "):
            field, value_key = [part.strip() for part in assignment.split(" = ")]
            field = ExpressionAttributeNames.get(field, field)
            item[field] = values[value_key]


class FakeSqs:
    def __init__(self):
        self.messages = []

    def send_message(self, **kwargs):
        self.messages.append(kwargs)


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, **kwargs):
        key = (kwargs["Bucket"], kwargs["Key"])
        if kwargs.get("IfNoneMatch") == "*" and key in self.objects:
            raise S3PreconditionError()
        self.objects[key] = kwargs

    def generate_presigned_url(self, operation, Params, ExpiresIn):
        return f"https://private.example/{Params['Key']}?expires={ExpiresIn}"


def make_clients():
    resources = FakeTable("resource_id")
    requests = FakeTable("request_id")
    return {
        "resources": resources,
        "requests": requests,
        "sqs": FakeSqs(),
        "s3": FakeS3(),
        "queue_url": "https://sqs.example/queue",
        "report_bucket": "private-reports",
    }


def api_event(method, path, body=None):
    return {
        "requestContext": {"http": {"method": method}},
        "rawPath": path,
        "body": json.dumps(body) if body is not None else None,
    }


def response_json(response):
    return json.loads(response["body"])


class AwsApiHandlerTests(unittest.TestCase):
    def setUp(self):
        self.clients = make_clients()

    def test_resource_seed_valid_invalid_and_async_acceptance(self):
        listed = handle_event(api_event("GET", "/resources"), self.clients)
        self.assertEqual(listed["statusCode"], 200)
        self.assertEqual(len(response_json(listed)), len(SAMPLE_RESOURCES))
        dependencies = handle_event(api_event("GET", "/resources/student_001/dependencies"), self.clients)
        self.assertEqual(dependencies["statusCode"], 200)
        self.assertEqual(len(response_json(dependencies)["targets"]), 3)
        missing_dependencies = handle_event(api_event("GET", "/resources/missing/dependencies"), self.clients)
        self.assertEqual(missing_dependencies["statusCode"], 404)

        invalid = handle_event(api_event("POST", "/deletion-requests", {"resource_id": "unknown"}), self.clients)
        self.assertEqual(invalid["statusCode"], 404)
        self.assertEqual(self.clients["sqs"].messages, [])

        accepted = handle_event(api_event("POST", "/deletion-requests", {"resource_id": "student_001"}), self.clients)
        self.assertEqual(accepted["statusCode"], 202)
        payload = response_json(accepted)
        self.assertEqual(payload["status"], "Pending")
        self.assertTrue(payload["simulation_only"])
        self.assertEqual(len(self.clients["sqs"].messages), 1)
        self.assertEqual(self.clients["requests"].items[payload["request_id"]]["status"], "Pending")

    def test_request_validation_and_request_size(self):
        invalid = handle_event(api_event("POST", "/deletion-requests", {"resource_id": "student_001", "simulate_failure": "yes"}), self.clients)
        self.assertEqual(invalid["statusCode"], 422)
        oversized = handle_event({**api_event("POST", "/experiments/run"), "body": " " * 33000}, self.clients)
        self.assertEqual(oversized["statusCode"], 413)
        invalid_experiment = handle_event(api_event("POST", "/experiments/run", {"num_resources": 2}), self.clients)
        self.assertEqual(invalid_experiment["statusCode"], 422)
        experiment = handle_event(api_event("POST", "/experiments/run", {"num_resources": 4, "trials": 1, "random_seed": 7}), self.clients)
        self.assertEqual(experiment["statusCode"], 200)
        experiment_body = response_json(experiment)
        self.assertTrue(experiment_body["simulation_only"])
        self.assertEqual(len(experiment_body["scenarios"]), 9)
        self.assertNotIn("trial_records", experiment_body)

    def test_private_report_link_and_final_request_read(self):
        self.clients["requests"].put_item(Item={"request_id": "req-1", "status": "Verified", "report_key": "reports/req-1.json"})
        report = handle_event(api_event("GET", "/deletion-requests/req-1/report"), self.clients)
        self.assertEqual(report["statusCode"], 302)
        self.assertIn("expires=300", report["headers"]["Location"])
        request = handle_event(api_event("GET", "/deletion-requests/req-1"), self.clients)
        self.assertEqual(response_json(request)["status"], "Verified")


class AwsWorkerTests(unittest.TestCase):
    def setUp(self):
        self.clients = make_clients()
        for resource_id, resource in SAMPLE_RESOURCES.items():
            self.clients["resources"].put_item(Item={"resource_id": resource_id, **resource})

    def add_request(self, request_id="req-1", resource_id="student_001", **extra):
        self.clients["requests"].put_item(Item={"request_id": request_id, "resource_id": resource_id,
                                                 "status": "Pending", **extra})

    def test_transition_s3_report_and_duplicate_delivery_are_idempotent(self):
        self.add_request()
        event = {"Records": [{"body": json.dumps({"request_id": "req-1"}), "attributes": {"ApproximateReceiveCount": "1"}}]}
        handle_worker_event(event, self.clients)
        final = self.clients["requests"].get_item(Key={"request_id": "req-1"})["Item"]
        self.assertEqual(final["status"], "Verified")
        self.assertEqual(final["targets_checked"], 3)
        self.assertEqual(len(self.clients["s3"].objects), 1)
        saved = next(iter(self.clients["s3"].objects.values()))
        report = json.loads(saved["Body"])
        self.assertTrue(report["simulation_only"])
        self.assertEqual(saved["ServerSideEncryption"], "AES256")
        handle_worker_event(event, self.clients)
        self.assertEqual(len(self.clients["s3"].objects), 1)
        first_report = next(iter(self.clients["s3"].objects.values()))["Body"]
        self.clients["requests"].items["req-1"]["status"] = "Processing"  # Simulate a concurrent duplicate after its initial read.
        handle_worker_event(event, self.clients)
        self.assertEqual(next(iter(self.clients["s3"].objects.values()))["Body"], first_report)

    def test_failure_is_distinguished_and_retry_limit_marks_failed(self):
        self.add_request("req-incomplete", simulate_failure=True)
        handle_worker_event({"Records": [{"body": json.dumps({"request_id": "req-incomplete"})}]}, self.clients)
        item = self.clients["requests"].get_item(Key={"request_id": "req-incomplete"})["Item"]
        self.assertEqual(item["status"], "Incomplete")

        self.add_request("req-broken", resource_id="does-not-exist")
        event = {"Records": [{"body": json.dumps({"request_id": "req-broken"}), "attributes": {"ApproximateReceiveCount": "3"}}]}
        with self.assertRaises(ValueError):
            handle_worker_event(event, self.clients)
        broken = self.clients["requests"].get_item(Key={"request_id": "req-broken"})["Item"]
        self.assertEqual(broken["status"], "Failed")
        with self.assertRaises(RuntimeError):
            handle_worker_event(event, self.clients)


class InfrastructureTests(unittest.TestCase):
    def test_template_configures_dlq_encryption_cors_and_private_reports(self):
        template_path = Path(__file__).resolve().parents[2] / "template.yaml"
        template = yaml.load(template_path.read_text(encoding="utf-8"), Loader=CfnLoader)
        resources = template["Resources"]
        self.assertEqual(resources["DeletionQueue"]["Properties"]["RedrivePolicy"]["maxReceiveCount"], {"Ref": "MaxReceiveCount"})
        self.assertTrue(resources["DeletionDeadLetterQueue"]["Properties"]["SqsManagedSseEnabled"])
        report_properties = resources["ReportBucket"]["Properties"]
        self.assertTrue(report_properties["PublicAccessBlockConfiguration"]["BlockPublicPolicy"])
        self.assertEqual(report_properties["BucketEncryption"]["ServerSideEncryptionConfiguration"][0]["ServerSideEncryptionByDefault"]["SSEAlgorithm"], "AES256")
        self.assertEqual(resources["TraceProofHttpApi"]["Properties"]["CorsConfiguration"]["AllowOrigins"], [{"Ref": "FrontendOrigin"}])
        api_events = resources["ApiFunction"]["Properties"]["Events"]
        configured_routes = {(event["Properties"].get("Path"), event["Properties"].get("Method")) for event in api_events.values()}
        self.assertIn(("/deletion-requests/{request_id}/report", "GET"), configured_routes)
        self.assertIn(("/experiments/run", "POST"), configured_routes)
        policy_text = str(resources)
        self.assertNotIn("dynamodb:DeleteItem", policy_text)
        self.assertNotIn("s3:DeleteObject", policy_text)


if __name__ == "__main__":
    unittest.main()
