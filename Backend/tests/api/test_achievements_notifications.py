import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def test_achievements_unauthenticated(client: TestClient):
    """Test unauthenticated access to achievement endpoints."""
    assert client.get("/api/v1/achievements").status_code == 401
    assert client.get("/api/v1/achievements/unlocked").status_code == 401
    assert client.get("/api/v1/achievements/progress").status_code == 401
    assert client.post("/api/v1/achievements/check").status_code == 401
    assert client.get("/api/v1/achievements/FIRST_STEP").status_code == 401


def test_notifications_unauthenticated(client: TestClient):
    """Test unauthenticated access to notification endpoints."""
    assert client.get("/api/v1/notifications").status_code == 401
    assert client.get("/api/v1/notifications/unread").status_code == 401
    assert client.get("/api/v1/notifications/count").status_code == 401
    assert client.patch("/api/v1/notifications/notif_123/read").status_code == 401
    assert client.post("/api/v1/notifications/read-all").status_code == 401
    assert client.delete("/api/v1/notifications/notif_123").status_code == 401
    assert client.get("/api/v1/notifications/preferences").status_code == 401


def test_get_achievements_and_progress_flow(client: TestClient, auth_headers: dict):
    """Test fetching all achievements list, unlocked achievements, and progress stats."""
    # 1. Fetch achievements list
    res = client.get("/api/v1/achievements", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert "achievements" in body
    assert "stats" in body
    assert isinstance(body["achievements"], list)
    assert body["stats"]["totalCount"] >= 10

    # 2. Fetch progress endpoint directly
    res_prog = client.get("/api/v1/achievements/progress", headers=auth_headers)
    assert res_prog.status_code == 200
    prog_stats = res_prog.json()
    assert "earnedXp" in prog_stats
    assert "level" in prog_stats

    # 3. Fetch single achievement by code
    res_single = client.get("/api/v1/achievements/FIRST_STEP", headers=auth_headers)
    assert res_single.status_code == 200
    single_item = res_single.json()
    assert single_item["code"] == "FIRST_STEP"


def test_achievement_check_trigger(client: TestClient, auth_headers: dict):
    """Test POST /api/v1/achievements/check endpoint."""
    res_check = client.post("/api/v1/achievements/check", headers=auth_headers)
    assert res_check.status_code == 200
    check_body = res_check.json()
    assert "newly_unlocked" in check_body
    assert "total_unlocked" in check_body
    assert isinstance(check_body["newly_unlocked"], list)


def test_notifications_crud_and_read_flow(client: TestClient, auth_headers: dict, mock_db):
    """Test notification retrieval, unread count, marking as read, and deletion."""
    user_id = "test_user_123"
    # Seed 2 notifications for test user
    mock_db["notifications"].docs["notif_1"] = {
        "_id": "notif_1",
        "notification_id": "notif_1",
        "user_id": user_id,
        "type": "task",
        "title": "Today's Task Reminder",
        "message": "You have 2 pending tasks scheduled today.",
        "priority": "normal",
        "read": False,
        "action_route": "/tasks",
    }
    mock_db["notifications"].docs["notif_2"] = {
        "_id": "notif_2",
        "notification_id": "notif_2",
        "user_id": user_id,
        "type": "achievement",
        "title": "Achievement Unlocked",
        "message": "You unlocked the Onboarding Pioneer badge!",
        "priority": "normal",
        "read": False,
        "action_route": "/achievements",
    }

    # 1. Fetch unread count
    res_cnt = client.get("/api/v1/notifications/count", headers=auth_headers)
    assert res_cnt.status_code == 200
    assert res_cnt.json()["unread_count"] == 2

    # 2. Fetch notifications list
    res_list = client.get("/api/v1/notifications", headers=auth_headers)
    assert res_list.status_code == 200
    notifs = res_list.json()
    assert len(notifs) == 2

    # 3. Mark single notification as read
    res_read = client.patch("/api/v1/notifications/notif_1/read", headers=auth_headers)
    assert res_read.status_code == 200
    assert res_read.json()["status"] == "success"

    # Verify count decremented
    res_cnt_2 = client.get("/api/v1/notifications/count", headers=auth_headers)
    assert res_cnt_2.json()["unread_count"] == 1

    # 4. Mark all as read
    res_read_all = client.post("/api/v1/notifications/read-all", headers=auth_headers)
    assert res_read_all.status_code == 200

    res_cnt_3 = client.get("/api/v1/notifications/count", headers=auth_headers)
    assert res_cnt_3.json()["unread_count"] == 0

    # 5. Delete notification
    res_del = client.delete("/api/v1/notifications/notif_1", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"


def test_notification_preferences_flow(client: TestClient, auth_headers: dict):
    """Test getting and updating user notification settings."""
    # 1. Get default preferences
    res_pref = client.get("/api/v1/notifications/preferences", headers=auth_headers)
    assert res_pref.status_code == 200
    prefs = res_pref.json()
    assert prefs["task_reminders"] is True

    # 2. Update preferences
    res_upd = client.put(
        "/api/v1/notifications/preferences",
        json={
            "task_reminders": False,
            "achievement_notifications": True,
            "roadmap_notifications": True,
            "interview_notifications": True,
            "general_notifications": True,
        },
        headers=auth_headers,
    )
    assert res_upd.status_code == 200
    assert res_upd.json()["task_reminders"] is False


def test_cross_user_notification_isolation(client: TestClient, auth_headers: dict, mock_db):
    """Test that users cannot access or modify another student's notifications."""
    # Seed user 2 and notification for user 2
    mock_db["users"].docs["other_user_notif_999"] = {
        "_id": "other_user_notif_999",
        "email": "other_notif@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "Other Student",
        "is_active": True,
    }
    mock_db["notifications"].docs["private_notif_999"] = {
        "_id": "private_notif_999",
        "notification_id": "private_notif_999",
        "user_id": "other_user_notif_999",
        "type": "achievement",
        "title": "Private Badge",
        "message": "Secret message",
        "read": False,
    }

    # Header for User 1
    # User 1 attempts to mark User 2's notification as read
    assert client.patch("/api/v1/notifications/private_notif_999/read", headers=auth_headers).status_code == 404

    # User 1 attempts to delete User 2's notification
    assert client.delete("/api/v1/notifications/private_notif_999", headers=auth_headers).status_code == 404
