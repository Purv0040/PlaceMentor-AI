import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def test_interview_unauthenticated(client: TestClient):
    """Test unauthenticated access to interview endpoints."""
    assert client.post("/api/v1/interviews", json={}).status_code == 401
    assert client.get("/api/v1/interviews/history").status_code == 401
    assert client.get("/api/v1/interviews/507f1f77bcf86cd799439011").status_code == 401


def test_create_and_flow_interview(client: TestClient, auth_headers: dict):
    """Test starting interview, getting current question, submitting answer, and completing session."""
    # 1. Start interview
    create_res = client.post(
        "/api/v1/interviews",
        json={"interview_type": "technical", "difficulty": "medium", "question_count": 3},
        headers=auth_headers
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert "id" in data
    interview_id = data["id"]
    assert data["interview_type"] == "technical"
    assert data["status"] == "active"
    assert data["current_question"] is not None

    # 2. Get current question
    curr_res = client.get(f"/api/v1/interviews/{interview_id}/current", headers=auth_headers)
    assert curr_res.status_code == 200
    q_data = curr_res.json()
    assert "question" in q_data
    assert q_data["question"]["question_number"] == 1

    # 3. Submit answer to question 1
    ans_res = client.post(
        f"/api/v1/interviews/{interview_id}/answer",
        json={"answer": "I would design a REST API with clear resource paths, proper HTTP verbs, and authentication using JWT."},
        headers=auth_headers
    )
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert "completed_question" in ans_data
    assert ans_data["completed_question"]["interview_id"] == interview_id
    assert "evaluation" in ans_data
    assert ans_data["evaluation"]["score"] >= 0

    # 4. Get session questions
    q_list_res = client.get(f"/api/v1/interviews/{interview_id}/questions", headers=auth_headers)
    assert q_list_res.status_code == 200
    questions = q_list_res.json()
    assert len(questions) >= 1

    # 5. Complete interview
    comp_res = client.post(f"/api/v1/interviews/{interview_id}/complete", headers=auth_headers)
    assert comp_res.status_code == 200
    result = comp_res.json()
    assert result["interview_id"] == interview_id
    assert "overall_score" in result
    assert "category_scores" in result

    # 6. Check history
    hist_res = client.get("/api/v1/interviews/history", headers=auth_headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["id"] == interview_id


def test_interview_ownership_security(client: TestClient, auth_headers: dict, mock_db):
    """Test that users cannot access or submit answers to another user's interview."""
    # Seed user 2 in mock DB
    mock_db["users"].docs["other_user_999"] = {
        "_id": "other_user_999",
        "email": "other@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "Other Student",
        "is_active": True,
    }

    # Create interview as user 1
    create_res = client.post(
        "/api/v1/interviews",
        json={"interview_type": "behavioral", "difficulty": "easy"},
        headers=auth_headers
    )
    interview_id = create_res.json()["id"]

    # Header for User 2
    user2_token = create_access_token(subject="other_user_999", extra_claims={"email": "other@example.com"})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 tries to view User 1's interview
    get_res = client.get(f"/api/v1/interviews/{interview_id}", headers=user2_headers)
    assert get_res.status_code == 404

    # User 2 tries to submit answer to User 1's interview
    ans_res = client.post(
        f"/api/v1/interviews/{interview_id}/answer",
        json={"answer": "Unpermitted answer"},
        headers=user2_headers
    )
    assert ans_res.status_code == 404


def test_invalid_interview_ids(client: TestClient, auth_headers: dict):
    """Test handling of non-existent or malformed interview IDs."""
    bad_id = "507f1f77bcf86cd799439099"
    assert client.get(f"/api/v1/interviews/{bad_id}", headers=auth_headers).status_code == 404
    assert client.get(f"/api/v1/interviews/{bad_id}/current", headers=auth_headers).status_code == 404
    assert client.post(f"/api/v1/interviews/{bad_id}/complete", headers=auth_headers).status_code == 404


from app.integrations.ai_client import AIClientError
from unittest.mock import patch, AsyncMock


def test_ai_failure_fallback_evaluation(client: TestClient, auth_headers: dict):
    """Test that if AI service fails, fallback question/evaluation safe handling occurs."""
    with patch("app.integrations.ai_client.AIClient.evaluate_interview_answer", new_callable=AsyncMock, side_effect=AIClientError("AI Service Unavailable")):
        create_res = client.post(
            "/api/v1/interviews",
            json={"interview_type": "technical"},
            headers=auth_headers
        )
        interview_id = create_res.json()["id"]

        ans_res = client.post(
            f"/api/v1/interviews/{interview_id}/answer",
            json={"answer": "This is a detailed technical response explaining my process."},
            headers=auth_headers
        )
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        assert ans_data["evaluation"]["score"] >= 50
