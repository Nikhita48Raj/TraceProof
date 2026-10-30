from copy import deepcopy
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator

from deletion_engine import (
    SAMPLE_RESOURCES,
    get_dependency_targets,
    run_baseline,
    run_traceproof,
)
from experiment_engine import aggregates_csv, research_report, run_reproducible_experiment, trials_csv

app = FastAPI(
    title="TraceProof API",
    description="Dependency-aware deletion verification research system",
    version="0.1.0",
)

# Local development origin. Configured for local Vite dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

resources = deepcopy(SAMPLE_RESOURCES)
requests = {}
reports = {}
experiment_results = {}


class DeletionRequest(BaseModel):
    resource_id: str = Field(min_length=1, max_length=200)
    simulate_failure: bool = False


class ExperimentConfig(BaseModel):
    num_resources: int = Field(default=12, ge=4, le=100)
    dependency_density: float = Field(default=0.15, ge=0, le=1)
    failure_rate: float = Field(default=0.2, ge=0, le=1)
    trials: int = Field(default=5, ge=1, le=100)
    random_seed: int = Field(default=42, ge=0, le=2147483647)
    dependency_depth: int = Field(default=1, ge=1, le=99)

    @model_validator(mode="after")
    def validate_experiment_size(self):
        if self.dependency_depth >= self.num_resources:
            raise ValueError("dependency_depth must be less than num_resources")
        if self.num_resources * self.trials * 9 > 40000:
            raise ValueError("Experiment is too large; reduce resources or trials")
        return self


@app.get("/")
def root_info():
    return {
        "name": "TraceProof API",
        "status": "running",
        "mode": "simulation",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TraceProof API",
        "mode": "local-simulation",
        "registered_resources": len(resources),
        "active_requests": len(requests),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/resources")
def list_resources():
    return [
        {
            "id": resource_id,
            "name": resource["name"],
            "type": resource["type"],
            "exists": resource["exists"],
            "depends_on": resource["depends_on"],
        }
        for resource_id, resource in resources.items()
    ]


@app.get("/resources/{resource_id}/dependencies")
def resource_dependencies(resource_id: str):
    try:
        targets = get_dependency_targets(resources, resource_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "root_resource": resource_id,
        "targets": [
            {
                "id": target,
                "name": resources[target]["name"],
                "type": resources[target]["type"],
            }
            for target in targets
        ],
    }


@app.post("/deletion-requests")
def create_deletion_request(body: DeletionRequest):
    if body.resource_id not in resources:
        raise HTTPException(
            status_code=404,
            detail="Resource not found",
        )

    request_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    # Work on a copy so requests do not mutate the persistent sample registry.
    state = deepcopy(resources)

    if body.simulate_failure:
        targets = get_dependency_targets(state, body.resource_id)
        if len(targets) > 1:
            state[targets[-1]]["fail_delete"] = True
        else:
            state[targets[0]]["fail_delete"] = True

    result = run_traceproof(state, body.resource_id)

    report_key = f"reports/{request_id}.json"
    record = {
        "request_id": request_id,
        "resource_id": body.resource_id,
        "created_at": created_at,
        "updated_at": created_at,
        "report_key": report_key,
        "report_created_at": created_at,
        "simulation_only": True,
        **result,
    }

    report = {
        "schema_version": 1,
        "request_id": request_id,
        "resource_id": body.resource_id,
        "request_created_at": created_at,
        "simulation_only": True,
        "scope": "Registered synthetic dependency closure",
        **result,
    }

    requests[request_id] = record
    reports[request_id] = report
    return record


@app.get("/deletion-requests")
def list_deletion_requests():
    records = list(requests.values())
    records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return records


@app.get("/deletion-requests/{request_id}")
def get_deletion_request(request_id: str):
    record = requests.get(request_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Deletion request not found",
        )

    return record


@app.get("/deletion-requests/{request_id}/report")
def get_deletion_report(request_id: str):
    report = reports.get(request_id)
    if report is not None:
        return report

    req = requests.get(request_id)
    if req is None:
        raise HTTPException(
            status_code=404,
            detail="Verification report not found",
        )

    report = {
        "schema_version": 1,
        "request_id": request_id,
        "resource_id": req.get("resource_id"),
        "request_created_at": req.get("created_at"),
        "simulation_only": True,
        "scope": "Registered synthetic dependency closure",
        "approach": req.get("approach", "TraceProof"),
        "status": req.get("status"),
        "targets_checked": req.get("targets_checked", 0),
        "task_results": req.get("task_results", {}),
        "remaining_targets": req.get("remaining_targets", []),
    }
    reports[request_id] = report
    return report


@app.get("/experiments/compare")
def compare_schedulers():
    baseline = run_baseline(resources, "student_001")
    traceproof = run_traceproof(resources, "student_001")

    return {
        "simulation_only": True,
        "baseline": baseline,
        "traceproof": traceproof,
    }


@app.post("/experiments/run")
def run_experiment(body: ExperimentConfig):
    result = run_reproducible_experiment(body.model_dump())
    experiment_results[result["experiment_id"]] = result
    while len(experiment_results) > 20:
        experiment_results.pop(next(iter(experiment_results)))
    return {key: value for key, value in result.items() if key != "trial_records"}


def _experiment_result(experiment_id):
    result = experiment_results.get(experiment_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Experiment result not found")
    return result


@app.get("/experiments/{experiment_id}/trials.csv")
def export_experiment_trials(experiment_id: str):
    return Response(
        trials_csv(_experiment_result(experiment_id)),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="traceproof-{experiment_id}-trials.csv"'}
    )


@app.get("/experiments/{experiment_id}/aggregates.csv")
def export_experiment_aggregates(experiment_id: str):
    return Response(
        aggregates_csv(_experiment_result(experiment_id)),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="traceproof-{experiment_id}-aggregates.csv"'}
    )


@app.get("/experiments/{experiment_id}/report.md")
def export_experiment_report(experiment_id: str):
    return Response(
        research_report(_experiment_result(experiment_id)),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="traceproof-{experiment_id}-report.md"'}
    )
