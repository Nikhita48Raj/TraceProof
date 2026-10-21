
from copy import deepcopy


SAMPLE_RESOURCES = {
    "student_001": {
        "name": "Student Record",
        "type": "DynamoDB",
        "depends_on": [],
        "exists": True,
        "fail_delete": False,
    },
    "report_001": {
        "name": "Student Report",
        "type": "S3",
        "depends_on": ["student_001"],
        "exists": True,
        "fail_delete": False,
    },
    "derived_001": {
        "name": "Derived Analytics Record",
        "type": "DynamoDB",
        "depends_on": ["student_001"],
        "exists": True,
        "fail_delete": True,
    },
}


def get_dependency_targets(resources, root_id):
    """Find the root and every registered dependent resource."""
    if root_id not in resources:
        raise ValueError(f"Unknown resource: {root_id}")

    targets = []
    visited = set()
    pending = [root_id]

    while pending:
        current_id = pending.pop(0)

        if current_id in visited:
            continue

        visited.add(current_id)
        targets.append(current_id)

        for resource_id, resource in resources.items():
            if current_id in resource["depends_on"]:
                pending.append(resource_id)

    return targets


def delete_resource(resources, resource_id):
    """Simulate deletion of a single resource."""
    resource = resources[resource_id]

    if resource["fail_delete"]:
        return False

    resource["exists"] = False
    return True


def run_baseline(resources, root_id):
    """Baseline deletes only the primary record."""
    state = deepcopy(resources)
    success = delete_resource(state, root_id)

    return {
        "approach": "Baseline",
        "status": "Success" if success else "Failed",
        "targets_checked": 1,
        "remaining_targets": [
            key for key, value in state.items()
            if value["exists"]
        ],
    }


def run_traceproof(resources, root_id):
    """Delete and verify every registered dependency."""
    state = deepcopy(resources)
    targets = get_dependency_targets(state, root_id)
    task_results = {}

    for resource_id in targets:
        task_results[resource_id] = delete_resource(
            state, resource_id
        )

    remaining = [
        resource_id for resource_id in targets
        if state[resource_id]["exists"]
    ]

    return {
        "approach": "TraceProof",
        "status": "Verified" if not remaining else "Incomplete",
        "targets_checked": len(targets),
        "task_results": task_results,
        "remaining_targets": remaining,
    }
