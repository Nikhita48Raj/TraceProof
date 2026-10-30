import unittest

from fastapi import HTTPException

import main


class LocalApiRegressionTests(unittest.TestCase):
    def setUp(self):
        self.saved_requests = dict(main.requests)
        self.saved_reports = dict(main.reports)
        self.saved_experiments = dict(main.experiment_results)
        main.requests.clear()
        main.reports.clear()
        main.experiment_results.clear()

    def tearDown(self):
        main.requests.clear()
        main.requests.update(self.saved_requests)
        main.reports.clear()
        main.reports.update(self.saved_reports)
        main.experiment_results.clear()
        main.experiment_results.update(self.saved_experiments)

    def test_existing_resource_and_comparison_endpoints(self):
        self.assertEqual({item["id"] for item in main.list_resources()}, set(main.resources))
        self.assertIn("baseline", main.compare_schedulers())
        self.assertIn("traceproof", main.compare_schedulers())

    def test_health_check_endpoint(self):
        health = main.health_check()
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["mode"], "local-simulation")
        root = main.root_info()
        self.assertEqual(root["status"], "running")

    def test_local_deletion_valid_invalid_and_request_lookup(self):
        result = main.create_deletion_request(main.DeletionRequest(resource_id="student_001"))
        self.assertEqual(result["status"], "Verified")
        self.assertEqual(main.get_deletion_request(result["request_id"])["resource_id"], "student_001")
        self.assertEqual(main.list_deletion_requests()[0]["request_id"], result["request_id"])

        # Test report retrieval
        report = main.get_deletion_report(result["request_id"])
        self.assertEqual(report["request_id"], result["request_id"])
        self.assertEqual(report["status"], "Verified")
        self.assertEqual(report["targets_checked"], 3)

        with self.assertRaises(HTTPException) as error:
            main.create_deletion_request(main.DeletionRequest(resource_id="not-registered"))
        self.assertEqual(error.exception.status_code, 404)

        with self.assertRaises(HTTPException) as report_error:
            main.get_deletion_report("missing-req-id")
        self.assertEqual(report_error.exception.status_code, 404)

    def test_local_experiment_exports_need_no_aws(self):
        result = main.run_experiment(main.ExperimentConfig(num_resources=4, dependency_depth=1, trials=1))
        experiment_id = result["experiment_id"]
        self.assertNotIn("trial_records", result)
        self.assertIn("experiment_id", main.export_experiment_trials(experiment_id).body.decode())
        self.assertIn("method,total_trials", main.export_experiment_aggregates(experiment_id).body.decode())
        self.assertIn("Research question", main.export_experiment_report(experiment_id).body.decode())
        with self.assertRaises(HTTPException):
            main.export_experiment_trials("missing")


if __name__ == "__main__":
    unittest.main()
