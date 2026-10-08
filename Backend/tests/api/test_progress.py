import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.utils.dates import get_today_date_str, APP_TIMEZONE


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


def test_daily_completion_current_window_calculation(client: TestClient, auth_headers: dict):
    """Verify daily_completion calculates dynamic current progress window starting near today/start date, not end of 90-day roadmap."""
    # 1. Generate a 90-day roadmap
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "Full Stack Engineer"}, headers=auth_headers)
    assert res_gen.status_code == 200
    active_rm = res_gen.json()
    roadmap_id = active_rm.get("roadmap_id") or active_rm.get("id")

    # 2. Fetch progress
    res_prog = client.get("/api/v1/progress", headers=auth_headers)
    assert res_prog.status_code == 200
    p_data = res_prog.json()

    assert p_data["roadmap_id"] == roadmap_id
    assert p_data["total_tasks"] == p_data["completed_tasks"] + p_data["pending_tasks"] + p_data["skipped_tasks"]
    assert len(p_data["daily_completion"]) <= 14

    today_str = get_today_date_str()
    daily_dates = [item["date"] for item in p_data["daily_completion"]]

    # Verify daily_completion begins around today/start of roadmap and includes today
    assert today_str in daily_dates
    # Ensure the first date is NOT the tail end of a 90-day roadmap (which would be ~76+ days in the future)
    first_date = datetime.strptime(daily_dates[0], "%Y-%m-%d").date()
    today_date = datetime.now(APP_TIMEZONE).date()
    assert abs((first_date - today_date).days) <= 7

    # 3. Complete a task for today
    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res_today.status_code == 200
    tasks = res_today.json()["tasks"]
    assert len(tasks) > 0
    first_task = tasks[0]

    res_comp = client.post(f"/api/v1/tasks/{first_task['id']}/complete", json={"actual_minutes": 45}, headers=auth_headers)
    assert res_comp.status_code == 200

    # 4. Fetch progress again
    res_prog2 = client.get("/api/v1/progress", headers=auth_headers)
    assert res_prog2.status_code == 200
    p_data2 = res_prog2.json()

    assert p_data2["completed_tasks"] == p_data["completed_tasks"] + 1
    assert p_data2["pending_tasks"] == p_data["pending_tasks"] - 1
    
    # Check that today's daily_completion entry has incremented completed count
    today_entry_1 = next((item for item in p_data["daily_completion"] if item["date"] == today_str), None)
    today_entry_2 = next((item for item in p_data2["daily_completion"] if item["date"] == today_str), None)
    assert today_entry_1 is not None
    assert today_entry_2 is not None
    assert today_entry_2["completed"] == today_entry_1["completed"] + 1


def test_weekly_completion_endpoint_calculation(client: TestClient, auth_headers: dict):
    """Verify GET /api/v1/progress/weekly returns dynamic 7-day week breakdown matching GET /api/v1/progress."""
    # 1. Generate roadmap
    res_gen = client.post("/api/v1/roadmap/generate", json={"target_role": "AI Engineer"}, headers=auth_headers)
    assert res_gen.status_code == 200

    # 2. Call GET /api/v1/progress/weekly
    res_weekly = client.get("/api/v1/progress/weekly", headers=auth_headers)
    assert res_weekly.status_code == 200
    weeks = res_weekly.json()

    assert isinstance(weeks, list)
    assert len(weeks) > 0  # Should not be empty

    # Verify structure of each week
    for w in weeks:
        assert "week" in w
        assert "start_date" in w
        assert "end_date" in w
        assert "total" in w
        assert "completed" in w
        assert "percentage" in w

    # Week 1 should be week 1
    assert weeks[0]["week"] == 1
    if len(weeks) > 1:
        assert weeks[1]["week"] == 2
        # Week 2 start_date should be 7 days after Week 1 start_date
        w1_start = datetime.strptime(weeks[0]["start_date"], "%Y-%m-%d").date()
        w2_start = datetime.strptime(weeks[1]["start_date"], "%Y-%m-%d").date()
        assert (w2_start - w1_start).days == 7

    # 3. Verify total weekly tasks matches GET /api/v1/progress total_tasks
    res_prog = client.get("/api/v1/progress", headers=auth_headers)
    assert res_prog.status_code == 200
    p_data = res_prog.json()

    weekly_sum = sum(w["total"] for w in weeks)
    assert weekly_sum == p_data["total_tasks"]

    # 4. Verify weekly_completion in GET /api/v1/progress matches GET /api/v1/progress/weekly
    assert p_data["weekly_completion"] == weeks

    # 5. Complete a task and verify week updates dynamically
    res_today = client.get("/api/v1/tasks/today", headers=auth_headers)
    assert res_today.status_code == 200
    tasks = res_today.json()["tasks"]
    if tasks:
        first_task = tasks[0]
        client.post(f"/api/v1/tasks/{first_task['id']}/complete", json={"actual_minutes": 30}, headers=auth_headers)

        res_weekly2 = client.get("/api/v1/progress/weekly", headers=auth_headers)
        assert res_weekly2.status_code == 200
        weeks2 = res_weekly2.json()
        assert weeks2[0]["completed"] >= 1

