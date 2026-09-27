import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


def test_readiness_unauthenticated_access(client: TestClient):
    res = client.get("/api/v1/readiness")
    assert res.status_code == 401

    res = client.post("/api/v1/readiness/analyze", json={})
    assert res.status_code == 401


def test_readiness_analyze_and_retrieve_flow(client: TestClient, auth_headers: dict):
    # 1. Trigger readiness calculation
    res_analyze = client.post("/api/v1/readiness/analyze", json={"target_role": "Backend Developer"}, headers=auth_headers)
    assert res_analyze.status_code == 200
    body_analyze = res_analyze.json()
    assert body_analyze["success"] is True
    data = body_analyze["data"]
    assert data["target_role"] == "Backend Developer"
    assert "categories" in data
    assert "Resume" in data["categories"]

    analysis_id = data["id"]

    # 2. Get latest readiness
    res_latest = client.get("/api/v1/readiness", headers=auth_headers)
    assert res_latest.status_code == 200
    assert res_latest.json()["data"]["id"] == analysis_id

    # 3. Get summary for dashboard
    res_summary = client.get("/api/v1/readiness/summary", headers=auth_headers)
    assert res_summary.status_code == 200
    summary_data = res_summary.json()["data"]
    assert "overall_score" in summary_data
    assert summary_data["target_role"] == "Backend Developer"

    # 4. Get readiness history
    res_history = client.get("/api/v1/readiness/history", headers=auth_headers)
    assert res_history.status_code == 200
    assert res_history.json()["total"] >= 1

    # 5. Get readiness by ID
    res_by_id = client.get(f"/api/v1/readiness/{analysis_id}", headers=auth_headers)
    assert res_by_id.status_code == 200
    assert res_by_id.json()["data"]["id"] == analysis_id
