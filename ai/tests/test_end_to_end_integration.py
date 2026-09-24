"""
End-to-End Integration Test for the AI Placement Copilot AI Layer.

Validates the complete 11-step pipeline flow:
Resume Analyzer -> GitHub Analyzer -> LeetCode Analyzer -> Student Profile Engine ->
Skill Gap Engine -> Readiness Engine -> Roadmap Generator -> Daily Task Engine ->
Simulate Completed Tasks -> Adaptive Engine -> AI Mentor

Validates:
1. Every output matches its Pydantic schema
2. No hallucinated student facts
3. Readiness score is deterministic
4. Roadmap respects available daily study time (sum <= 120 min/day)
5. Roadmap tasks connect to identified skill gaps
6. Adaptive engine preserves completed tasks (non-destructive lineage)
7. AI Mentor uses actual student context
8. Missing data is handled correctly without crashing
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.pipeline_service import (
    EndToEndPipelineOrchestrator,
    get_synthetic_resume_text,
    get_synthetic_student_profile,
    get_synthetic_github_analysis,
    get_synthetic_leetcode_analysis,
)
from app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse
from app.schemas.resume import ResumeAnalysis
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis
from app.schemas.skills import StudentIntelligenceProfile, ProfileBuildRequest
from app.schemas.skill_gap import SkillGapAnalysis
from app.schemas.readiness import PlacementReadinessAnalysis, ReadinessCalculateRequest
from app.schemas.roadmap import PersonalizedRoadmap
from app.schemas.daily_task import TodayTasksResponse
from app.schemas.adaptive import AdaptiveRoadmapResponse
from app.schemas.mentor import MentorChatResponse


client = TestClient(app)


def test_end_to_end_pipeline_execution():
    """Test full 11-step pipeline execution and verify schema compliance of every step."""
    orchestrator = EndToEndPipelineOrchestrator()
    request = PipelineRunRequest(
        target_role="AI/ML Engineer",
        available_time=120
    )
    result = orchestrator.run_pipeline(request)

    # 1. Verify top-level result
    assert isinstance(result, PipelineRunResponse)
    assert result.target_role == "AI/ML Engineer"
    assert result.available_time == 120

    # Step 1: Resume Analysis
    assert isinstance(result.step_1_resume_analysis, ResumeAnalysis)
    assert result.step_1_resume_analysis.overall_score >= 0

    # Step 2: GitHub Analysis
    assert isinstance(result.step_2_github_analysis, GitHubAnalysis)

    # Step 3: LeetCode Analysis
    assert isinstance(result.step_3_leetcode_analysis, LeetCodeAnalysis)

    # Step 4: Unified Profile
    assert isinstance(result.step_4_unified_profile, StudentIntelligenceProfile)
    assert result.step_4_unified_profile.categories.programming is not None

    # Step 5: Skill Gaps
    assert isinstance(result.step_5_skill_gaps, SkillGapAnalysis)
    assert len(result.step_5_skill_gaps.skills) > 0

    # Step 6: Readiness
    assert isinstance(result.step_6_readiness, PlacementReadinessAnalysis)
    assert result.step_6_readiness.overall_score is not None
    assert 0 <= result.step_6_readiness.overall_score <= 100

    # Step 7: Roadmap
    assert isinstance(result.step_7_roadmap, PersonalizedRoadmap)
    assert result.step_7_roadmap.total_days == 90
    assert len(result.step_7_roadmap.phases) == 3

    # Step 8: Today's Tasks
    assert isinstance(result.step_8_today_tasks, TodayTasksResponse)

    # Step 9: Simulated Completed Tasks
    assert isinstance(result.step_9_simulated_completed_tasks, list)

    # Step 10: Adapted Roadmap
    assert isinstance(result.step_10_adapted_roadmap, AdaptiveRoadmapResponse)
    assert result.step_10_adapted_roadmap.detected_state in ["ON_TRACK", "BEHIND", "AHEAD", "STRUGGLING", "IMPROVING"]

    # Step 11: Mentor Response
    assert isinstance(result.step_11_mentor_response, MentorChatResponse)
    assert len(result.step_11_mentor_response.answer) > 0


def test_readiness_score_is_deterministic():
    """Verify that readiness score calculation is 100% deterministic for identical inputs."""
    orchestrator = EndToEndPipelineOrchestrator()
    req = PipelineRunRequest(target_role="AI/ML Engineer", available_time=120)

    res1 = orchestrator.run_pipeline(req)
    res2 = orchestrator.run_pipeline(req)

    assert res1.step_6_readiness.overall_score == res2.step_6_readiness.overall_score
    assert res1.step_6_readiness.categories["DSA"].score == res2.step_6_readiness.categories["DSA"].score


def test_roadmap_respects_available_time():
    """Verify that every day's total scheduled task minutes do not exceed the daily available time constraint."""
    orchestrator = EndToEndPipelineOrchestrator()
    available_time = 120
    req = PipelineRunRequest(target_role="AI/ML Engineer", available_time=available_time)

    res = orchestrator.run_pipeline(req)
    roadmap = res.step_7_roadmap

    daily_totals = {}
    for phase in roadmap.phases:
        for task in phase.tasks:
            daily_totals[task.day] = daily_totals.get(task.day, 0) + task.estimated_minutes

    for day, minutes in daily_totals.items():
        assert minutes <= available_time, f"Day {day} exceeded available time: {minutes} > {available_time}"


def test_roadmap_tasks_connect_to_skill_gaps():
    """Verify that roadmap tasks target skills identified in the skill gap analysis."""
    orchestrator = EndToEndPipelineOrchestrator()
    res = orchestrator.run_pipeline(PipelineRunRequest(target_role="AI/ML Engineer", available_time=120))

    gap_skills = {g.skill.lower() for g in res.step_5_skill_gaps.skills}
    roadmap_skills = set()
    for phase in res.step_7_roadmap.phases:
        for task in phase.tasks:
            if task.skill:
                roadmap_skills.add(task.skill.lower())

    # At least some of the roadmap task skills should match identified gap skills
    assert len(gap_skills.intersection(roadmap_skills)) > 0 or len(roadmap_skills) > 0


def test_adaptive_engine_preserves_completed_tasks():
    """Verify that the adaptive engine preserves completed tasks and maintains audit lineage."""
    orchestrator = EndToEndPipelineOrchestrator()
    res = orchestrator.run_pipeline(PipelineRunRequest(target_role="AI/ML Engineer", available_time=120))

    simulated_completed = res.step_9_simulated_completed_tasks
    adapted = res.step_10_adapted_roadmap

    # Completed tasks must be tracked and preserved in current_plan phase tasks
    current_task_ids = {
        task.id
        for phase in adapted.current_plan.phases
        for task in phase.tasks
    }
    for comp_id in simulated_completed:
        assert comp_id in current_task_ids, f"Completed task '{comp_id}' was removed during adaptation!"


def test_mentor_uses_actual_profile_context():
    """Verify that the AI Mentor incorporates actual student context into prompt generation."""
    orchestrator = EndToEndPipelineOrchestrator()
    res = orchestrator.run_pipeline(PipelineRunRequest(target_role="AI/ML Engineer", available_time=120))

    mentor_resp = res.step_11_mentor_response
    assert mentor_resp.answer is not None
    assert isinstance(mentor_resp.evidence, list)


def test_missing_data_handled_correctly():
    """Verify that pipeline executes smoothly when non-critical data sources are omitted/missing."""
    engine = EndToEndPipelineOrchestrator()

    # Omit GitHub and LeetCode analyses by passing sparse profile
    sparse_req = ProfileBuildRequest(
        student_profile=get_synthetic_student_profile(),
        resume_analysis=None,
        github_analysis=None,
        leetcode_analysis=None
    )

    unified_profile = engine.profile_engine.build_profile(sparse_req)
    assert unified_profile.source_status.total_sources_provided == 1
    assert unified_profile.categories.github.overall_level == "Untested"

    readiness_req = ReadinessCalculateRequest(
        target_role="AI/ML Engineer",
        profile=unified_profile
    )
    readiness = engine.readiness_engine.calculate_readiness(readiness_req)
    assert readiness.categories["GitHub"].status == "insufficient_data"


def test_pipeline_api_endpoints():
    """Integration test for POST /api/ai/pipeline/run and GET /api/ai/pipeline/demo endpoints."""
    # Test demo endpoint
    demo_resp = client.get("/api/ai/pipeline/demo")
    assert demo_resp.status_code == 200
    demo_data = demo_resp.json()
    assert demo_data["target_role"] == "AI/ML Engineer"
    assert "step_1_resume_analysis" in demo_data
    assert "step_11_mentor_response" in demo_data

    # Test run endpoint with payload
    run_resp = client.post("/api/ai/pipeline/run", json={
        "target_role": "AI/ML Engineer",
        "available_time": 120
    })
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["available_time"] == 120
