import pytest
from app.engines.skill_gap_engine import (
    DeterministicSkillGapEngine,
    normalize_skill_name,
    get_canonical_role,
)
from app.services.skill_gap_service import SkillGapService


def test_deterministic_skill_normalization():
    """Verify alias normalization to canonical forms and categories."""
    engine = DeterministicSkillGapEngine()

    assert normalize_skill_name("py") == ("Python", "Programming")
    assert normalize_skill_name("js") == ("JavaScript", "Programming")
    assert normalize_skill_name("reactjs") == ("React", "Frontend")
    assert normalize_skill_name("k8s") == ("Kubernetes", "DevOps")
    assert normalize_skill_name("postgres") == ("PostgreSQL", "Databases")
    assert normalize_skill_name("dsa") == ("Data Structures & Algorithms", "DSA")
    assert get_canonical_role("ai/ml engineer") == "AI/ML Engineer"
    assert get_canonical_role("backend") == "Backend Developer"
    assert get_canonical_role("Backend-Develpoer") == "Backend Developer"
    assert get_canonical_role("backend dev") == "Backend Developer"
    assert get_canonical_role("devops") == "DevOps Engineer"
    assert get_canonical_role("cybersecurity analyst") == "Cybersecurity Analyst"


def test_deterministic_skill_gap_logic():
    """Verify skill gap evaluation, gap types, priority calculations, and coverage mathematics."""
    engine = DeterministicSkillGapEngine()

    mock_profile = {
        "technical_skills": ["Python", "Git"],
        "target_role": "Backend Developer"
    }
    mock_resume = {
        "analysis": {
            "skills_extracted": ["Python", "FastAPI", "PostgreSQL"],
            "experience": [{"role": "Backend Intern", "technologies": ["Python", "FastAPI"]}]
        }
    }
    mock_projects = [
        {
            "title": "Placement Portal",
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "score": 90
        }
    ]
    mock_leetcode = {
        "statistics": {"total_solved": 150},
        "topic_statistics": [
            {"topic_name": "Data Structures & Algorithms", "problems_solved": 150}
        ]
    }
    mock_github = {
        "statistics": {
            "languages": {"Python": 500000, "TypeScript": 10000}
        }
    }

    result = engine.analyze(
        target_role="Backend Developer",
        profile_data=mock_profile,
        resume_data=mock_resume,
        github_data=mock_github,
        leetcode_data=mock_leetcode,
        projects_list=mock_projects
    )

    assert result["target_role"] == "Backend Developer"
    assert "overall_coverage" in result
    assert result["overall_coverage"] > 50

    skills = {s["skill"]: s for s in result["skills"]}
    
    # Python is present across profile, resume, projects, github -> aligned
    assert "Python" in skills
    assert skills["Python"]["gap_type"] == "aligned"
    assert skills["Python"]["evidence_level"] == "strong_evidence"

    # Redis or SQL is required for Backend Developer, but likely not present -> missing/developing
    # Check at least one gap exists
    gap_skills = [s for s in result["skills"] if s["gap_type"] in ("missing", "developing")]
    assert len(gap_skills) >= 1, "Backend Developer should have at least one gap skill"

    # Verify summary counts match sum of skills
    summary = result["summary"]
    total = summary["skills_aligned"] + summary["skills_developing"] + summary["skills_weak"] + summary["skills_missing"]
    assert total == summary["total_required_skills"]


@pytest.mark.asyncio
async def test_skill_gap_service_analyze_and_summary(mock_db):
    """Verify SkillGapService data orchestration, persistence, and summary generation."""
    service = SkillGapService(mock_db)
    user_id = "test_user_service_skill_gap"

    analysis = await service.analyze_skill_gaps(user_id, target_role_override="AI/ML Engineer")
    assert analysis["user_id"] == user_id
    assert analysis["target_role"] == "AI/ML Engineer"
    assert len(analysis["skills"]) > 0

    latest = await service.get_latest_skill_gaps(user_id)
    assert latest["id"] == analysis["id"]

    summary = await service.get_skill_gap_summary(user_id)
    assert summary["user_id"] == user_id
    assert summary["target_role"] == "AI/ML Engineer"
    assert "overall_coverage" in summary
