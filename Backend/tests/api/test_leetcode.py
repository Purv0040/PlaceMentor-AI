import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


def test_leetcode_unauthenticated_access(client: TestClient):
    res = client.get("/api/v1/leetcode")
    assert res.status_code == 401

    res = client.post("/api/v1/leetcode/connect", json={"username": "digisha_prep"})
    assert res.status_code == 401


def test_leetcode_connect_and_sync_flow(client: TestClient, auth_headers: dict):
    mock_profile = {
        "username": "digisha_prep",
        "real_name": "Digisha",
        "about": "DSA practice",
        "ranking": 12000,
        "reputation": 450,
        "avatar_url": "https://assets.leetcode.com/users/avatar.jpg"
    }

    mock_solved = {
        "total_solved": 342,
        "easy_solved": 140,
        "medium_solved": 165,
        "hard_solved": 37,
        "total_questions": 3000,
        "easy_total": 800,
        "medium_total": 1500,
        "hard_total": 700,
        "acceptance_rate": 62.5
    }

    mock_topics = [
        {"tagName": "Array", "slug": "array", "problemsSolved": 75, "tier": "fundamental"},
        {"tagName": "Dynamic Programming", "slug": "dynamic-programming", "problemsSolved": 32, "tier": "advanced"}
    ]

    mock_contest = {
        "rating": 1842.5,
        "global_ranking": 15000,
        "attended_contests": 12,
        "top_percentage": 4.8
    }

    mock_recent = [
        {"title": "Course Schedule II", "timestamp": "1690000000"}
    ]

    with patch("app.integrations.leetcode_client.LeetCodeAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.return_value = mock_profile

        res_connect = client.post("/api/v1/leetcode/connect", json={"username": "digisha_prep"}, headers=auth_headers)
        assert res_connect.status_code == 200
        body_connect = res_connect.json()
        assert body_connect["success"] is True
        assert body_connect["data"]["leetcode_username"] == "digisha_prep"

    res_get = client.get("/api/v1/leetcode", headers=auth_headers)
    assert res_get.status_code == 200
    body_get = res_get.json()
    assert body_get["data"]["leetcode_username"] == "digisha_prep"

    with patch("app.integrations.leetcode_client.LeetCodeAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile, \
         patch("app.integrations.leetcode_client.LeetCodeAPIClient.get_solved_problems", new_callable=AsyncMock) as mock_get_solved, \
         patch("app.integrations.leetcode_client.LeetCodeAPIClient.get_topic_tags", new_callable=AsyncMock) as mock_get_topics, \
         patch("app.integrations.leetcode_client.LeetCodeAPIClient.get_contest_info", new_callable=AsyncMock) as mock_get_contest, \
         patch("app.integrations.leetcode_client.LeetCodeAPIClient.get_recent_submissions", new_callable=AsyncMock) as mock_get_recent:
        
        mock_get_profile.return_value = mock_profile
        mock_get_solved.return_value = mock_solved
        mock_get_topics.return_value = mock_topics
        mock_get_contest.return_value = mock_contest
        mock_get_recent.return_value = mock_recent

        res_sync = client.post("/api/v1/leetcode/sync", headers=auth_headers)
        assert res_sync.status_code == 200
        body_sync = res_sync.json()
        assert body_sync["success"] is True
        assert body_sync["data"]["statistics"]["total_solved"] == 342
        assert body_sync["data"]["contest"]["rating"] == 1842.5

    res_stats = client.get("/api/v1/leetcode/statistics", headers=auth_headers)
    assert res_stats.status_code == 200
    assert res_stats.json()["data"]["statistics"]["total_solved"] == 342

    res_act = client.get("/api/v1/leetcode/activity", headers=auth_headers)
    assert res_act.status_code == 200
    assert len(res_act.json()["data"]["recent_activity"]) == 1

    mock_ai_output = {
        "profile": {"username": "digisha_prep", "ranking": 12000},
        "problem_statistics": mock_solved,
        "difficulty_distribution": {"easy_pct": 40.9, "medium_pct": 48.2, "hard_pct": 10.9},
        "topic_analysis": [{"topic": "Dynamic Programming", "solved_count": 32, "performance_level": "developing", "evidence": ["32 DP solved"], "confidence": "high"}],
        "strong_topics": ["Array", "Trees"],
        "weak_topics": ["Dynamic Programming"],
        "contest": mock_contest,
        "recent_activity": mock_recent,
        "recommendations": ["Solve 28 additional Medium DP problems."],
        "data_source_status": {"provider": "LeetCodeGraphQLProvider", "profile_available": True, "problems_available": True}
    }

    with patch("app.integrations.ai_client.AIClient.analyze_leetcode", new_callable=AsyncMock) as mock_ai_analyze:
        mock_ai_analyze.return_value = mock_ai_output

        res_analyze = client.post("/api/v1/leetcode/analyze", headers=auth_headers)
        assert res_analyze.status_code == 200
        body_analyze = res_analyze.json()
        assert body_analyze["success"] is True
        assert body_analyze["data"]["analysis"]["profile"]["username"] == "digisha_prep"

    res_fetch = client.get("/api/v1/leetcode/analysis", headers=auth_headers)
    assert res_fetch.status_code == 200
    assert res_fetch.json()["data"]["analysis"]["profile"]["username"] == "digisha_prep"

    # Test Daily Practice Plan
    res_plan = client.get("/api/v1/leetcode/daily-plan", headers=auth_headers)
    assert res_plan.status_code == 200
    plan_data = res_plan.json()["data"]
    assert "tasks" in plan_data
    assert len(plan_data["tasks"]) >= 3
    assert plan_data["completed_count"] == 0
    first_task_id = plan_data["tasks"][0]["task_id"]

    # Test toggling a daily practice task
    res_toggle = client.post(f"/api/v1/leetcode/daily-plan/{first_task_id}/toggle", headers=auth_headers)
    assert res_toggle.status_code == 200
    toggled_data = res_toggle.json()["data"]
    assert toggled_data["completed_count"] == 1
    assert toggled_data["tasks"][0]["status"] == "completed"

    # Test Activity History (7d, 30d, 90d)
    for period in [7, 30, 90]:
        res_hist = client.get(f"/api/v1/leetcode/history?days={period}", headers=auth_headers)
        assert res_hist.status_code == 200
        hist_data = res_hist.json()["data"]
        assert hist_data["days"] == period
        assert len(hist_data["data_points"]) == period
        assert hist_data["has_contest_history"] is True

    # Test Focus Areas (14 DSA topics)
    res_focus = client.get("/api/v1/leetcode/focus-areas", headers=auth_headers)
    assert res_focus.status_code == 200
    focus_data = res_focus.json()["data"]
    assert len(focus_data) == 14
    for topic_item in focus_data:
        assert 0 <= topic_item["mastery_percentage"] <= 100
        assert topic_item["priority"] in ["High", "Medium", "Low"]
        assert len(topic_item["suggested_problems"]) > 0

    # Test Readiness Breakdown
    res_ready = client.get("/api/v1/leetcode/readiness-breakdown", headers=auth_headers)
    assert res_ready.status_code == 200
    ready_data = res_ready.json()["data"]
    assert 25 <= ready_data["readiness_score"] <= 98
    assert "disclaimer" in ready_data
    assert ready_data["easy_pts"] > 0
    assert ready_data["medium_pts"] > 0

    res_del = client.delete("/api/v1/leetcode", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["disconnected"] is True

    res_after = client.get("/api/v1/leetcode", headers=auth_headers)
    assert res_after.status_code == 404

