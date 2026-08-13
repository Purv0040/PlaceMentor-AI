"""Unit tests for LeetCode FastAPI endpoints using TestClient."""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from models.leetcode import (
    LeetCodeAnalyzeResponse,
    ProblemStatistics,
    ConsistencyData,
    ContestData,
    DSAScoreBreakdown
)

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_analyze_leetcode_api_success():
    mock_pipeline_response = LeetCodeAnalyzeResponse(
        success=True,
        username="tourist",
        problem_statistics=ProblemStatistics(total_solved=300),
        topic_statistics={"Arrays": 50},
        weak_topics=[],
        consistency=ConsistencyData(is_available=True),
        contest_data=ContestData(is_available=True),
        dsa_score=DSAScoreBreakdown(
            total_score=85.0,
            problems_solved_score=20.0,
            difficulty_distribution_score=18.0,
            topic_coverage_score=25.0,
            consistency_score=12.0,
            contest_performance_score=10.0,
            contest_available=True
        ),
        suggestions=[]
    )

    with patch("api.leetcode.LeetCodePipeline.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_pipeline_response

        response = client.post("/api/v1/leetcode/analyze", json={"username": "tourist"})
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["username"] == "tourist"
        assert json_data["dsa_score"]["total_score"] == 85.0


def test_analyze_leetcode_api_user_not_found():
    with patch("api.leetcode.LeetCodePipeline.run", new_callable=AsyncMock) as mock_run:
        from utils.exceptions import LeetCodeUserNotFoundError
        mock_run.side_effect = LeetCodeUserNotFoundError("unknown_leetcode_user")

        response = client.post("/api/v1/leetcode/analyze", json={"username": "unknown_leetcode_user"})
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()
