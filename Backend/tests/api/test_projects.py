import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


def test_projects_unauthenticated_access(client: TestClient):
    res = client.get("/api/v1/projects")
    assert res.status_code == 401

    res = client.post("/api/v1/projects", json={"title": "Test Proj", "description": "Test Desc"})
    assert res.status_code == 401


def test_projects_full_crud_and_analysis_flow(client: TestClient, auth_headers: dict):
    # 1. Create project
    create_payload = {
        "title": "PlaceMentor AI — SDE Placement Copilot",
        "description": "Full-stack AI placement mentoring platform featuring AST code audit.",
        "category": "Full Stack / AI",
        "role": "Lead Developer",
        "technologies": ["React", "FastAPI", "Python", "MongoDB"],
        "architectureTags": ["Microservices", "REST API", "JWT Auth"],
        "githubUrl": "https://github.com/Purv0040/PlaceMentor-AI",
        "liveUrl": "https://placementor-ai.demo.app",
        "is_featured": True
    }

    res_create = client.post("/api/v1/projects", json=create_payload, headers=auth_headers)
    assert res_create.status_code == 201
    body_create = res_create.json()
    assert body_create["success"] is True
    project_data = body_create["data"]
    project_id = project_data["id"]
    assert project_data["title"] == "PlaceMentor AI — SDE Placement Copilot"
    assert project_data["is_featured"] is True
    assert "Python" in project_data["technologies"]

    # 2. List projects
    res_list = client.get("/api/v1/projects", headers=auth_headers)
    assert res_list.status_code == 200
    body_list = res_list.json()
    assert body_list["total"] >= 1
    assert any(p["id"] == project_id for p in body_list["data"])

    # 3. Get single project
    res_get = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["data"]["id"] == project_id

    # 4. Update project
    update_payload = {
        "title": "PlaceMentor AI — Updated Platform",
        "description": "Updated description with enhanced distributed features."
    }
    res_update = client.put(f"/api/v1/projects/{project_id}", json=update_payload, headers=auth_headers)
    assert res_update.status_code == 200
    assert res_update.json()["data"]["title"] == "PlaceMentor AI — Updated Platform"

    # 5. Patch featured status
    res_featured = client.patch(f"/api/v1/projects/{project_id}/featured", json={"is_featured": False}, headers=auth_headers)
    assert res_featured.status_code == 200
    assert res_featured.json()["data"]["is_featured"] is False

    # 6. Analyze project with mocked AI client
    mock_ai_analysis = {
        "score": 92,
        "score_badge": "Production Grade",
        "complexity_score": 90,
        "architecture_tags": ["Microservices", "REST API", "JWT Auth"],
        "evidence_bullets": ["Engineered PlaceMentor AI with sub-200ms latency."],
        "strengths": ["Solid full-stack architecture"],
        "weaknesses": ["Needs load testing documentation"],
        "recommendations": ["Add automated CI/CD pipeline"]
    }

    with patch("app.integrations.ai_client.AIClient.analyze_project", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_ai_analysis
        res_analyze = client.post(f"/api/v1/projects/{project_id}/analyze", headers=auth_headers)
        assert res_analyze.status_code == 200
        body_analyze = res_analyze.json()
        assert body_analyze["success"] is True
        assert body_analyze["data"]["analysis_status"] == "completed"

    # 7. Fetch project analysis
    res_fetch_analysis = client.get(f"/api/v1/projects/{project_id}/analysis", headers=auth_headers)
    assert res_fetch_analysis.status_code == 200
    assert res_fetch_analysis.json()["data"]["analysis"]["score"] == 92

    # 8. Soft delete project
    res_delete = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert res_delete.status_code == 200
    assert res_delete.json()["data"]["deleted"] is True

    # 9. Verify project no longer in active list
    res_list_after = client.get("/api/v1/projects", headers=auth_headers)
    assert not any(p["id"] == project_id for p in res_list_after.json()["data"])
