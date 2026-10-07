import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from app.services.readiness_service import ReadinessService
from app.engines.readiness_engine import DeterministicReadinessEngine


@pytest.mark.asyncio
async def test_deterministic_scoring_formula():
    engine = DeterministicReadinessEngine()

    resume_data = {"_id": "res_1", "analysis": {"ats_score": {"score": 80}, "skills": {"programming": ["Python", "FastAPI"]}}}
    leetcode_data = {"_id": "lc_1", "statistics": {"total_solved": 150, "easy_solved": 50, "medium_solved": 80, "hard_solved": 20}}
    projects_list = [{"_id": "proj_1", "title": "P1", "score": 90, "status": "active", "githubUrl": "https://github.com/u/p1"}]
    github_data = {"_id": "gh_1", "github_username": "user", "statistics": {"total_repositories": 10, "total_stars": 5, "primary_language": "Python"}}

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

    # All 7 categories present
    cats = res["categories"]
    assert "Resume" in cats
    assert "DSA" in cats
    assert "Projects" in cats
    assert "GitHub" in cats
    assert "CS Fundamentals" in cats
    assert "Communication" in cats
    assert "Interview" in cats

    assert cats["Resume"]["status"] == "scored"
    assert cats["DSA"]["status"] == "scored"
    assert cats["Projects"]["status"] == "scored"
    assert cats["GitHub"]["status"] == "scored"
    assert cats["Interview"]["status"] == "insufficient_data"

    # Weight normalization math check
    sum_weights = sum(res["weights_used"].values())
    assert abs(sum_weights - 1.0) < 0.001


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


@pytest.mark.asyncio
async def test_target_role_from_profile(mock_db):
    service = ReadinessService(mock_db)
    user_id = "user_profile_role_1"

    # Set profile target role to Full Stack Engineer
    await mock_db["student_profiles"].insert_one({
        "user_id": user_id,
        "career": {"targetRole": "Full Stack Engineer"},
        "skills": {"selectedSkills": ["JavaScript", "React", "Node.js"]}
    })

    analysis = await service.analyze_readiness(user_id)
    assert analysis["target_role"] == "Full Stack Engineer"
    assert analysis["role_alignment"]["role"] == "Full Stack Engineer"
    assert "React" in analysis["role_alignment"]["aligned_skills"] or "JavaScript" in analysis["role_alignment"]["aligned_skills"]


@pytest.mark.asyncio
async def test_missing_target_role(mock_db):
    engine = DeterministicReadinessEngine()
    res = engine.compute(target_role=None)

    assert res["target_role"] == "Unspecified Role"
    assert res["role_alignment"]["role"] == "Unspecified Role"
    assert res["role_alignment"]["status"] == "insufficient_data"


@pytest.mark.asyncio
async def test_role_alignment_dynamic_comparison():
    engine = DeterministicReadinessEngine()
    profile = {"skills": {"selectedSkills": ["Python", "PyTorch", "NumPy", "Pandas"]}}

    res_ml = engine.compute(target_role="AI/ML Engineer", profile_data=profile)
    assert "PyTorch" in res_ml["role_alignment"]["aligned_skills"] or "Python" in res_ml["role_alignment"]["aligned_skills"]

    res_fs = engine.compute(target_role="Frontend Engineer", profile_data=profile)
    assert "React" in res_fs["role_alignment"]["missing_skills"]


@pytest.mark.asyncio
async def test_missing_interview_and_communication_behavior():
    engine = DeterministicReadinessEngine()
    res = engine.compute(target_role="Backend Developer", interview_data=None, communication_data=None)

    cats = res["categories"]
    assert cats["Interview"]["status"] == "insufficient_data"
    assert cats["Interview"]["score"] is None
    assert cats["Interview"]["confidence"] == 0.0

    assert cats["Communication"]["confidence"] <= 0.55  # Limited proxy or insufficient


@pytest.mark.asyncio
async def test_provenance_and_stale_data(mock_db):
    service = ReadinessService(mock_db)
    user_id = "user_stale_prov_1"
    stale_date = datetime.utcnow() - timedelta(days=20)

    await mock_db["leetcode_profiles"].insert_one({
        "user_id": user_id,
        "leetcode_username": "stale_user",
        "statistics": {"total_solved": 100},
        "updated_at": stale_date
    })

    analysis = await service.analyze_readiness(user_id, target_role_override="Backend Developer")
    assert len(analysis["stale_data"]) >= 1
    assert analysis["stale_data"][0]["source"] == "leetcode"
    assert "provenance" in analysis
    assert analysis["provenance"]["leetcode_analysis_id"] is not None
