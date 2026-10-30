# TraceProof Experimental Methodology

## Research question and objective

Under controlled synthetic dependency graphs and injected deletion failures, how does dependency-aware verification compare with root-record-only verification in detecting incomplete deletion? This benchmark evaluates that question on the defined simulation; it makes no claim of universal novelty or superiority.

## System and data

The local research path is React/Vite -> FastAPI -> in-memory Python benchmark. It uses no AWS credentials and performs no cloud operations. The optional AWS architecture is a separate integration and no AWS deployment status is implied by local results. Synthetic resources have IDs, reverse dependency links (`depends_on`), an existence flag, and a failure-injection flag. A seeded random generator creates bounded DAG edges and configured failures. Explicit scenario generators provide chain, branching, isolated-root, and cycle structures.

## Experimental protocol

Each scenario/trial creates one graph and one failure assignment. Each method receives a deep copy of this same input. The selected root is `resource_0000`. The registered dependency closure consists of the root and all resources that transitively depend on it; traversal tracks visited IDs and therefore terminates on cycles.

The baseline attempts and observes only the root. It is not passed the dependency closure for its decision. TraceProof attempts and observes every registered resource in the closure. The actual post-operation state of the full closure is retained by the simulator as the common outcome oracle. This oracle is used to score the baseline's root-only report, so failed/unattempted dependents can produce false negatives. For the method-level confusion matrix, a case is incomplete if any resource in that method's resulting registered closure remains.

Scenarios are: no failures; failed root; one failed dependent; multiple failed dependents; multi-level chain; resource without dependents; branching graph; cycle; configured failure probability. The configured probability applies independently to each closure member. Forced scenarios guarantee specific failures and therefore do not model that probability. Graph generation and configured failures share the seeded PRNG stream.

## Metrics

- TP: actual incomplete and reported incomplete.
- TN: actual complete and reported complete.
- FP: actual complete and reported incomplete.
- FN: actual incomplete and reported complete.
- Detection rate = TP / (TP + FN).
- False-negative rate = FN / (TP + FN).
- False-positive rate = FP / (FP + TN).

For a zero denominator, the rate is null (not applicable). Wilson score 95% intervals are used for each proportion. They assume independent Bernoulli cases; trials generated within a scenario/seed may be dependent, so intervals are descriptive. Paired binary correctness is compared with a two-sided exact McNemar/binomial test over discordant pairs. Scenario-wise multiplicity is not adjusted; p-values should not be used as broad evidence. Timing reports mean, median, and sample standard deviation from `perf_counter_ns` around simulated delete attempts. Graph generation, ground truth, aggregation, network time, and AWS latency are excluded. Attempt and target counts expose the work difference.

## Reproducibility and exports

Record the returned experiment ID, complete configuration, random seed, code version, and runtime environment. Same seed/config yields the same graph/failure/outcome sequence, but experiment IDs and timing measurements differ. The API keeps results in process memory for CSV/report export; restarting the process clears them. Trial CSV preserves each method/scenario/trial record; aggregate CSV reports method summaries; Markdown report cites measured values from that run.

## Threats to validity and limits

The closure oracle is only as complete as the registered graph. Missing dependency registrations, untracked copies, external backups, and resources outside the modeled system are not visible. The simulator's failure behavior is simplified; the benchmark does not model permissions, eventual consistency, retries, provider deletion semantics, or physical-media erasure. Timing values are host-specific and represent Python simulation work, not a production cost or cloud latency. The selected synthetic graph families and failure scenarios may not represent operational workloads. The design supports bounded descriptive comparisons, not universal claims.
