import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.core.security import create_access_token


def test_communication_unauthenticated(client: TestClient):
    """Ensure communication endpoints require authentication."""
    assert client.post("/api/v1/communication/analyze", json={}).status_code == 401
    assert client.get("/api/v1/communication/history").status_code == 401
    assert client.get("/api/v1/communication/summary").status_code == 401
    assert client.get("/api/v1/communication/507f1f77bcf86cd799439011").status_code == 401


def test_communication_analysis_and_history_flow(client: TestClient, auth_headers: dict):
    """Test analyzing answer, retrieving summary, history, and single analysis."""
    # 1. Analyze sample answer
    request_data = {
        "question": "Tell me about a technical challenge you faced.",
        "answer": "Well, um, basically we had a memory leak in our Python microservice. I used tracemalloc to pinpoint unclosed database connections, fixed the pool limit, and reduced memory usage by 40%."
    }
    res = client.post("/api/v1/communication/analyze", json=request_data, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert "id" in data
    analysis_id = data["id"]
    assert "clarity" in data
    assert "structure" in data
    assert "conciseness" in data
    assert "technical_explanation" in data
    assert "overall_score" in data
    assert "strengths" in data
    assert "improved_answer_structure" in data

    # 2. Get communication summary
    sum_res = client.get("/api/v1/communication/summary", headers=auth_headers)
    assert sum_res.status_code == 200
    sum_data = sum_res.json()
    assert "total_analyses" in sum_data
    assert sum_data["total_analyses"] >= 1
    assert "average_overall_score" in sum_data

    # 3. Get communication history
    hist_res = client.get("/api/v1/communication/history", headers=auth_headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["id"] == analysis_id

    # 4. Get specific analysis by ID
    single_res = client.get(f"/api/v1/communication/{analysis_id}", headers=auth_headers)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == analysis_id


def test_communication_ownership_security(client: TestClient, auth_headers: dict, mock_db):
    """Test that users cannot access another student's communication analysis."""
    # Seed user 2 in mock DB
    mock_db["users"].docs["user_xyz_777"] = {
        "_id": "user_xyz_777",
        "email": "xyz@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "XYZ Student",
        "is_active": True,
    }

    request_data = {
        "question": "Explain quicksort algorithm.",
        "answer": "Quicksort is a divide and conquer algorithm that picks a pivot element..."
    }
    res = client.post("/api/v1/communication/analyze", json=request_data, headers=auth_headers)
    analysis_id = res.json()["id"]

    # Other user header
    other_token = create_access_token(subject="user_xyz_777", extra_claims={"email": "xyz@example.com"})
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Other user tries to access analysis
    assert client.get(f"/api/v1/communication/{analysis_id}", headers=other_headers).status_code == 404


def test_invalid_analysis_id(client: TestClient, auth_headers: dict):
    """Test response for non-existent analysis ID."""
    bad_id = "507f1f77bcf86cd799439099"
    assert client.get(f"/api/v1/communication/{bad_id}", headers=auth_headers).status_code == 404


from app.integrations.ai_client import AIClientError
from unittest.mock import patch, AsyncMock


def test_communication_ai_fallback(client: TestClient, auth_headers: dict):
    """Test fallback articulation analysis when AI service raises an error."""
    with patch("app.integrations.ai_client.AIClient.analyze_communication", new_callable=AsyncMock, side_effect=AIClientError("AI Service Error")):
        request_data = {
            "question": "What is dependency injection?",
            "answer": "Dependency injection is a software design pattern where objects receive their dependencies from external sources rather than constructing them internally."
        }
        res = client.post("/api/v1/communication/analyze", json=request_data, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["overall_score"] >= 50
