import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


def test_github_unauthenticated_access(client: TestClient):
    res = client.get("/api/v1/github")
    assert res.status_code == 401

    res = client.post("/api/v1/github/connect", json={"github_username": "Purv0040"})
    assert res.status_code == 401


def test_github_connect_and_sync_flow(client: TestClient, auth_headers: dict):
    mock_profile = {
        "id": 12345,
        "login": "Purv0040",
        "name": "Purv Patel",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345",
        "bio": "Full Stack & AI Engineer",
        "public_repos": 14,
        "followers": 50,
        "following": 20,
        "html_url": "https://github.com/Purv0040"
    }

    mock_repos = [
        {
            "repo_id": 101,
            "name": "PlaceMentor-AI",
            "full_name": "Purv0040/PlaceMentor-AI",
            "description": "AI placement copilot",
            "html_url": "https://github.com/Purv0040/PlaceMentor-AI",
            "language": "TypeScript",
            "languages": {"TypeScript": 1000},
            "stars": 42,
            "forks": 12,
            "topics": ["react", "fastapi"],
            "has_readme": True,
            "is_fork": False,
            "size": 5000,
        },
        {
            "repo_id": 102,
            "name": "microservice-event-bus",
            "full_name": "Purv0040/microservice-event-bus",
            "description": "Event bus in Go",
            "html_url": "https://github.com/Purv0040/microservice-event-bus",
            "language": "Go",
            "languages": {"Go": 1000},
            "stars": 28,
            "forks": 6,
            "topics": ["go", "rabbitmq"],
            "has_readme": True,
            "is_fork": False,
            "size": 2000,
        }
    ]

    with patch("app.integrations.github_client.GitHubAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.return_value = mock_profile

        res_connect = client.post("/api/v1/github/connect", json={"github_username": "Purv0040"}, headers=auth_headers)
        assert res_connect.status_code == 200
        body_connect = res_connect.json()
        assert body_connect["success"] is True
        assert body_connect["data"]["github_username"] == "Purv0040"

    res_get = client.get("/api/v1/github", headers=auth_headers)
    assert res_get.status_code == 200
    body_get = res_get.json()
    assert body_get["data"]["github_username"] == "Purv0040"

    with patch("app.integrations.github_client.GitHubAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile, \
         patch("app.integrations.github_client.GitHubAPIClient.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_profile.return_value = mock_profile
        mock_get_repos.return_value = mock_repos

        res_sync = client.post("/api/v1/github/sync", headers=auth_headers)
        assert res_sync.status_code == 200
        body_sync = res_sync.json()
        assert body_sync["success"] is True
        assert body_sync["data"]["statistics"]["total_repositories"] == 2
        assert body_sync["data"]["statistics"]["total_stars"] == 70

    res_repos = client.get("/api/v1/github/repositories?page=1&limit=10", headers=auth_headers)
    assert res_repos.status_code == 200
    body_repos = res_repos.json()
    assert body_repos["data"]["total"] == 2
    assert len(body_repos["data"]["items"]) == 2

    mock_ai_output = {
        "profile": {"username": "Purv0040", "public_repos": 14},
        "activity": {"total_public_repos": 14, "total_stars": 70, "total_forks": 18},
        "languages": {"primary_language": "TypeScript", "all_languages": ["TypeScript", "Go"]},
        "technical_categories": [{"name": "Frontend", "detected": True, "evidence": ["PlaceMentor-AI"]}],
        "complexity_analyses": [{"repo_name": "PlaceMentor-AI", "complexity_level": "advanced", "confidence": "high"}],
        "strengths": ["Strong TypeScript and Go technical variety"],
        "gaps": ["Add Kubernetes container orchestration evidence"],
        "technical_patterns": ["Microservices and REST API architecture"],
        "recommendations": ["Add architecture diagrams to repositories"],
        "evidence_summary": "Solid engineering portfolio with production-grade fullstack microservices."
    }

    with patch("app.integrations.ai_client.AIClient.analyze_github", new_callable=AsyncMock) as mock_ai_analyze:
        mock_ai_analyze.return_value = mock_ai_output

        res_analyze = client.post("/api/v1/github/analyze", headers=auth_headers)
        assert res_analyze.status_code == 200
        body_analyze = res_analyze.json()
        assert body_analyze["success"] is True
        assert body_analyze["data"]["analysis"]["profile"]["username"] == "Purv0040"

    res_fetch_analysis = client.get("/api/v1/github/analysis", headers=auth_headers)
    assert res_fetch_analysis.status_code == 200
    assert res_fetch_analysis.json()["data"]["analysis"]["profile"]["username"] == "Purv0040"

    res_del = client.delete("/api/v1/github", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["disconnected"] is True

    res_after = client.get("/api/v1/github", headers=auth_headers)
    assert res_after.status_code == 404
