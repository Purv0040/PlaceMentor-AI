import pytest
from fastapi.testclient import TestClient


def test_adaptive_unauthenticated_access(client: TestClient):
    """Ensure adaptive endpoints require authentication."""
    assert client.get("/api/v1/adaptive/summary").status_code == 401
    assert client.post("/api/v1/adaptive/recalculate").status_code == 401
    assert client.get("/api/v1/adaptive/recommendations").status_code == 401


def test_adaptive_rebalance_and_apply_flow(client: TestClient, auth_headers: dict):
    """Test adaptive recalculate, recommendation retrieval, and applying recommendations."""
    # 1. Generate roadmap
    client.post("/api/v1/roadmap/generate", json={"target_role": "Backend Developer"}, headers=auth_headers)

    # 2. Get adaptive summary
    res_sum = client.get("/api/v1/adaptive/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    assert "status" in res_sum.json()

    # 3. Recalculate adaptive plan
    res_recalc = client.post("/api/v1/adaptive/recalculate", headers=auth_headers)
    assert res_recalc.status_code == 200
    recalc_data = res_recalc.json()
    assert "trigger" in recalc_data
    assert "recommendation" in recalc_data
    event_id = recalc_data["id"]

    # 4. Get recommendations
    res_recs = client.get("/api/v1/adaptive/recommendations", headers=auth_headers)
    assert res_recs.status_code == 200
    assert len(res_recs.json()) >= 1

    # 5. Apply adaptation
    res_apply = client.post("/api/v1/adaptive/apply", json={"adaptation_id": event_id}, headers=auth_headers)
    assert res_apply.status_code == 200
    assert res_apply.json()["status"] == "success"
