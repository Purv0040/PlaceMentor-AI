"""
Unit and integration tests for the Adaptive Roadmap Engine.
Tests state detection (ON_TRACK, BEHIND, AHEAD, STRUGGLING, IMPROVING), strategy adaptations,
non-destructive lineage, missed task reconciliation, configurable thresholds, and FastAPI endpoint.
"""
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.adaptive_engine import AdaptiveRoadmapEngine
from app.schemas.adaptive import (
    AdaptiveRoadmapRequest,
    AdaptiveRoadmapResponse,
    AdaptiveThresholds,
    StudentPerformancePayload,
    StudentProgressPayload,
)
from app.schemas.roadmap import (
    PersonalizedRoadmap,
    RoadmapPhase,
    RoadmapTask,
)


@pytest.fixture
def mock_llm_service():
    """Mock LLMService for deterministic execution without external API calls."""
    return MagicMock()


@pytest.fixture
def sample_roadmap():
    """Create a sample baseline 90-day PersonalizedRoadmap for testing."""
    tasks = [
        RoadmapTask(
            id="task_d1_1",
            day=1,
            category="DSA",
            title="Arrays & Strings Practice",
            description="Solve 2 easy array problems",
            estimated_minutes=45,
            difficulty="Beginner",
            priority="High",
            skill="Arrays",
            status="pending",
        ),
        RoadmapTask(
            id="task_d1_2",
            day=1,
            category="Backend",
            title="FastAPI Setup",
            description="Create basic routes",
            estimated_minutes=45,
            difficulty="Intermediate",
            priority="Medium",
            skill="FastAPI",
            status="pending",
        ),
        RoadmapTask(
            id="task_d2_1",
            day=2,
            category="DSA",
            title="Two Pointers Technique",
            description="Solve 2 medium problems",
            estimated_minutes=60,
            difficulty="Intermediate",
            priority="High",
            skill="Arrays",
            status="pending",
        ),
        RoadmapTask(
            id="task_d2_2",
            day=2,
            category="CS Fundamentals",
            title="OS Process vs Thread",
            description="Review concurrency basics",
            estimated_minutes=30,
            difficulty="Intermediate",
            priority="Low",
            skill="OS",
            status="pending",
        ),
        RoadmapTask(
            id="task_d20_1",
            day=20,
            category="DSA",
            title="Advanced Dynamic Programming",
            description="Solve DP on Trees",
            estimated_minutes=60,
            difficulty="Advanced",
            priority="High",
            skill="Dynamic Programming",
            status="pending",
        ),
    ]

    return PersonalizedRoadmap(
        target_role="Backend Developer",
        total_days=90,
        available_minutes_per_day=120,
        total_estimated_hours=4.0,
        phases=[
            RoadmapPhase(
                phase_number=1,
                name="Phase 1: Foundation",
                day_range="Days 1-30",
                start_day=1,
                end_day=30,
                goal="Foundation phase",
                tasks=tasks,
            )
        ],
        all_tasks=tasks,
        summary="Test sample baseline roadmap.",
    )


def test_on_track_state(sample_roadmap, mock_llm_service):
    """Test ON_TRACK state detection (completion rate = 85%)."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)
    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=["task_d1_1"],
            missed_tasks=[],
            completion_rate=85.0,
            current_day=2,
        ),
        performance=StudentPerformancePayload(available_time=120),
    )

    response = engine.adapt_roadmap(req)

    assert response.detected_state == "ON_TRACK"
    assert "ON_TRACK" in response.state_description
    assert response.original_plan.target_role == "Backend Developer"
    # Completed task must keep status='completed'
    completed_task = next(t for t in response.current_plan.all_tasks if t.id == "task_d1_1")
    assert completed_task.status == "completed"


def test_behind_state_reschedules_low_priority(sample_roadmap, mock_llm_service):
    """Test BEHIND state (completion rate = 60%). Verify low priority task is rescheduled."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)
    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=[],
            missed_tasks=["task_d1_2"],
            completion_rate=60.0,
            current_day=2,
        ),
        performance=StudentPerformancePayload(available_time=120),
    )

    response = engine.adapt_roadmap(req)

    assert response.detected_state == "BEHIND"
    assert len(response.adjustments) > 0
    # Check that at least one task was rescheduled or logged with explanation
    task_resched_adj = [a for a in response.adjustments if a.action_type == "task_rescheduled"]
    assert len(task_resched_adj) > 0
    assert task_resched_adj[0].old_task is not None
    assert task_resched_adj[0].new_task is not None


def test_ahead_state_accelerates_tasks(sample_roadmap, mock_llm_service):
    """Test AHEAD state (completion rate = 95%). Verify difficulty increase or task acceleration."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)
    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=["task_d1_1", "task_d1_2"],
            missed_tasks=[],
            completion_rate=95.0,
            current_day=2,
        ),
        performance=StudentPerformancePayload(available_time=120),
    )

    response = engine.adapt_roadmap(req)

    assert response.detected_state == "AHEAD"
    # Should contain difficulty_increased or task_accelerated adjustment
    ahead_adjs = [a for a in response.adjustments if a.action_type in ["difficulty_increased", "task_accelerated"]]
    assert len(ahead_adjs) > 0


def test_struggling_state_reduces_difficulty_and_injects_prereq(sample_roadmap, mock_llm_service):
    """Test STRUGGLING state (completion rate = 35%). Verify difficulty reduction & prereq task injection."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)
    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=[],
            missed_tasks=["task_d1_1", "task_d1_2"],
            completion_rate=35.0,
            current_day=2,
        ),
        performance=StudentPerformancePayload(
            available_time=120,
            dsa_performance={"accuracy": 30.0, "weak_topics": ["Dynamic Programming"]},
        ),
    )

    response = engine.adapt_roadmap(req)

    assert response.detected_state == "STRUGGLING"
    diff_reduced_adjs = [a for a in response.adjustments if a.action_type == "difficulty_reduced"]
    prereq_injected_adjs = [a for a in response.adjustments if a.action_type == "prerequisite_injected"]

    assert len(diff_reduced_adjs) > 0
    assert len(prereq_injected_adjs) > 0
    assert "Dynamic Programming" in prereq_injected_adjs[0].reason


def test_improving_state_detection(sample_roadmap, mock_llm_service):
    """Test IMPROVING state detection via delta in completion rates."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)
    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=["task_d1_1"],
            missed_tasks=[],
            completion_rate=70.0,
            current_day=2,
            recent_completion_rate=85.0,
            previous_completion_rate=60.0,  # Delta = +25% >= 15%
        ),
        performance=StudentPerformancePayload(available_time=120),
    )

    response = engine.adapt_roadmap(req)

    assert response.detected_state == "IMPROVING"
    assert "IMPROVING" in response.state_description


def test_non_destructive_completed_task_rule(sample_roadmap, mock_llm_service):
    """Test critical rule: Never silently delete completed work."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)
    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=["task_d1_1"],
            missed_tasks=["task_d1_2"],
            completion_rate=50.0,
            current_day=2,
        ),
        performance=StudentPerformancePayload(available_time=120),
    )

    response = engine.adapt_roadmap(req)

    # Task task_d1_1 must remain in all_tasks and have status='completed'
    matching_tasks = [t for t in response.current_plan.all_tasks if t.id == "task_d1_1"]
    assert len(matching_tasks) == 1
    assert matching_tasks[0].status == "completed"


def test_configurable_thresholds(sample_roadmap, mock_llm_service):
    """Test threshold customization altering state detection boundaries."""
    engine = AdaptiveRoadmapEngine(llm_service=mock_llm_service)

    custom_thresholds = AdaptiveThresholds(
        on_track_completion_pct=70.0,
        behind_completion_pct=40.0,
    )

    req = AdaptiveRoadmapRequest(
        roadmap=sample_roadmap,
        progress=StudentProgressPayload(
            completed_tasks=[],
            missed_tasks=[],
            completion_rate=75.0,  # Normally BEHIND (<80%), but with custom thresholds (>=70%) it is ON_TRACK
            current_day=2,
        ),
        performance=StudentPerformancePayload(available_time=120),
        thresholds=custom_thresholds,
    )

    response = engine.adapt_roadmap(req)
    assert response.detected_state == "ON_TRACK"
    assert response.thresholds_used.on_track_completion_pct == 70.0


def test_api_adapt_roadmap_endpoint():
    """Integration test for POST /api/ai/roadmap/adapt."""
    client = TestClient(app)

    payload = {
        "target_role": "Backend Developer",
        "progress": {
            "completed_tasks": ["task_d1_1"],
            "missed_tasks": ["task_d1_2"],
            "completion_rate": 65.0,
            "current_day": 2,
        },
        "performance": {
            "available_time": 120,
            "dsa_performance": {"accuracy": 50.0, "weak_topics": ["Arrays"]},
        },
    }

    response = client.post("/api/ai/roadmap/adapt", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "target_role" in data
    assert "detected_state" in data
    assert "original_plan" in data
    assert "current_plan" in data
    assert "adjustments" in data
    assert data["detected_state"] in ["ON_TRACK", "BEHIND", "AHEAD", "STRUGGLING", "IMPROVING"]
