import pytest
from fastapi.testclient import TestClient


def test_skill_gaps_unauthenticated_access(client: TestClient):
    """Ensure all skill gaps endpoints reject unauthenticated requests."""
    assert client.post("/api/v1/skill-gaps/analyze").status_code == 401
    assert client.get("/api/v1/skill-gaps").status_code == 401
    assert client.get("/api/v1/skill-gaps/summary").status_code == 401
    assert client.get("/api/v1/skill-gaps/history").status_code == 401
    assert client.get("/api/v1/skill-gaps/650c1f2e8f1b2c3d4e5f6a7b").status_code == 401


def test_skill_gaps_analyze_and_retrieve_flow(client: TestClient, auth_headers: dict):
    """Test full skill gaps flow: analyze -> get latest -> summary -> history -> get by ID."""
    # 1. Trigger skill gap analysis
    res_analyze = client.post(
        "/api/v1/skill-gaps/analyze",
        json={"target_role": "Backend Developer"},
        headers=auth_headers
    )
    assert res_analyze.status_code == 200
    data_analyze = res_analyze.json()["data"]
    assert data_analyze["target_role"] == "Backend Developer"
    assert "overall_coverage" in data_analyze
    assert "summary" in data_analyze
    assert "skills" in data_analyze
    assert "priority_gaps" in data_analyze
    assert "category_coverage" in data_analyze
    assert "matrix2x2" in data_analyze
    analysis_id = data_analyze["id"]

    # 2. Get latest analysis
    res_latest = client.get("/api/v1/skill-gaps", headers=auth_headers)
    assert res_latest.status_code == 200
    data_latest = res_latest.json()["data"]
    assert data_latest["id"] == analysis_id
    assert data_latest["target_role"] == "Backend Developer"

    # 3. Get summary for dashboard
    res_summary = client.get("/api/v1/skill-gaps/summary", headers=auth_headers)
    assert res_summary.status_code == 200
    data_summary = res_summary.json()["data"]
    assert data_summary["target_role"] == "Backend Developer"
    assert "overall_coverage" in data_summary
    assert "gaps_identified_count" in data_summary
    assert "top_priority_gaps" in data_summary

    # 4. Get history
    res_history = client.get("/api/v1/skill-gaps/history", headers=auth_headers)
    assert res_history.status_code == 200
    data_history = res_history.json()["data"]
    assert data_history["total"] >= 1
    assert len(data_history["items"]) >= 1

    # 5. Get by ID
    res_by_id = client.get(f"/api/v1/skill-gaps/{analysis_id}", headers=auth_headers)
    assert res_by_id.status_code == 200
    assert res_by_id.json()["data"]["id"] == analysis_id

    # 6. Invalid ID returns 404
    res_invalid = client.get("/api/v1/skill-gaps/650c1f2e8f1b2c3d4e5f9999", headers=auth_headers)
    assert res_invalid.status_code == 404
