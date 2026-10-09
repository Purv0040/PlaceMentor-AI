import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from app.services.readiness_service import ReadinessService
from app.engines.readiness_engine import DeterministicReadinessEngine, DEFAULT_WEIGHTS


@pytest.mark.asyncio
async def test_deterministic_scoring_formula():
    engine = DeterministicReadinessEngine()

    resume_data = {"_id": "res_1", "analysis": {"ats_score": {"score": 80}, "skills": {"programming": ["Python", "FastAPI"]}}}
    leetcode_data = {"_id": "lc_1", "statistics": {"total_solved": 150, "easy_solved": 50, "medium_solved": 80, "hard_solved": 20}}
    projects_list = [
        {"_id": "proj_1", "title": "P1", "score": 90, "status": "active", "githubUrl": "https://github.com/u/p1", "liveUrl": "https://p1.app"},
        {"_id": "proj_2", "title": "P2", "score": 85, "status": "active", "githubUrl": "https://github.com/u/p2"}
    ]
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
    assert res["readiness_status"] in ["assessed", "provisional"]
    assert res["coverage_percentage"] >= 65.0

    # All 7 categories present
    cats = res["categories"]
    assert "Resume" in cats
    assert "DSA" in cats
    assert "Projects" in cats
    assert "GitHub" in cats
    assert "CS Fundamentals" in cats
    assert "Communication" in cats
    assert "Interview" in cats

    assert cats["Resume"]["status"] == "assessed"
    assert cats["DSA"]["status"] == "assessed"
    assert cats["Projects"]["status"] == "assessed"
    assert cats["GitHub"]["status"] == "assessed"
    assert cats["Interview"]["status"] == "not_assessed"

    # Weight normalization math check
    sum_weights = sum(res["weights_used"].values())
    assert abs(sum_weights - 1.0) < 0.001


@pytest.mark.asyncio
async def test_weight_validation_and_custom_weights():
    # Valid custom weights summing to 1.0
    custom = {
        "Resume": 0.20,
        "DSA": 0.30,
        "Projects": 0.20,
        "GitHub": 0.10,
        "CS Fundamentals": 0.10,
        "Communication": 0.05,
        "Interview": 0.05
    }
    engine = DeterministicReadinessEngine(custom_weights=custom)
    assert abs(sum(engine.weights.values()) - 1.0) < 0.001

    # Negative weights should raise ValueError
    with pytest.raises(ValueError):
        DeterministicReadinessEngine(custom_weights={"Resume": -0.1, "DSA": 1.1})


@pytest.mark.asyncio
async def test_readiness_service_analyze_and_summary(mock_db):
    service = ReadinessService(mock_db)
    user_id = "user_readiness_serv_1"

    analysis = await service.analyze_readiness(user_id, target_role_override="AI/ML Engineer")
    assert analysis["user_id"] == user_id
    assert analysis["target_role"] == "AI/ML Engineer"
    assert analysis["calculation_version"] == "2.0"

    latest = await service.get_latest_readiness(user_id)
    assert latest["id"] == analysis["id"]

    summary = await service.get_readiness_summary(user_id)
    assert summary["user_id"] == user_id
    assert summary["target_role"] == "AI/ML Engineer"
    assert "coverage_percentage" in summary


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
async def test_role_alignment_dynamic_comparison_and_aiml_gaps():
    engine = DeterministicReadinessEngine()
    profile = {"skills": {"selectedSkills": ["Python", "NumPy", "Pandas"]}}

    res_ml = engine.compute(target_role="AI/ML Engineer", profile_data=profile)
    assert "Python" in res_ml["role_alignment"]["aligned_skills"]
    assert "PyTorch" in res_ml["role_alignment"]["missing_skills"]
    assert len(res_ml["role_alignment"]["role_specific_gaps"]) >= 1

    # Check that PyTorch gap is specifically identified
    areas = [g["area"] for g in res_ml["role_alignment"]["role_specific_gaps"]]
    assert "Deep Learning & Neural Networks" in areas


@pytest.mark.asyncio
async def test_missing_interview_and_communication_behavior():
    engine = DeterministicReadinessEngine()
    res = engine.compute(target_role="Backend Developer", interview_data=None, communication_data=None)

    cats = res["categories"]
    assert cats["Interview"]["status"] == "not_assessed"
    assert cats["Interview"]["score"] is None
    assert cats["Interview"]["confidence"] == 0.0

    assert cats["Communication"]["confidence"] <= 0.55  # Limited proxy or not assessed


@pytest.mark.asyncio
async def test_score_delta_tracking_across_snapshots(mock_db):
    service = ReadinessService(mock_db)
    user_id = "user_delta_test_1"

    # 1. First snapshot without LeetCode
    s1 = await service.analyze_readiness(user_id, target_role_override="Backend Developer")
    assert s1["previous_score"] is None
    assert s1["score_delta"] is None

    # 2. Add LeetCode evidence
    await mock_db["leetcode_profiles"].insert_one({
        "user_id": user_id,
        "leetcode_username": "coder",
        "statistics": {"total_solved": 200, "easy_solved": 60, "medium_solved": 100, "hard_solved": 40},
        "updated_at": datetime.utcnow()
    })

    # 3. Second snapshot should record previous score and positive delta
    s2 = await service.analyze_readiness(user_id, target_role_override="Backend Developer")
    assert s2["previous_score"] == s1["overall_score"]
    if s1["overall_score"] is not None and s2["overall_score"] is not None:
        assert s2["score_delta"] == s2["overall_score"] - s1["overall_score"]


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
