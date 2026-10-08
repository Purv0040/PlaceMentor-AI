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


def test_cybersecurity_curriculum_personalization(client: TestClient, auth_headers: dict):
    """Test that Cybersecurity Analyst & Engineer produces domain-specific curriculum."""
    res = client.post(
        "/api/v1/roadmap/generate",
        json={
            "target_role": "Cybersecurity Analyst & Engineer",
            "available_minutes_per_day": 120,
            "force_regenerate": True,
        },
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["target_role"] == "Cybersecurity Analyst & Engineer"
    assert data["duration_days"] == 90
    assert len(data["phases"]) == 3

    # 1. Verify Phase goals are specific to Cybersecurity
    p1, p2, p3 = data["phases"]
    assert "networking" in p1["goal"].lower() or "linux" in p1["goal"].lower() or "security" in p1["goal"].lower()
    assert "threat" in p2["goal"].lower() or "vulnerability" in p2["goal"].lower() or "owasp" in p2["goal"].lower()
    assert "hunting" in p3["goal"].lower() or "cloud security" in p3["goal"].lower() or "soc" in p3["goal"].lower() or "interview" in p3["goal"].lower()

    # 2. Extract all tasks across 3 phases
    all_tasks = []
    for phase in data["phases"]:
        all_tasks.extend(phase.get("tasks", []))

    all_titles = " ".join(t.get("title", "") for t in all_tasks).lower()
    all_skills = {t.get("skill", "") for t in all_tasks}
    all_cats = {t.get("category", "") for t in all_tasks}

    # 3. Verify core Cybersecurity competencies are prioritized
    assert any("network" in s.lower() for s in all_skills)
    assert any("siem" in s.lower() or "threat" in s.lower() or "vulnerability" in s.lower() for s in all_skills)
    assert any("owasp" in s.lower() or "linux" in s.lower() or "cryptography" in s.lower() for s in all_skills)
    assert "Networking" in all_cats or "Security" in all_cats

    # 4. Verify specific domain terms appear in titles/curriculum
    assert "wireshark" in all_titles or "packet" in all_titles or "nmap" in all_titles or "firewall" in all_titles
    assert "mitre" in all_titles or "vulnerability" in all_titles or "incident" in all_titles or "siem" in all_titles


def test_aiml_vs_backend_curriculum_distinctness(client: TestClient, auth_headers: dict):
    """Test that AI/ML and Backend Developer produce materially distinct curricula."""
    # AI/ML Roadmap
    res_ai = client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "AI/ML Engineer", "available_minutes_per_day": 180, "force_regenerate": True},
        headers=auth_headers,
    )
    assert res_ai.status_code == 200
    data_ai = res_ai.json()
    assert data_ai["total_estimated_hours"] == 270.0  # 180 min * 90 days / 60

    ai_tasks = [t for phase in data_ai["phases"] for t in phase.get("tasks", [])]
    ai_skills = {t.get("skill", "").lower() for t in ai_tasks}
    ai_titles = " ".join(t.get("title", "") for t in ai_tasks).lower()

    assert any(s in ai_skills for s in ["numpy", "pandas", "scikit-learn", "pytorch", "deep learning", "ai/ml"])
    assert "deep learning" in ai_titles or "neural network" in ai_titles or "transformer" in ai_titles or "pytorch" in ai_titles

    # Backend Roadmap
    res_be = client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer", "available_minutes_per_day": 60, "force_regenerate": True},
        headers=auth_headers,
    )
    assert res_be.status_code == 200
    data_be = res_be.json()
    assert data_be["total_estimated_hours"] == 90.0  # 60 min * 90 days / 60

    be_tasks = [t for phase in data_be["phases"] for t in phase.get("tasks", [])]
    be_skills = {t.get("skill", "").lower() for t in be_tasks}
    be_titles = " ".join(t.get("title", "") for t in be_tasks).lower()

    assert any(s in be_skills for s in ["rest api", "fastapi", "postgresql", "redis", "system design"])
    assert "rest" in be_titles or "database" in be_titles or "system design" in be_titles or "fastapi" in be_titles


def test_roadmap_task_progression_and_non_repetition(client: TestClient, auth_headers: dict):
    """Test that tasks progress through difficulty levels and avoid identical repetitive titles."""
    res = client.post(
        "/api/v1/roadmap/generate",
        json={"target_role": "Backend Developer", "available_minutes_per_day": 120, "force_regenerate": True},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()

    p1, p2, p3 = data["phases"]
    p1_diffs = {t.get("difficulty") for t in p1.get("tasks", [])}
    p3_diffs = {t.get("difficulty") for t in p3.get("tasks", [])}

    assert "Beginner" in p1_diffs
    assert "Advanced" in p3_diffs

    # Verify task titles are varied and progressive across days
    all_titles = [t.get("title") for phase in data["phases"] for t in phase.get("tasks", [])]
    unique_titles = set(all_titles)
    # Most tasks across the 90 days must be unique
    assert len(unique_titles) >= len(all_titles) * 0.8
