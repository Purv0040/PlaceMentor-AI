"""
Tests for Daily Task Engine.
Validates candidate task collection, filtering of completed tasks, carryover of overdue tasks,
deterministic 5-level priority ranking, strict time budget enforcement, and API integration.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.task_engine import DailyTaskEngine
from app.schemas.daily_task import TodayTasksRequest, TodayTasksResponse
from app.schemas.roadmap import RoadmapTask, PersonalizedRoadmap, RoadmapPhase


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return DailyTaskEngine()


@pytest.fixture
def sample_roadmap():
    tasks = [
        RoadmapTask(id="task_d5_1", day=5, category="DSA", title="Day 5: Linked List Operations", description="Implement linked list", estimated_minutes=30, difficulty="Beginner", priority="High", skill="Linked Lists"),
        RoadmapTask(id="task_d5_2", day=5, category="CS Fundamentals", title="Day 5: OOP Principles", description="Review OOP", estimated_minutes=30, difficulty="Beginner", priority="Medium", skill="OOP"),
        RoadmapTask(id="task_d10_1", day=10, category="Resume", title="Day 10: Resume ATS Audit", description="Rewrite bullet points", estimated_minutes=60, difficulty="Beginner", priority="High", skill="Resume"),
        RoadmapTask(id="task_d10_2", day=10, category="DSA", title="Day 10: Array Sliding Window", description="Solve LeetCode sliding window", estimated_minutes=60, difficulty="Beginner", priority="High", skill="Arrays"),
        RoadmapTask(id="task_d11_1", day=11, category="Backend", title="Day 11: FastAPI Setup", description="Setup FastAPI app", estimated_minutes=60, difficulty="Intermediate", priority="High", skill="FastAPI"),
    ]
    p1 = RoadmapPhase(phase_number=1, name="Phase 1: Foundation", day_range="Days 1-30", start_day=1, end_day=30, goal="Foundation", tasks=tasks)
    return PersonalizedRoadmap(
        target_role="Backend Developer",
        total_days=90,
        available_minutes_per_day=120,
        total_estimated_hours=180.0,
        phases=[p1],
        all_tasks=tasks,
        summary="Sample roadmap",
    )


# ---------------------------------------------------------------------------
# Test 1: Standard Scheduled Day
# ---------------------------------------------------------------------------

def test_daily_task_standard_day(engine, sample_roadmap):
    req = TodayTasksRequest(
        roadmap=sample_roadmap,
        current_day=10,
        completed_tasks=[],
        missed_tasks=[],
        available_time=120,
        target_role="Backend Developer",
    )

    res = engine.get_today_tasks(req)

    assert isinstance(res, TodayTasksResponse)
    assert res.target_role == "Backend Developer"
    assert res.current_day == 10
    assert res.available_time == 120
    assert res.total_scheduled_minutes <= 120
    assert len(res.tasks) >= 1

    # Verify task attributes
    task_ids = [t.id for t in res.tasks]
    assert "task_d10_1" in task_ids or "task_d10_2" in task_ids
    for t in res.tasks:
        assert t.source_roadmap_day in [10, 11]
        assert len(t.reason) > 0


# ---------------------------------------------------------------------------
# Test 2: Overdue / Missed Task Carryover
# ---------------------------------------------------------------------------

def test_daily_task_overdue_carryover(engine, sample_roadmap):
    # Student missed task_d5_1 on Day 5, now on Day 10
    req = TodayTasksRequest(
        roadmap=sample_roadmap,
        current_day=10,
        completed_tasks=[],
        missed_tasks=["task_d5_1"],
        available_time=120,
        target_role="Backend Developer",
    )

    res = engine.get_today_tasks(req)

    task_ids = [t.id for t in res.tasks]
    assert "task_d5_1" in task_ids
    assert res.overdue_rescheduled_count >= 1
    assert res.total_scheduled_minutes <= 120

    # Verify reason annotates carryover
    overdue_task = next((t for t in res.tasks if t.id == "task_d5_1"), None)
    assert overdue_task is not None
    assert "Overdue" in overdue_task.reason
    assert overdue_task.source_roadmap_day == 5


# ---------------------------------------------------------------------------
# Test 3: Completed Task Filtering
# ---------------------------------------------------------------------------

def test_daily_task_completed_filtering(engine, sample_roadmap):
    # Student already completed task_d10_1
    req = TodayTasksRequest(
        roadmap=sample_roadmap,
        current_day=10,
        completed_tasks=["task_d10_1"],
        missed_tasks=[],
        available_time=120,
        target_role="Backend Developer",
    )

    res = engine.get_today_tasks(req)

    task_ids = [t.id for t in res.tasks]
    assert "task_d10_1" not in task_ids
    assert res.completed_count_so_far == 1


# ---------------------------------------------------------------------------
# Test 4: Strict Daily Time Budget Enforcement
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("budget", [30, 60, 90, 120])
def test_daily_task_strict_time_budget(engine, sample_roadmap, budget):
    req = TodayTasksRequest(
        roadmap=sample_roadmap,
        current_day=10,
        completed_tasks=[],
        missed_tasks=["task_d5_1"],  # Overdue candidate
        available_time=budget,
        target_role="Backend Developer",
    )

    res = engine.get_today_tasks(req)

    assert res.total_scheduled_minutes <= budget
    total_from_items = sum(t.estimated_minutes for t in res.tasks)
    assert total_from_items <= budget


# ---------------------------------------------------------------------------
# Test 5: Deterministic 5-Level Priority Ranking
# ---------------------------------------------------------------------------

def test_daily_task_priority_ranking(engine, sample_roadmap):
    req = TodayTasksRequest(
        roadmap=sample_roadmap,
        current_day=10,
        completed_tasks=[],
        missed_tasks=["task_d5_1"],
        available_time=60,  # Limited time budget (60 mins)
        target_role="Backend Developer",
    )

    res = engine.get_today_tasks(req)

    # First task scheduled should be High priority (either critical gap or overdue High priority)
    assert len(res.tasks) >= 1
    assert res.tasks[0].priority == "High"


# ---------------------------------------------------------------------------
# Test 6: API Endpoint POST /api/ai/tasks/today
# ---------------------------------------------------------------------------

def test_api_today_tasks_endpoint(client):
    payload = {
        "current_day": 10,
        "completed_tasks": ["task_d1_1"],
        "missed_tasks": ["task_d5_1"],
        "available_time": 120,
        "target_role": "Backend Developer",
    }

    response = client.post("/api/ai/tasks/today", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "target_role" in data
    assert data["target_role"] == "Backend Developer"
    assert data["current_day"] == 10
    assert data["available_time"] == 120
    assert data["total_scheduled_minutes"] <= 120
    assert len(data["tasks"]) >= 1
    assert "summary" in data
    assert "reasoning" in data
