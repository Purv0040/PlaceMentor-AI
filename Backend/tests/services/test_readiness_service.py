import pytest
from unittest.mock import AsyncMock, patch
from app.services.readiness_service import ReadinessService
from app.engines.readiness_engine import DeterministicReadinessEngine


@pytest.mark.asyncio
async def test_deterministic_scoring_formula():
    engine = DeterministicReadinessEngine()

    resume_data = {"analysis": {"ats_score": {"score": 80}, "skills": {"programming": ["Python", "FastAPI"]}}}
    leetcode_data = {"statistics": {"total_solved": 150, "easy_solved": 50, "medium_solved": 80, "hard_solved": 20}}
    projects_list = [{"title": "P1", "score": 90, "status": "active", "githubUrl": "https://github.com/u/p1"}]
    github_data = {"github_username": "user", "statistics": {"total_repositories": 10, "total_stars": 5, "primary_language": "Python"}}

    res = engine.compute(
        target_role="Backend Developer",
        resume_data=resume_data,
        github_data=github_data,
        leetcode_data=leetcode_data,
        projects_list=projects_list
    )

    assert res["overall_score"] is not None
    assert res["overall_score"] >= 50
    assert res["readiness_label"] in ["Placement Ready", "Advanced", "Developing"]
    assert res["categories"]["Resume"]["status"] == "scored"
    assert res["categories"]["DSA"]["status"] == "scored"
    assert res["categories"]["Projects"]["status"] == "scored"
    assert res["categories"]["GitHub"]["status"] == "scored"


@pytest.mark.asyncio
async def test_readiness_service_analyze_and_summary(mock_db):
    service = ReadinessService(mock_db)
    user_id = "user_readiness_serv_1"

    analysis = await service.analyze_readiness(user_id, target_role_override="AI/ML Engineer")
    assert analysis["user_id"] == user_id
    assert analysis["target_role"] == "AI/ML Engineer"

    latest = await service.get_latest_readiness(user_id)
    assert latest["id"] == analysis["id"]

    summary = await service.get_readiness_summary(user_id)
    assert summary["user_id"] == user_id
    assert summary["target_role"] == "AI/ML Engineer"
