"""Unit tests for GitHub FastAPI endpoints using TestClient."""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from models.github import (
    GitHubAnalyzeResponse,
    GitHubProfile,
    GitHubStatistics,
    GitHubScoreBreakdown
)

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_analyze_github_api_success():
    mock_pipeline_response = GitHubAnalyzeResponse(
        success=True,
        username="octocat",
        profile=GitHubProfile(
            username="octocat",
            name="The Octocat",
            followers=100
        ),
        repositories=[],
        languages={"Python": 1},
        statistics=GitHubStatistics(total_repos=1, non_fork_repos=1),
        score=GitHubScoreBreakdown(
            total_score=80.0,
            repository_quality=24.0,
            activity=20.0,
            documentation=16.0,
            technology_diversity=12.0,
            profile_completeness=8.0
        ),
        suggestions=[]
    )

    with patch("api.github.GitHubPipeline.run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_pipeline_response

        response = client.post("/api/v1/github/analyze", json={"username": "octocat"})
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["username"] == "octocat"
        assert json_data["score"]["total_score"] == 80.0


def test_analyze_github_api_user_not_found():
    with patch("api.github.GitHubPipeline.run", new_callable=AsyncMock) as mock_run:
        from utils.exceptions import GitHubUserNotFoundError
        mock_run.side_effect = GitHubUserNotFoundError("unknown_user")

        response = client.post("/api/v1/github/analyze", json={"username": "unknown_user"})
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()
