import pytest
from fastapi.testclient import TestClient


def test_progress_unauthenticated_access(client: TestClient):
    """Ensure progress endpoints require authentication."""
    assert client.get("/api/v1/progress").status_code == 401
    assert client.get("/api/v1/progress/summary").status_code == 401
    assert client.get("/api/v1/progress/streak").status_code == 401


def test_progress_and_streak_calculation_flow(client: TestClient, auth_headers: dict):
    """Test getting progress, completing a task, verifying streak & percentage updates."""
    # 1. Generate roadmap & tasks
    client.post("/api/v1/roadmap/generate", json={"target_role": "Backend Developer"}, headers=auth_headers)

    # 2. Check progress before completing
    res_p1 = client.get("/api/v1/progress", headers=auth_headers)
    assert res_p1.status_code == 200
    p1_data = res_p1.json()
    assert "user_id" in p1_data

    # 3. Get today tasks & complete one
    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    task_id = res_today.json()["tasks"][0]["id"]

    client.post(f"/api/v1/tasks/{task_id}/complete", json={"actual_minutes": 50}, headers=auth_headers)

    # 4. Check progress after completing
    res_p2 = client.get("/api/v1/progress", headers=auth_headers)
    assert res_p2.status_code == 200
    p2_data = res_p2.json()
    assert p2_data["completed_tasks"] >= 1
    assert p2_data["current_streak"] >= 1

    # 5. Check streak endpoint
    res_streak = client.get("/api/v1/progress/streak", headers=auth_headers)
    assert res_streak.status_code == 200
    s_data = res_streak.json()
    assert s_data["current_streak"] >= 1
    assert s_data["is_active_today"] is True
