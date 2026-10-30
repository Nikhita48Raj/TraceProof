# TraceProof

TraceProof is a research prototype for dependency-aware deletion verification. Its local benchmark compares a root-record-only baseline with verification over registered dependents on synthetic data. Results describe this simulation and registered graph only; the project does not measure physical erasure or cover unregistered copies.

## Architecture

- React/Vite dashboard in `frontend/`
- FastAPI local API and simulation engine in `backend/`
- Optional AWS SAM API/queue/worker architecture in `template.yaml` and `backend/aws_handlers/`

The research runner executes locally in memory without AWS credentials. The AWS integration is optional and has not been deployed by the research runner.

## Run locally

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL (normally `http://localhost:5173`) and use **Experiments**. The API defaults to `http://127.0.0.1:8000`; set `VITE_API_BASE_URL` if needed.

To run the backend test suite, install `backend/requirements-dev.txt` (includes PyYAML for CloudFormation template tests), then run `python -m unittest discover -s tests -v` from `backend/`.

## Run and reproduce experiments

Use the dashboard controls or call the API:

```powershell
$body = '{"num_resources":12,"dependency_density":0.15,"failure_rate":0.2,"trials":5,"random_seed":42,"dependency_depth":4}'
$result = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/experiments/run -ContentType 'application/json' -Body $body
$result.experiment_id
```

Use the same configuration and seed to reproduce graph/failure outcomes. Trial timings vary by runtime and host. The API enforces graph/config bounds and a 40,000 resource-trial work cap. Each run stays in process memory; restarting the API clears its exportable run results.

## Export results

After a run, the dashboard provides trial-level CSV, aggregate CSV, and a structured Markdown research report. The API routes are:

- `GET /experiments/{experiment_id}/trials.csv`
- `GET /experiments/{experiment_id}/aggregates.csv`
- `GET /experiments/{experiment_id}/report.md`

Exports contain synthetic resource IDs only and no cloud credentials or account data.

## Experimental design and metrics

Each trial is paired: both methods start from the same pristine graph and injected failures. The baseline attempts and observes only the selected root and does not receive the dependency closure while deciding its outcome. TraceProof attempts and observes all registered reverse dependents, with cycle-safe traversal. Ground truth is incomplete if any resource in the method's resulting state within that registered closure remains.

TP means incomplete and reported incomplete; TN means complete and reported complete; FP means complete and reported incomplete; FN means incomplete and reported complete. Detection = TP/(TP+FN), FNR = FN/(TP+FN), and FPR = FP/(FP+TN). A zero denominator produces null. Wilson 95% intervals are included for proportions. The paired exact McNemar test compares binary correctness; its p-value is descriptive given repeated scenarios and no multiplicity adjustment. Timings cover simulated delete attempts only. The methodology and assumptions are detailed in [METHODOLOGY.md](METHODOLOGY.md).

Scenarios include no failures, failed root deletion, one/multiple dependent failures, a dependency chain, a resource without dependents, a branching graph, cycles, and configured random failures.

## Limitations

The graph contains only registered synthetic resources. Missing dependency registrations, untracked copies, external backups, and storage systems outside the graph are invisible. Synthetic operation timing is not AWS latency. A verified result is not proof of physical erasure, and these experiments do not establish universal novelty or superiority.

AWS deployment instructions are in [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md). AWS observations, if separately run, must be reported separately from local simulation results.
