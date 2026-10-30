import unittest

from pydantic import ValidationError

from deletion_engine import SAMPLE_RESOURCES, delete_resource, get_dependency_targets, run_baseline, run_traceproof
from experiment_engine import (SCENARIOS, _metrics, aggregates_csv, research_report, run_reproducible_experiment,
                               trials_csv, validate_config)
from main import ExperimentConfig, run_experiment


class DeletionEngineTests(unittest.TestCase):
    def test_traverses_registered_dependents_and_handles_cycles(self):
        graph = {
            "root": {"depends_on": ["missing"], "exists": True, "fail_delete": False},
            "child": {"depends_on": ["root"], "exists": True, "fail_delete": False},
            "grandchild": {"depends_on": ["child"], "exists": True, "fail_delete": False},
            "cycle": {"depends_on": ["grandchild"], "exists": True, "fail_delete": False},
        }
        graph["root"]["depends_on"].append("cycle")
        self.assertEqual(get_dependency_targets(graph, "root"), ["root", "child", "grandchild", "cycle"])
        with self.assertRaisesRegex(ValueError, "Unknown resource"):
            get_dependency_targets(graph, "absent")

    def test_successful_and_failed_deletion(self):
        graph = {"x": {"exists": True, "fail_delete": False}}
        self.assertTrue(delete_resource(graph, "x"))
        self.assertFalse(graph["x"]["exists"])
        graph["x"]["exists"] = True
        graph["x"]["fail_delete"] = True
        self.assertFalse(delete_resource(graph, "x"))
        self.assertTrue(graph["x"]["exists"])

    def test_comparison_methods_have_different_scopes_and_independent_state(self):
        original = {key: dict(value) for key, value in SAMPLE_RESOURCES.items()}
        baseline = run_baseline(SAMPLE_RESOURCES, "student_001")
        traceproof = run_traceproof(SAMPLE_RESOURCES, "student_001")
        self.assertEqual(baseline["targets_checked"], 1)
        self.assertEqual(traceproof["targets_checked"], 3)
        self.assertEqual(SAMPLE_RESOURCES, original)


class ExperimentRunnerTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "num_resources": 8,
            "dependency_density": 0.25,
            "failure_rate": 0.4,
            "trials": 2,
            "random_seed": 17,
            "dependency_depth": 3,
        }

    def test_fixed_seed_reproduces_outcomes(self):
        original_resources = {key: dict(value) for key, value in SAMPLE_RESOURCES.items()}
        first = run_reproducible_experiment(self.config)
        second = run_reproducible_experiment(self.config)
        for method in ("baseline", "traceproof"):
            for metric in ("true_positive_count", "false_negative_count", "false_positive_count", "injected_failures", "deletion_attempts"):
                self.assertEqual(first[method][metric], second[method][metric])
        self.assertEqual([s["scenario"] for s in first["scenarios"]], [s["scenario"] for s in second["scenarios"]])
        self.assertEqual(SAMPLE_RESOURCES, original_resources)
        self.assertEqual(first["experiment_id"] != second["experiment_id"], True)
        self.assertEqual(first["trial_records"][0]["classification"], second["trial_records"][0]["classification"])

    def test_metric_denominator_and_root_only_false_negatives(self):
        result = run_reproducible_experiment(self.config)
        baseline = result["baseline"]
        traceproof = result["traceproof"]
        self.assertGreater(baseline["false_negative_count"], 0)
        self.assertEqual(baseline["detection_rate"], baseline["true_positive_count"] / (baseline["true_positive_count"] + baseline["false_negative_count"]))
        self.assertEqual(traceproof["false_negative_count"], 0)
        self.assertEqual(result["paired_comparison"]["paired_trials"], len(SCENARIOS) * self.config["trials"])
        self.assertIsNotNone(baseline["detection_rate_wilson_95_ci"])

    def test_ground_truth_and_method_reports_use_shared_starting_graph(self):
        result = run_reproducible_experiment({**self.config, "trials": 1})
        baseline = next(row for row in result["trial_records"] if row["scenario"] == "single_dependent_failure" and row["method"] == "Baseline")
        traceproof = next(row for row in result["trial_records"] if row["scenario"] == "single_dependent_failure" and row["method"] == "TraceProof")
        self.assertTrue(baseline["ground_truth_incomplete"])
        self.assertEqual(baseline["classification"], "FN")
        self.assertEqual(traceproof["classification"], "TP")
        self.assertEqual(baseline["deletion_attempts"], 1)
        self.assertGreater(traceproof["deletion_attempts"], 1)

    def test_no_incomplete_cases_rates_are_undefined(self):
        result = run_reproducible_experiment({**self.config, "failure_rate": 0})
        isolated = next(s for s in result["scenarios"] if s["scenario"] == "resource_without_dependents")
        self.assertIsNone(isolated["baseline"]["detection_rate"])
        self.assertIn("undefined", isolated["baseline"]["rate_note"])

    def test_config_validation_and_api_shape(self):
        with self.assertRaises(ValidationError):
            ExperimentConfig(num_resources=2)
        with self.assertRaises(ValidationError):
            ExperimentConfig(failure_rate=1.2)
        response = run_experiment(ExperimentConfig(**self.config))
        self.assertTrue(response["simulation_only"])
        self.assertEqual(response["configuration"], self.config)
        self.assertIn("baseline", response)
        self.assertIn("traceproof", response)
        self.assertEqual(len(response["scenarios"]), 9)
        self.assertIn("interpretation", response)

    def test_different_config_changes_trial_design(self):
        first = run_reproducible_experiment(self.config)
        changed = run_reproducible_experiment({**self.config, "dependency_density": 0.9})
        self.assertNotEqual(first["trial_records"][0]["registered_dependency_targets"], changed["trial_records"][0]["registered_dependency_targets"])

    def test_csv_escaping_report_and_zero_denominators(self):
        result = run_reproducible_experiment({**self.config, "failure_rate": 0})
        trial_csv = trials_csv(result)
        self.assertIn("experiment_id,random_seed,configuration", trial_csv)
        self.assertIn('"dependency_depth"', trial_csv)
        self.assertIn("method,total_trials", aggregates_csv(result))
        report = research_report(result)
        self.assertIn("Threats to validity", report)
        self.assertIn("local", report)
        self.assertIsNone(_metrics([])["false_positive_rate"])

    def test_validation_rejects_impractical_or_invalid_config(self):
        with self.assertRaises(ValueError):
            validate_config({**self.config, "num_resources": 100, "trials": 100})
        with self.assertRaises(ValueError):
            run_reproducible_experiment({**self.config, "dependency_depth": 99})


if __name__ == "__main__":
    unittest.main()
