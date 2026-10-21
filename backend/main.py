
from copy import deepcopy
from uuid import uuid4
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from deletion_engine import (
    SAMPLE_RESOURCES,
    get_dependency_targets,
    run_baseline,
    run_traceproof,
)

app = FastAPI(
    title="TraceProof API",
    description="Dependency-aware deletion verification demo",
    version="0.1.0",
)

# Local development only. Restrict this to the deployed frontend
# origin before publishing the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

resources = deepcopy(SAMPLE_RESOURCES)
requests = {}


class DeletionRequest(BaseModel):
    resource_id: str = Field(min_length=1)
    simulate_failure: bool = False


@app.get("/")
def health_check():
    return {
        "name": "TraceProof API",
        "status": "running",
        "mode": "simulation",
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

    # Work on a copy so requests do not change the sample registry.
    state = deepcopy(resources)

    if body.simulate_failure:
        targets = get_dependency_targets(state, body.resource_id)
        if len(targets) > 1:
            state[targets[-1]]["fail_delete"] = True

    result = run_traceproof(state, body.resource_id)

    record = {
        "request_id": request_id,
        "resource_id": body.resource_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "simulation_only": True,
        **result,
    }

    requests[request_id] = record
    return record


@app.get("/deletion-requests")
def list_deletion_requests():
    return list(requests.values())


@app.get("/deletion-requests/{request_id}")
def get_deletion_request(request_id: str):
    record = requests.get(request_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Deletion request not found",
        )

    return record


@app.get("/experiments/compare")
def compare_schedulers():
    baseline = run_baseline(resources, "student_001")
    traceproof = run_traceproof(resources, "student_001")

    return {
        "simulation_only": True,
        "baseline": baseline,
        "traceproof": traceproof,
    }
