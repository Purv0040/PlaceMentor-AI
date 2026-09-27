import pytest
from fastapi.testclient import TestClient


def test_tasks_unauthenticated_access(client: TestClient):
    """Ensure tasks endpoints require authentication."""
    assert client.get("/api/v1/tasks/today").status_code == 401
    assert client.get("/api/v1/tasks").status_code == 401
    assert client.post("/api/v1/tasks").status_code == 401


def test_daily_tasks_crud_and_completion_flow(client: TestClient, auth_headers: dict):
    """Test getting today's tasks, creating a task, completing it, and skipping it."""
    # 1. First generate a roadmap so today's tasks exist
    client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer"},
        headers=auth_headers
    )

    # 2. Get today's tasks
    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res_today.status_code == 200
    data_today = res_today.json()
    assert "tasks" in data_today
    assert data_today["total_tasks"] >= 1
    task_1 = data_today["tasks"][0]
    task_id_1 = task_1["id"]

    # 3. Complete task 1
    res_comp = client.post(f"/api/v1/tasks/{task_id_1}/complete", json={"actual_minutes": 45, "notes": "Done!"}, headers=auth_headers)
    assert res_comp.status_code == 200
    assert res_comp.json()["status"] == "completed"

    # 4. Create custom task
    res_create = client.post(
        "/api/v1/tasks",
        json={
            "title": "Custom Practice Task",
            "description": "Solve 2 Graph DP problems",
            "category": "DSA",
            "skill": "Graphs",
            "priority": "HIGH",
            "estimated_minutes": 60
        },
        headers=auth_headers
    )
    assert res_create.status_code == 201
    custom_task_id = res_create.json()["id"]

    # 5. Skip custom task
    res_skip = client.post(f"/api/v1/tasks/{custom_task_id}/skip", json={"reason": "Need more background review"}, headers=auth_headers)
    assert res_skip.status_code == 200
    assert res_skip.json()["status"] == "skipped"

    # 6. List all tasks
    res_list = client.get("/api/v1/tasks", headers=auth_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 2
