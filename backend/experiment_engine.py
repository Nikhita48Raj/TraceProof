"""Reproducible synthetic benchmark for root-only and dependency-aware deletion."""

from collections import defaultdict
from copy import deepcopy
import csv
from io import StringIO
from math import comb, sqrt
from random import Random
from statistics import mean, median, stdev
from time import perf_counter_ns
from uuid import uuid4

from deletion_engine import delete_resource, get_dependency_targets

SCENARIOS = (
    "no_failures", "failed_root", "single_dependent_failure",
    "multiple_dependent_failures", "multi_level_chain",
    "resource_without_dependents", "branching_graph", "dependency_cycle",
    "configured_failure_rate",
)
MAX_WORK_UNITS = 40000


def validate_config(config):
    required = {"num_resources", "dependency_density", "failure_rate", "trials", "random_seed"}
    if not required.issubset(config):
        raise ValueError("Experiment configuration is missing required fields")
    if not 4 <= config["num_resources"] <= 100:
        raise ValueError("num_resources must be between 4 and 100")
    if not 0 <= config["dependency_density"] <= 1 or not 0 <= config["failure_rate"] <= 1:
        raise ValueError("dependency_density and failure_rate must be between 0 and 1")
    if not 1 <= config["trials"] <= 100:
        raise ValueError("trials must be between 1 and 100")
    if not 0 <= config["random_seed"] <= 2147483647:
        raise ValueError("random_seed is outside the supported range")
    if config["num_resources"] * config["trials"] * len(SCENARIOS) > MAX_WORK_UNITS:
        raise ValueError("Experiment is too large; reduce resources or trials")


def _empty_graph(count):
    return {
        f"resource_{i:04d}": {
            "name": f"Synthetic resource {i:04d}",
            "type": "Synthetic",
            "depends_on": [],
            "exists": True,
            "fail_delete": False,
        }
        for i in range(count)
    }


def _scenario_graph(count, density, depth, rng, scenario):
    graph = _empty_graph(count)
    ids = list(graph)
    # A rooted random DAG. Edges are child -> prerequisite; traversal discovers dependents.
    for child in range(1, count):
        for parent in range(max(0, child - depth), child):
            if rng.random() < density:
                graph[ids[child]]["depends_on"].append(ids[parent])
    if scenario in {"single_dependent_failure", "multiple_dependent_failures", "multi_level_chain"}:
        for item in graph.values():
            item["depends_on"] = []
        for i in range(1, count):
            graph[ids[i]]["depends_on"] = [ids[i - 1]]
    elif scenario == "resource_without_dependents":
        for item in graph.values():
            item["depends_on"] = [parent for parent in item["depends_on"] if parent != ids[0]]
    elif scenario == "branching_graph":
        for item in graph.values():
            item["depends_on"] = []
        for i in range(1, count):
            graph[ids[i]]["depends_on"] = [ids[0]]
    elif scenario == "dependency_cycle":
        for item in graph.values():
            item["depends_on"] = []
        for i in range(1, count):
            graph[ids[i]]["depends_on"] = [ids[i - 1]]
        graph[ids[0]]["depends_on"] = [ids[-1]]
    return graph


def _inject_failures(graph, scenario, failure_rate, rng):
    root = "resource_0000"
    targets = get_dependency_targets(graph, root)
    descendants = targets[1:]
    if scenario == "failed_root":
        failed = [root]
    elif scenario == "single_dependent_failure":
        failed = descendants[:1]
    elif scenario == "multiple_dependent_failures":
        failed = descendants[:2]
    elif scenario == "configured_failure_rate":
        failed = [target for target in targets if rng.random() < failure_rate]
    else:
        failed = []
    for target in failed:
        graph[target]["fail_delete"] = True
    return failed


def _execute_method(resources, root_id, method):
    state = deepcopy(resources)
    closure = get_dependency_targets(state, root_id)
    # Baseline sees only its attempted root. It cannot inspect registered dependencies.
    targets = closure if method == "TraceProof" else [root_id]
    start = perf_counter_ns()
    retries = 0
    for target in targets:
        success = delete_resource(state, target)
        if not success:
            retries += 1
    elapsed_ms = (perf_counter_ns() - start) / 1_000_000
    observed_remaining = [target for target in targets if state[target]["exists"]]
    # Shared trial ground truth is computed from actual post-run state in the registered closure.
    remaining = [target for target in closure if state[target]["exists"]]
    total_closure = len(closure)
    coverage = len(targets) / total_closure if total_closure > 0 else 1.0
    return {
        "reported_incomplete": bool(observed_remaining),
        "remaining_resource_ids": remaining,
        "remaining_count": len(remaining),
        "targets_checked": len(targets),
        "deletion_attempts": len(targets),
        "execution_time_ms": elapsed_ms,
        "retry_count": retries,
        "dependency_coverage": coverage,
    }


def _metrics(rows):
    actual = [row["ground_truth_incomplete"] for row in rows]
    reported = [row["reported_incomplete"] for row in rows]
    tp = sum(a and r for a, r in zip(actual, reported))
    tn = sum((not a) and (not r) for a, r in zip(actual, reported))
    fp = sum((not a) and r for a, r in zip(actual, reported))
    fn = sum(a and (not r) for a, r in zip(actual, reported))
    incomplete = tp + fn
    complete = tn + fp
    predicted_positive = tp + fp
    timings = [row["execution_time_ms"] for row in rows]
    coverages = [row.get("dependency_coverage", 1.0) for row in rows]

    def proportion_interval(success, total):
        if not total:
            return None
        p = success / total
        z = 1.96
        denom = 1 + z * z / total
        center = (p + z * z / (2 * total)) / denom
        half = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
        return [max(0.0, center - half), min(1.0, center + half)]

    detection_rate = tp / incomplete if incomplete else None
    false_negative_rate = fn / incomplete if incomplete else None
    false_positive_rate = fp / complete if complete else None
    precision = tp / predicted_positive if predicted_positive else None
    recall = detection_rate
    f1_score = (
        (2 * precision * recall) / (precision + recall)
        if (precision is not None and recall is not None and (precision + recall) > 0)
        else (0.0 if (precision is not None and recall is not None and precision == 0 and recall == 0) else None)
    )
    mean_time = mean(timings) if timings else None
    median_time = median(timings) if timings else None
    total_time = sum(timings) if timings else 0.0
    stddev_time = stdev(timings) if len(timings) > 1 else (0.0 if timings else None)
    total_retries = sum(row.get("retry_count", 0) for row in rows)
    mean_coverage = mean(coverages) if coverages else None

    return {
        "total_trials": len(rows),
        "incomplete_deletion_cases": incomplete,
        "true_positive_count": tp,
        "true_negative_count": tn,
        "false_positive_count": fp,
        "false_negative_count": fn,
        "detection_rate": detection_rate,
        "false_negative_rate": false_negative_rate,
        "false_positive_rate": false_positive_rate,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "detection_rate_wilson_95_ci": proportion_interval(tp, incomplete),
        "false_negative_rate_wilson_95_ci": proportion_interval(fn, incomplete),
        "false_positive_rate_wilson_95_ci": proportion_interval(fp, complete),
        "precision_wilson_95_ci": proportion_interval(tp, predicted_positive),
        "mean_execution_time_ms": mean_time,
        "average_processing_time_ms": mean_time,
        "median_execution_time_ms": median_time,
        "total_processing_time_ms": total_time,
        "stddev_execution_time_ms": stddev_time,
        "deletion_attempts": sum(row["deletion_attempts"] for row in rows),
        "dependency_targets_checked": sum(row["targets_checked"] for row in rows),
        "injected_failures": sum(len(row["injected_failures"]) for row in rows),
        "resources_remaining_in_dependency_closure": sum(row["remaining_count"] for row in rows),
        "incomplete_deletion_scenarios_detected": tp,
        "retry_count": total_retries,
        "dependency_coverage": mean_coverage,
        "rate_note": None if incomplete and complete else "Rates with a zero denominator are undefined and returned as null.",
    }


def _paired_comparison(rows):
    pairs = defaultdict(dict)
    for row in rows:
        pairs[(row["scenario"], row["trial"])][row["method"]] = row
    pairs = [p for p in pairs.values() if len(p) == 2]
    discordant_tp = sum(p["TraceProof"]["true_positive"] and p["Baseline"]["false_negative"] for p in pairs)
    discordant_fp = sum(p["TraceProof"]["false_positive"] and p["Baseline"]["true_negative"] for p in pairs)
    # Exact two-sided McNemar binomial test on paired correctness discordances.
    a = sum(p["TraceProof"]["correct"] and not p["Baseline"]["correct"] for p in pairs)
    b = sum(p["Baseline"]["correct"] and not p["TraceProof"]["correct"] for p in pairs)
    n = a + b
    p_value = min(1.0, 2 * sum(comb(n, k) for k in range(min(a, b) + 1) if k <= n) / (2 ** n)) if n else None
    diffs = [p["TraceProof"]["execution_time_ms"] - p["Baseline"]["execution_time_ms"] for p in pairs]
    return {
        "paired_trials": len(pairs),
        "traceproof_only_detected_incomplete": discordant_tp,
        "traceproof_only_false_alarms": discordant_fp,
        "correctness_discordances_traceproof_better": a,
        "correctness_discordances_baseline_better": b,
        "exact_mcnemar_two_sided_p_value": p_value,
        "paired_execution_time_difference_traceproof_minus_baseline_mean_ms": mean(diffs) if diffs else None,
        "paired_execution_time_difference_median_ms": median(diffs) if diffs else None,
        "test_note": "Exact McNemar/binomial comparison uses paired binary correctness; descriptive only, no multiplicity adjustment across scenarios."
    }


def run_reproducible_experiment(config):
    validate_config(config)
    config = {**config, "dependency_depth": config.get("dependency_depth", min(4, config["num_resources"] - 1))}
    if not 1 <= config["dependency_depth"] <= config["num_resources"] - 1:
        raise ValueError("dependency_depth must be between 1 and num_resources - 1")
    experiment_id = str(uuid4())
    rng = Random(config["random_seed"])
    trial_rows = []
    grouped = defaultdict(list)
    scenario_trials = defaultdict(list)
    for scenario in SCENARIOS:
        for trial in range(1, config["trials"] + 1):
            graph = _scenario_graph(config["num_resources"], config["dependency_density"], config["dependency_depth"], rng, scenario)
            root = "resource_0000"
            failed = _inject_failures(graph, scenario, config["failure_rate"], rng)
            closure = get_dependency_targets(graph, root)
            # Paired methods receive exact same input; ground truth from applying each method.
            for method in ("Baseline", "TraceProof"):
                outcome = _execute_method(graph, root, method)
                actual_incomplete = outcome["remaining_count"] > 0
                reported = outcome["reported_incomplete"]
                tp, fn = int(actual_incomplete and reported), int(actual_incomplete and not reported)
                fp, tn = int(not actual_incomplete and reported), int(not actual_incomplete and not reported)
                row = {
                    "experiment_id": experiment_id,
                    "random_seed": config["random_seed"],
                    "configuration": config.copy(),
                    "scenario": scenario,
                    "trial": trial,
                    "method": method,
                    "ground_truth_incomplete": actual_incomplete,
                    "reported_incomplete": reported,
                    "classification": "TP" if tp else "FN" if fn else "FP" if fp else "TN",
                    "true_positive": tp,
                    "false_negative": fn,
                    "false_positive": fp,
                    "true_negative": tn,
                    "targets_checked": outcome["targets_checked"],
                    "deletion_attempts": outcome["deletion_attempts"],
                    "retry_count": outcome["retry_count"],
                    "dependency_coverage": outcome["dependency_coverage"],
                    "remaining_resources": outcome["remaining_resource_ids"],
                    "remaining_count": outcome["remaining_count"],
                    "registered_dependency_targets": len(closure),
                    "injected_failures": failed,
                    "execution_time_ms": outcome["execution_time_ms"]
                }
                row["correct"] = bool(tp or tn)
                trial_rows.append(row)
                grouped[method].append(row)
                scenario_trials[(scenario, method)].append(row)
    summaries = {method: _metrics(items) for method, items in grouped.items()}
    scenarios = [
        {
            "scenario": name,
            "baseline": _metrics(scenario_trials[(name, "Baseline")]),
            "traceproof": _metrics(scenario_trials[(name, "TraceProof")]),
        }
        for name in SCENARIOS
    ]
    base_rate = summaries["Baseline"]["detection_rate"]
    trace_rate = summaries["TraceProof"]["detection_rate"]
    if base_rate is None or trace_rate is None:
        interpretation = "At least one method has no incomplete-deletion cases in its denominator; rates cannot be compared."
    elif trace_rate > base_rate:
        interpretation = "In this controlled simulation, TraceProof detected a larger share of incomplete cases than the root-only baseline."
    elif trace_rate < base_rate:
        interpretation = "In this controlled simulation, the root-only baseline detected a larger share of incomplete cases than TraceProof."
    else:
        interpretation = "In this controlled simulation, both methods detected the same share of incomplete cases."
    return {
        "experiment_id": experiment_id,
        "simulation_only": True,
        "execution_environment": "local API process; synthetic in-memory data",
        "configuration": config,
        "trial_records": trial_rows,
        "baseline": summaries["Baseline"],
        "traceproof": summaries["TraceProof"],
        "scenarios": scenarios,
        "interpretation": interpretation,
        "paired_comparison": _paired_comparison(trial_rows),
        "methodology": {
            "root": "resource_0000",
            "registered_closure": "Root plus all registered reverse dependents, cycle-safe.",
            "ground_truth": "Incomplete when any resource in the registered root dependency closure remains after that method's simulated deletion.",
            "baseline_scope": "Attempts and observes root only; it receives no closure list when making its report.",
            "traceproof_scope": "Attempts and observes all registered closure resources.",
            "classification": "Each reported method outcome is compared with that method's resulting full-closure state; baseline false negatives expose dependent resources it did not observe.",
            "timing": "perf_counter_ns around simulated delete attempts only; graph generation, ground-truth calculation, report aggregation, and network overhead excluded.",
            "uncertainty": "Wilson 95% score intervals for proportions assume independent Bernoulli cases; repeated cases under one seed/scenario may be dependent, so intervals are descriptive.",
            "paired_test": "Exact two-sided McNemar test on paired binary correctness; scenario-specific tests are not multiplicity-adjusted.",
            "limitations": "Only registered synthetic graph resources are represented; missing registrations, untracked copies, external backups, and systems outside the modeled graph are invisible. No physical erasure is measured."
        }
    }


TRIAL_COLUMNS = (
    "experiment_id", "random_seed", "configuration", "scenario", "trial", "method",
    "ground_truth_incomplete", "reported_incomplete", "classification", "targets_checked",
    "deletion_attempts", "retry_count", "dependency_coverage", "remaining_resources", "execution_time_ms"
)


def trials_csv(result):
    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=TRIAL_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in result["trial_records"]:
        writer.writerow({
            key: (_json(row[key]) if key in {"configuration", "remaining_resources"} else row.get(key, ""))
            for key in TRIAL_COLUMNS
        })
    return out.getvalue()


def aggregates_csv(result):
    fields = (
        "experiment_id", "random_seed", "configuration", "method", "total_trials",
        "incomplete_deletion_cases", "true_positive_count", "true_negative_count",
        "false_positive_count", "false_negative_count", "detection_rate", "false_negative_rate",
        "false_positive_rate", "precision", "recall", "f1_score",
        "mean_execution_time_ms", "total_processing_time_ms", "median_execution_time_ms",
        "stddev_execution_time_ms", "deletion_attempts", "dependency_targets_checked",
        "retry_count", "dependency_coverage"
    )
    out = StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for method in ("Baseline", "TraceProof"):
        aggregate = result[method.lower()]
        writer.writerow({
            "experiment_id": result["experiment_id"],
            "random_seed": result["configuration"]["random_seed"],
            "configuration": _json(result["configuration"]),
            "method": method,
            **{key: aggregate.get(key, "") for key in fields if key in aggregate}
        })
    return out.getvalue()


def _json(value):
    import json
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def research_report(result):
    cfg = result["configuration"]
    lines = [
        "# TraceProof Synthetic Research Report",
        "",
        "## Research question",
        "",
        "Under controlled synthetic dependency graphs and injected deletion failures, how does dependency-aware verification compare with root-record-only verification in detecting incomplete deletion?",
        "",
        "## Objectives",
        "",
        "Compare detection outcomes, false-negative prevention, coverage, and execution work on paired, reproducible synthetic trials. Findings apply strictly to this simulation and registered dependency graph.",
        "",
        "## System architecture",
        "",
        "React/Vite dashboard -> local FastAPI experiment endpoint -> in-memory synthetic graph and shared deletion engine. This run was executed locally; it used no AWS resources or credentials.",
        "",
        "## Experimental methodology",
        "",
        f"Experiment ID: `{result['experiment_id']}`",
        f"Configuration: `{_json(cfg)}`",
        "",
        "Both methods start from a deep copy of the same trial graph with the same injected failures. Baseline attempts and observes only the root. TraceProof attempts and observes the registered dependency closure. The method's reported outcome is compared with actual remaining resources in that full closure.",
        "",
        "### Synthetic dataset and scenarios",
        "",
        f"{cfg['num_resources']} resources per graph; random DAG edges are generated with configured density and depth window. Each of {cfg['trials']} trials runs these scenarios: {', '.join(SCENARIOS)}. `random_seed` controls graph and configured-failure generation.",
        "",
        "### Ground truth and metrics",
        "",
        result["methodology"]["ground_truth"],
        "",
        "- **TP**: actual incomplete and reported incomplete.",
        "- **TN**: actual complete and reported complete.",
        "- **FP**: actual complete and reported incomplete.",
        "- **FN**: actual incomplete and reported complete.",
        "- **Detection Rate (Recall)**: TP / (TP + FN).",
        "- **False Negative Rate**: FN / (TP + FN).",
        "- **False Positive Rate**: FP / (FP + TN).",
        "- **Precision**: TP / (TP + FP).",
        "- **F1 Score**: 2 * (Precision * Recall) / (Precision + Recall).",
        "- **Dependency Coverage**: Ratio of checked targets to full closure.",
        "- **Retry Count**: Total simulated retry attempts.",
        "",
        "A zero denominator yields null. Timing covers simulated delete attempts only, measured with `perf_counter_ns`; do not interpret it as cloud latency.",
        "",
        "## Measured results",
        "",
        "| Method | Cases | TP | TN | FP | FN | Detection | FNR | FPR | Precision | F1 | Coverage | Retries | Mean ms | Total ms | SD ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for method in ("Baseline", "TraceProof"):
        m = result[method.lower()]
        f = lambda x: "N/A" if x is None else f"{x:.4f}"
        lines.append(
            f"| {method} | {m['total_trials']} | {m['true_positive_count']} | {m['true_negative_count']} | "
            f"{m['false_positive_count']} | {m['false_negative_count']} | {f(m['detection_rate'])} | "
            f"{f(m['false_negative_rate'])} | {f(m['false_positive_rate'])} | {f(m.get('precision'))} | "
            f"{f(m.get('f1_score'))} | {f(m.get('dependency_coverage'))} | {m.get('retry_count', 0)} | "
            f"{f(m['mean_execution_time_ms'])} | {f(m.get('total_processing_time_ms'))} | {f(m['stddev_execution_time_ms'])} |"
        )
    lines += [
        "",
        "Wilson 95% intervals and the paired exact McNemar comparison are included in the machine-readable API result. They are descriptive; repeated trials and multiple scenarios limit inferential strength.",
        "",
        "## Scenario-level results",
        "",
        "| Scenario | Baseline TP/FN | TraceProof TP/FN | TraceProof Coverage |",
        "|---|---:|---:|---:|",
    ]
    for s in result["scenarios"]:
        tp_cov = f"{s['traceproof'].get('dependency_coverage', 1.0):.2%}"
        lines.append(
            f"| {s['scenario']} | {s['baseline']['true_positive_count']}/{s['baseline']['false_negative_count']} | "
            f"{s['traceproof']['true_positive_count']}/{s['traceproof']['false_negative_count']} | {tp_cov} |"
        )
    lines += [
        "",
        "## Statistical analysis",
        "",
        f"- **Paired Trials Evaluated**: {result['paired_comparison']['paired_trials']}",
        f"- **TraceProof Exclusive Incomplete Detections**: {result['paired_comparison']['traceproof_only_detected_incomplete']}",
        f"- **TraceProof Discordant Correctness Wins**: {result['paired_comparison']['correctness_discordances_traceproof_better']}",
        f"- **Baseline Discordant Correctness Wins**: {result['paired_comparison']['correctness_discordances_baseline_better']}",
        f"- **Exact McNemar Two-Sided p-value**: {result['paired_comparison']['exact_mcnemar_two_sided_p_value']}",
        f"- **Mean Paired Time Delta (TraceProof - Baseline)**: {result['paired_comparison']['paired_execution_time_difference_traceproof_minus_baseline_mean_ms']:.4f} ms" if result['paired_comparison']['paired_execution_time_difference_traceproof_minus_baseline_mean_ms'] is not None else "- **Mean Paired Time Delta**: N/A",
        "",
        "## Threats to validity and limitations",
        "",
        result["methodology"]["limitations"],
        "Synthetic resource operations and timing are simplified. Results depend on graph-generation rules, injected failures, selected seed/configuration, and this runtime environment. No claims about universal superiority, real cloud latency, or physical data erasure are supported.",
        "",
        "## Conclusion",
        "",
        result["interpretation"] if "interpretation" in result else "Use the measured tables above to describe this run only; the benchmark does not support universal claims.",
        "",
    ]
    return "\n".join(lines)
