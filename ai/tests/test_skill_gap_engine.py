"""
Tests for Skill Gap Engine.
Validates deterministic gap calculation, priority logic, role requirements matching,
handling of strong/weak students, missing evidence, conflicting evidence, and API responses.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.profile_engine import StudentProfileIntelligenceEngine
from app.engines.skill_gap_engine import SkillGapEngine
from app.schemas.skills import ProfileBuildRequest
from app.schemas.skill_gap import SkillGapAnalysis, SkillGapRequest
from app.schemas.student import StudentProfile, SelfReportedSkill
from app.schemas.github import (
    ActivitySummary,
    ComplexityAnalysis,
    GitHubAnalysis,
    GitHubProfileRaw,
    LanguageDistribution,
    TechCategory,
)
from app.schemas.leetcode import (
    DataSourceStatus,
    DifficultyDistribution,
    LeetCodeAnalysis,
    LeetCodeProfileRaw,
    ProblemStatistics,
    TopicAnalysis,
)
from app.schemas.resume import (
    ExtractedSkills,
    LLMResumeExtraction,
    Project,
    ResumeAnalysis,
    ScoreDetail,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def profile_engine():
    return StudentProfileIntelligenceEngine()


@pytest.fixture
def gap_engine():
    return SkillGapEngine()


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def strong_aiml_student_profile(profile_engine):
    """A strong student profile tailored for AI/ML Engineer role."""
    resume = ResumeAnalysis(
        ats_score=ScoreDetail(score=90, reason="Excellent"),
        skills_score=ScoreDetail(score=95, reason="Comprehensive"),
        projects_score=ScoreDetail(score=90, reason="Great metrics"),
        experience_score=ScoreDetail(score=85, reason="Relevant intern"),
        formatting_score=ScoreDetail(score=95, reason="Clean"),
        impact_score=ScoreDetail(score=90, reason="High impact"),
        overall_score=91,
        suggestions=[],
        extracted_skills=ExtractedSkills(
            languages=["Python", "C++", "SQL"],
            frameworks=["PyTorch", "Scikit-learn", "TensorFlow", "FastAPI"],
            tools=["Docker", "Git", "PostgreSQL", "Linux"],
            other=["Deep Learning", "NLP", "Statistics"],
        ),
        education=[],
        experience=[],
        projects=[
            Project(
                name="Deep Neural Network Classifier",
                description="Built ResNet model in PyTorch",
                technologies=["Python", "PyTorch", "Scikit-learn", "Docker"],
                bullets=["Achieved 98.5% accuracy on benchmark"],
                has_metrics=True,
            )
        ],
        certifications=[],
        achievements=[],
        missing_sections=[],
        weak_bullets=[],
        repeated_words=[],
        generic_phrases=[],
        keyword_gaps=[],
    )

    github = GitHubAnalysis(
        profile=GitHubProfileRaw(username="ml_pro", public_repos=8),
        activity=ActivitySummary(
            total_public_repos=8,
            non_fork_repos=7,
            repos_with_readme=7,
            most_starred_count=30,
            total_stars=45,
        ),
        languages=LanguageDistribution(
            primary_language="Python",
            all_languages=["Python", "C++"],
            language_repo_counts={"Python": 6, "C++": 2},
        ),
        technical_categories=[
            TechCategory(name="Machine Learning", detected=True, evidence=["ml-repo-1", "ml-repo-2"]),
            TechCategory(name="Docker", detected=True, evidence=["ml-repo-1"]),
            TechCategory(name="REST API", detected=True, evidence=["api-repo"]),
        ],
        complexity_analyses=[],
        strengths=[],
        gaps=[],
        technical_patterns=[],
        recommendations=[],
        evidence_summary="Strong Python ML portfolio.",
    )

    leetcode = LeetCodeAnalysis(
        profile=LeetCodeProfileRaw(username="ml_pro_lc"),
        problem_statistics=ProblemStatistics(
            total_solved=160,
            easy_solved=50,
            medium_solved=95,
            hard_solved=15,
        ),
        difficulty_distribution=DifficultyDistribution(easy_pct=31, medium_pct=59, hard_pct=10),
        topic_analysis=[
            TopicAnalysis(
                topic="Arrays",
                solved_count=50,
                performance_level="strong",
                evidence=["50 solved"],
                confidence="high",
            ),
            TopicAnalysis(
                topic="Dynamic Programming",
                solved_count=30,
                performance_level="strong",
                evidence=["30 solved"],
                confidence="high",
            ),
        ],
        strong_topics=["Arrays", "Dynamic Programming"],
        data_source_status=DataSourceStatus(provider="LeetCodeGraphQL"),
    )

    return profile_engine.build_profile(
        ProfileBuildRequest(
            resume_analysis=resume,
            github_analysis=github,
            leetcode_analysis=leetcode,
        )
    )


# ---------------------------------------------------------------------------
# Test 1: Strong Student (AI/ML Engineer)
# ---------------------------------------------------------------------------

def test_skill_gap_strong_student(gap_engine, strong_aiml_student_profile):
    analysis = gap_engine.analyze_gaps("AI/ML Engineer", strong_aiml_student_profile)

    assert isinstance(analysis, SkillGapAnalysis)
    assert analysis.target_role == "AI/ML Engineer"
    
    # Python, PyTorch, DSA should have gap == 'None'
    py_gap = next((s for s in analysis.skills if s.skill == "Python"), None)
    assert py_gap is not None
    assert py_gap.gap == "None"
    assert py_gap.priority == "Low"

    # High priority list should be empty or minimal for strong student
    assert len(analysis.high_priority) == 0


# ---------------------------------------------------------------------------
# Test 2: Weak / Baseline Student (Backend Developer)
# ---------------------------------------------------------------------------

def test_skill_gap_weak_student(gap_engine, profile_engine):
    # Empty baseline profile
    empty_profile = profile_engine.build_profile(ProfileBuildRequest())

    analysis = gap_engine.analyze_gaps("Backend Developer", empty_profile)

    assert analysis.target_role == "Backend Developer"
    assert len(analysis.skills) > 0

    # High priority list must contain critical backend skills (Python, DSA, REST API)
    assert "Python" in analysis.high_priority or "Data Structures & Algorithms" in analysis.high_priority or "REST API" in analysis.high_priority
    assert len(analysis.high_priority) >= 2

    # Check gap severity for unevidenced Python
    py_gap = next((s for s in analysis.skills if s.skill == "Python"), None)
    assert py_gap is not None
    assert py_gap.gap in ["High", "Critical"]
    assert py_gap.priority == "High"
    assert "No verified evidence" in py_gap.evidence[0]


# ---------------------------------------------------------------------------
# Test 3: Missing Evidence (No GitHub/LeetCode)
# ---------------------------------------------------------------------------

def test_skill_gap_missing_evidence(gap_engine, profile_engine):
    # Student with only a basic resume (no GitHub or LeetCode)
    resume = ResumeAnalysis(
        ats_score=ScoreDetail(score=70, reason="Basic"),
        skills_score=ScoreDetail(score=70, reason="Basic skills"),
        projects_score=ScoreDetail(score=60, reason="1 project"),
        experience_score=ScoreDetail(score=0, reason="None"),
        formatting_score=ScoreDetail(score=80, reason="OK"),
        impact_score=ScoreDetail(score=60, reason="Generic"),
        overall_score=68,
        suggestions=[],
        extracted_skills=ExtractedSkills(languages=["Python", "HTML"]),
        education=[],
        experience=[],
        projects=[],
        certifications=[],
        achievements=[],
        missing_sections=[],
        weak_bullets=[],
        repeated_words=[],
        generic_phrases=[],
        keyword_gaps=[],
    )

    profile = profile_engine.build_profile(ProfileBuildRequest(resume_analysis=resume))
    analysis = gap_engine.analyze_gaps("Backend Developer", profile)

    # Docker and System Design have no evidence and should be flagged as gaps
    docker_gap = next((s for s in analysis.skills if s.skill == "Docker"), None)
    assert docker_gap is not None
    assert docker_gap.gap in ["Medium", "High", "Critical"]
    assert len(docker_gap.evidence) > 0


# ---------------------------------------------------------------------------
# Test 4: Different Target Roles Comparison
# ---------------------------------------------------------------------------

def test_skill_gap_different_target_roles(gap_engine, strong_aiml_student_profile):
    # Same student evaluated against AI/ML Engineer vs Data Analyst vs Full Stack
    aiml_analysis = gap_engine.analyze_gaps("AI/ML Engineer", strong_aiml_student_profile)
    da_analysis = gap_engine.analyze_gaps("Data Analyst", strong_aiml_student_profile)

    assert aiml_analysis.target_role == "AI/ML Engineer"
    assert da_analysis.target_role == "Data Analyst"

    # Data Analyst requires Tableau / Power BI / Excel which student doesn't have
    da_high_or_med = da_analysis.high_priority + da_analysis.medium_priority
    assert any(skill in da_high_or_med for skill in ["Tableau", "Data Visualization", "Exploratory Data Analysis"])


# ---------------------------------------------------------------------------
# Test 5: Conflicting Evidence Gap Analysis
# ---------------------------------------------------------------------------

def test_skill_gap_conflicting_evidence(gap_engine, profile_engine):
    # Student claims "Advanced" in Docker, but GitHub analysis shows 0 Docker usage
    student = StudentProfile(
        name="Claimant",
        self_reported_skills=[SelfReportedSkill(name="Docker", level="Advanced")],
    )
    github = GitHubAnalysis(
        profile=GitHubProfileRaw(username="claimant", public_repos=3),
        activity=ActivitySummary(total_public_repos=3, non_fork_repos=3, repos_with_readme=3),
        languages=LanguageDistribution(primary_language="Python", language_repo_counts={"Python": 3}),
        technical_categories=[TechCategory(name="Docker", detected=False)],
        complexity_analyses=[],
        strengths=[], gaps=[], technical_patterns=[], recommendations=[], evidence_summary="",
    )

    profile = profile_engine.build_profile(
        ProfileBuildRequest(student_profile=student, github_analysis=github)
    )

    analysis = gap_engine.analyze_gaps("Backend Developer", profile)

    docker_gap = next((s for s in analysis.skills if s.skill == "Docker"), None)
    assert docker_gap is not None
    # Check that discrepancy note appears in docker evidence
    assert any("Discrepancy" in ev or "0 public GitHub" in ev for ev in docker_gap.evidence)


# ---------------------------------------------------------------------------
# Test 6: API Endpoint POST /api/ai/skills/analyze
# ---------------------------------------------------------------------------

def test_api_skills_analyze_endpoint(client):
    payload = {
        "target_role": "Backend Developer",
        "profile": {},
    }

    response = client.post("/api/ai/skills/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "target_role" in data
    assert data["target_role"] == "Backend Developer"
    assert "skills" in data
    assert "high_priority" in data
    assert "medium_priority" in data
    assert "low_priority" in data
    assert "summary" in data
    assert "evidence" in data
    assert len(data["skills"]) > 0
