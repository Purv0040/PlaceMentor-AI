"""
Tests for 90-Day Personalized Roadmap Generator.
Validates 90-day task coverage, 3-phase structure, strict daily time budget enforcement,
prerequisite sequence validation, role relevance, auto-repair, and API endpoint integration.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.roadmap_engine import PersonalizedRoadmapEngine
from app.schemas.roadmap import PersonalizedRoadmap, RoadmapGenerateRequest


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return PersonalizedRoadmapEngine()


# ---------------------------------------------------------------------------
# Test 1: 90-Day Structure & 3-Phase Breakdown
# ---------------------------------------------------------------------------

def test_roadmap_90_day_structure(engine):
    req = RoadmapGenerateRequest(
        target_role="Backend Developer",
        available_minutes_per_day=120,
    )

    roadmap = engine.generate_roadmap(req)

    assert isinstance(roadmap, PersonalizedRoadmap)
    assert roadmap.target_role == "Backend Developer"
    assert roadmap.total_days == 90
    assert roadmap.available_minutes_per_day == 120
    assert len(roadmap.phases) == 3

    p1, p2, p3 = roadmap.phases
    assert p1.phase_number == 1 and p1.start_day == 1 and p1.end_day == 30
    assert p2.phase_number == 2 and p2.start_day == 31 and p2.end_day == 60
    assert p3.phase_number == 3 and p3.start_day == 61 and p3.end_day == 90

    # Ensure every single day from 1 to 90 has scheduled tasks
    days_present = {t.day for t in roadmap.all_tasks}
    assert len(days_present) == 90
    assert min(days_present) == 1
    assert max(days_present) == 90


# ---------------------------------------------------------------------------
# Test 2: Daily Time Budget Constraint Enforcement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("daily_budget", [60, 90, 120, 180])
def test_roadmap_daily_time_budget_constraint(engine, daily_budget):
    req = RoadmapGenerateRequest(
        target_role="AI/ML Engineer",
        available_minutes_per_day=daily_budget,
    )

    roadmap = engine.generate_roadmap(req)

    # Group tasks by day and sum estimated_minutes
    daily_totals = {}
    for t in roadmap.all_tasks:
        daily_totals[t.day] = daily_totals.get(t.day, 0) + t.estimated_minutes

    for day in range(1, 91):
        assert day in daily_totals, f"Day {day} has no scheduled tasks"
        total_mins = daily_totals[day]
        assert total_mins <= daily_budget, f"Day {day} exceeded time budget: {total_mins} mins > {daily_budget} mins"

    assert roadmap.validation_report["daily_time_constraint_passed"] is True


# ---------------------------------------------------------------------------
# Test 3: Prerequisite Order Validation
# ---------------------------------------------------------------------------

def test_roadmap_prerequisite_ordering(engine):
    req = RoadmapGenerateRequest(
        target_role="Full Stack Developer",
        available_minutes_per_day=120,
    )

    roadmap = engine.generate_roadmap(req)

    p1_tasks = [t for t in roadmap.all_tasks if 1 <= t.day <= 30]
    p3_tasks = [t for t in roadmap.all_tasks if 61 <= t.day <= 90]

    # Foundation tasks (e.g. JavaScript, HTML/CSS, Arrays) must appear in Phase 1
    p1_skills = {t.skill.lower() for t in p1_tasks}
    assert "javascript" in p1_skills or "html/css" in p1_skills or "arrays" in p1_skills

    # Advanced prep tasks (e.g. System Design, Mock Interviews) must appear in Phase 3
    p3_categories = {t.category for t in p3_tasks}
    assert "Interview" in p3_categories or "CS Fundamentals" in p3_categories


# ---------------------------------------------------------------------------
# Test 4: Role Relevance & Category Filtering
# ---------------------------------------------------------------------------

def test_roadmap_role_relevance(engine):
    backend_req = RoadmapGenerateRequest(target_role="Backend Developer", available_minutes_per_day=120)
    aiml_req = RoadmapGenerateRequest(target_role="AI/ML Engineer", available_minutes_per_day=120)

    backend_roadmap = engine.generate_roadmap(backend_req)
    aiml_roadmap = engine.generate_roadmap(aiml_req)

    backend_cats = {t.category for t in backend_roadmap.all_tasks}
    aiml_cats = {t.category for t in aiml_roadmap.all_tasks}

    assert "Backend" in backend_cats
    assert "AI/ML" in aiml_cats or "Data Science" in aiml_cats


# ---------------------------------------------------------------------------
# Test 5: Validation Report Integrity
# ---------------------------------------------------------------------------

def test_roadmap_validation_report(engine):
    req = RoadmapGenerateRequest(
        target_role="Data Scientist",
        available_minutes_per_day=90,
    )

    roadmap = engine.generate_roadmap(req)

    report = roadmap.validation_report
    assert report["valid_90_days"] is True
    assert report["daily_time_constraint_passed"] is True
    assert report["phase_structure_passed"] is True
    assert report["prerequisites_passed"] is True
    assert report["total_tasks_scheduled"] >= 90


# ---------------------------------------------------------------------------
# Test 6: API Endpoint POST /api/ai/roadmap/generate
# ---------------------------------------------------------------------------

def test_api_roadmap_generate_endpoint(client):
    payload = {
        "target_role": "AI/ML Engineer",
        "available_minutes_per_day": 120,
        "profile": {},
        "skill_gaps": {},
        "readiness": {},
    }

    response = client.post("/api/ai/roadmap/generate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "target_role" in data
    assert data["target_role"] == "AI/ML Engineer"
    assert data["total_days"] == 90
    assert data["available_minutes_per_day"] == 120
    assert len(data["phases"]) == 3
    assert len(data["all_tasks"]) >= 90
    assert "summary" in data
    assert "validation_report" in data
