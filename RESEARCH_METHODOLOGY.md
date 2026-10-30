# TraceProof Research Methodology & Formal Experimental Design

**Document Version:** 1.0.0  
**Authors:** TraceProof Research Engineering  
**Focus:** Cloud Computing, Distributed Deletion Verification, Statistical Evaluation

---

## 1. Research Objective & Hypothesis

### Problem Formulation
Modern enterprise cloud applications maintain data spread across heterogeneous services—relational and NoSQL datastores, object storage, derived reporting pipelines, analytical aggregation tables, and backup repositories. Conventional cloud data deletion processes (here termed the **Baseline Method**) routinely delete only the designated root resource (e.g., a student database record) while assuming that downstream dependent copies are deleted or silently obsolete.

### Core Research Question
*Under controlled synthetic dependency graphs and injected deletion failure modes, how does dependency-aware closure verification (TraceProof) compare with root-record-only verification (Baseline) in detecting incomplete cloud deletions?*

### Formal Hypothesis
- **Null Hypothesis ($H_0$):** There is no significant difference in the detection rate (recall) of incomplete cloud deletion events between root-only verification and dependency-aware verification across synthetic cloud topologies ($p_{\text{TraceProof}} = p_{\text{Baseline}}$).
- **Alternative Hypothesis ($H_1$):** Dependency-aware verification achieves a significantly higher detection rate of incomplete deletions by discovering and inspecting unaddressed dependent resources ($p_{\text{TraceProof}} > p_{\text{Baseline}}$).

---

## 2. Dependency Graph Model

Let the cloud data topology be modeled as a directed acyclic graph (DAG):

$$\mathcal{G} = (\mathcal{V}, \mathcal{E})$$

where:
- $\mathcal{V} = \{v_1, v_2, \dots, v_n\}$ represents the set of registered cloud resources (e.g., primary records in DynamoDB, documents in S3, derived analytical aggregates).
- $\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}$ represents directed dependency relationships. An edge $(u, v) \in \mathcal{E}$ indicates that resource $v$ depends on prerequisite resource $u$ ($u \to v$, where $v$ registers $u \in \text{depends\_on}(v)$).

### Transitive Dependency Closure
For a selected root resource $r \in \mathcal{V}$, the transitive dependency closure $\mathcal{C}(r)$ is defined as the set of all resources reachable from $r$ in the dependency graph:

$$\mathcal{C}(r) = \{r\} \cup \{v \in \mathcal{V} \mid \exists \text{ path from } r \text{ to } v \text{ in } \mathcal{G}\}$$

TraceProof implements a cycle-safe breadth-first search (BFS) algorithm to compute $\mathcal{C}(r)$, recording visited node identifiers to guarantee termination even in malformed topologies exhibiting cyclic references.

---

## 3. Comparative Verification Methods

For a deletion request targeting root resource $r$:

### A. Baseline Method (Root-Only Deletion)
1. **Scope:** $\mathcal{T}_{\text{Baseline}} = \{r\}$ (receives only the root resource identifier).
2. **Execution:** Simulates deletion on the root resource only: $\text{delete}(r)$.
3. **Observation:** Inspects the post-operation existence of $r$:
   $$\text{reported\_incomplete}_{\text{Baseline}} = \begin{cases} \text{True} & \text{if } \text{exists}(r) = \text{True} \\ \text{False} & \text{if } \text{exists}(r) = \text{False} \end{cases}$$
4. **Blind Spot:** Baseline does not traverse $\mathcal{C}(r) \setminus \{r\}$; any unaddressed or failed child, grandchild, or derived records are completely unobserved.

### B. TraceProof Method (Dependency-Aware Closure Verification)
1. **Scope:** $\mathcal{T}_{\text{TraceProof}} = \mathcal{C}(r)$ (the entire registered transitive closure).
2. **Execution:** Simulates deletion across every node in topological closure: $\forall v \in \mathcal{C}(r), \text{delete}(v)$.
3. **Observation:** Inspects post-operation existence of all nodes in closure:
   $$\text{reported\_incomplete}_{\text{TraceProof}} = \begin{cases} \text{True} & \text{if } \exists v \in \mathcal{C}(r) \text{ such that } \text{exists}(v) = \text{True} \\ \text{False} & \text{if } \forall v \in \mathcal{C}(r), \text{exists}(v) = \text{False} \end{cases}$$
4. **Verification Status:**
   - **Verified:** All $v \in \mathcal{C}(r)$ successfully processed ($\text{exists}(v) = \text{False}$).
   - **Incomplete:** One or more dependent resources remain unaddressed or failed.
   - **Failed:** The execution job itself crashed or exhausted retry limits.

---

## 4. Ground Truth Oracle & Classification Matrix

### Common Outcome Oracle
Both methods are evaluated on identical cloned starting states of graph $\mathcal{G}$ with identical injected failures. The actual ground truth of whether deletion was complete is evaluated against the post-execution state of the entire registered closure $\mathcal{C}(r)$:

$$\text{ground\_truth\_incomplete} = \exists v \in \mathcal{C}(r) \text{ such that } \text{exists}(v) = \text{True}$$

### Classification Confusion Matrix
For each trial, the method's reported outcome is compared with the actual post-operation state:

| Classification | Condition | Description |
|---|---|---|
| **True Positive (TP)** | $\text{ground\_truth} = \text{Incomplete} \land \text{reported} = \text{Incomplete}$ | Correctly detected incomplete deletion. |
| **True Negative (TN)** | $\text{ground\_truth} = \text{Complete} \land \text{reported} = \text{Complete}$ | Correctly identified clean closure deletion. |
| **False Positive (FP)** | $\text{ground\_truth} = \text{Complete} \land \text{reported} = \text{Incomplete}$ | False alarm on a completely deleted closure. |
| **False Negative (FN)** | $\text{ground\_truth} = \text{Incomplete} \land \text{reported} = \text{Complete}$ | **Dangerous miss:** Unaddressed copies remain, but method reported success. |

---

## 5. Formal Evaluation Metrics

All metrics are defined strictly with handling for zero denominators:

1. **Detection Rate (Recall / Sensitivity):**
   $$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}} \quad (\text{if } \text{TP} + \text{FN} > 0 \text{ else null})$$
2. **False Negative Rate (Miss Rate):**
   $$\text{FNR} = \frac{\text{FN}}{\text{TP} + \text{FN}} = 1 - \text{Recall} \quad (\text{if } \text{TP} + \text{FN} > 0 \text{ else null})$$
3. **False Positive Rate (Fall-out):**
   $$\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}} \quad (\text{if } \text{FP} + \text{TN} > 0 \text{ else null})$$
4. **Precision (Positive Predictive Value):**
   $$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} \quad (\text{if } \text{TP} + \text{FP} > 0 \text{ else null})$$
5. **F1 Score:**
   $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}} \quad (\text{if } \text{Precision} + \text{Recall} > 0 \text{ else null})$$
6. **Dependency Coverage:**
   $$\text{Coverage} = \frac{|\mathcal{T}_{\text{checked}}|}{|\mathcal{C}(r)|}$$
7. **Simulated Retry Count:** Cumulative retry attempts incurred during failure handling.
8. **Processing Latency (Mean, Median, StdDev, Total):**
   Measured using nanosecond CPU clock (`perf_counter_ns`) strictly around simulated deletion operations. Excludes synthetic graph generation, oracle computation, and network transit.

---

## 6. Statistical Significance & Confidence Intervals

### Wilson Score Interval for Proportions
To account for small trial counts or proportions near 0 or 1, 95% confidence intervals are computed using the Wilson score interval:

$$CI_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1 - \hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

where $z = 1.96$, $\hat{p}$ is the sample proportion, and $n$ is the denominator. Intervals are constrained to $[0, 1]$.

### McNemar's Exact Binomial Test for Paired Discordances
Because Baseline and TraceProof are evaluated on identical paired trial graphs, differences in classification correctness are tested via an exact two-sided McNemar binomial test:

Let:
- $a$: Trials where TraceProof was correct ($\text{TP} \lor \text{TN}$) and Baseline was incorrect ($\text{FP} \lor \text{FN}$).
- $b$: Trials where Baseline was correct and TraceProof was incorrect.

Under $H_0$, $a$ and $b$ follow a binomial distribution with $p = 0.5$ over $n = a + b$:

$$\text{p-value} = 2 \times \sum_{k=0}^{\min(a, b)} \binom{n}{k} 0.5^n$$

---

## 7. Experimental Scenarios

Each experimental run evaluates nine distinct topological and failure configurations:

1. **`no_failures`:** Clean graph execution where all deletions succeed. Tests True Negative accuracy ($\text{FPR} = 0$).
2. **`failed_root`:** Root resource deletion fails. Both methods should observe root failure ($\text{TP}$).
3. **`single_dependent_failure`:** One direct child resource fails. Baseline exhibits False Negative; TraceProof detects incomplete state ($\text{TP}$).
4. **`multiple_dependent_failures`:** Multiple descendants fail across the graph.
5. **`multi_level_chain`:** Deep linear chain ($A \to B \to C \to D$). Tests propagation down deep ancestry.
6. **`resource_without_dependents`:** Isolated leaf node without downstream copies.
7. **`branching_graph`:** High-fanout graph with multiple parallel children.
8. **`dependency_cycle`:** Malformed circular topology ($A \to B \to C \to A$). Validates cycle detection and BFS termination.
9. **`configured_failure_rate`:** Randomized failure injection according to the user-specified probability $p_{\text{fail}} \in [0, 1]$.

---

## 8. Threats to Validity & Limitations

1. **Closure Registration Completeness:** TraceProof's verification oracle is strictly bounded by registered resources. Shadow databases, offline tape backups, and unregistered data lakes cannot be discovered.
2. **Simulation vs. Physical Sanitization:** TraceProof evaluates logical dependency tracking in cloud architectures. It does not measure physical disk overwrite passes or hardware sanitization.
3. **Timing Invariants:** Processing latency measures in-memory Python or Lambda execution overhead. It does not simulate AWS network jitter, throttling, or cold start latency.
4. **Generalizability:** Statistical results are descriptive of the specified graph generation parameters and synthetic seed, and should be reported with configuration context.

