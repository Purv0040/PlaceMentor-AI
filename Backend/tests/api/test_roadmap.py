import pytest
from fastapi.testclient import TestClient


def test_roadmap_unauthenticated_access(client: TestClient):
    """Ensure roadmap endpoints require authentication."""
    assert client.post("/api/v1/roadmap/generate").status_code == 401
    assert client.get("/api/v1/roadmap").status_code == 401
    assert client.get("/api/v1/roadmap/summary").status_code == 401
    assert client.get("/api/v1/roadmap/invalid_id").status_code == 401


def test_roadmap_generation_and_retrieval_flow(client: TestClient, auth_headers: dict):
    """Test generating, fetching, summary, phases, and weeks for roadmap."""
    # 1. Generate roadmap
    res_gen = client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer", "available_minutes_per_day": 120},
        headers=auth_headers
    )
    assert res_gen.status_code == 200
    data_gen = res_gen.json()
    assert data_gen["target_role"] == "Backend Developer"
    assert data_gen["duration_days"] == 90
    assert len(data_gen["phases"]) == 3
    roadmap_id = data_gen["id"]

    # 2. Get active roadmap
    res_active = client.get("/api/v1/roadmap", headers=auth_headers)
    assert res_active.status_code == 200
    data_active = res_active.json()
    assert data_active["id"] == roadmap_id
    assert data_active["status"] == "active"

    # 3. Get summary
    res_sum = client.get("/api/v1/roadmap/summary", headers=auth_headers)
    assert res_sum.status_code == 200
    data_sum = res_sum.json()
    assert data_sum["roadmap_id"] == roadmap_id
    assert data_sum["target_role"] == "Backend Developer"

    # 4. Get by ID
    res_id = client.get(f"/api/v1/roadmap/{roadmap_id}", headers=auth_headers)
    assert res_id.status_code == 200
    assert res_id.json()["id"] == roadmap_id

    # 5. Get weeks and phases
    res_weeks = client.get(f"/api/v1/roadmap/{roadmap_id}/weeks", headers=auth_headers)
    assert res_weeks.status_code == 200
    assert len(res_weeks.json()) == 13

    res_phases = client.get(f"/api/v1/roadmap/{roadmap_id}/phases", headers=auth_headers)
    assert res_phases.status_code == 200
    assert len(res_phases.json()) == 3

    # 6. Regenerate roadmap
    res_regen = client.post(
        "/api/v1/roadmap/regenerate",
        json={"target_role": "AI/ML Engineer", "available_minutes_per_day": 90},
        headers=auth_headers
    )
    assert res_regen.status_code == 200
    data_regen = res_regen.json()
    assert data_regen["target_role"] == "AI/ML Engineer"
    assert data_regen["id"] != roadmap_id
