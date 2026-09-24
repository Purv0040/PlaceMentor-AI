"""
Tests for Placement Readiness Engine.
Validates 7 category scoring, configurable weighting system, status & confidence tracking,
insufficient data handling, historical snapshots, and deterministic arithmetic.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.readiness_engine import PlacementReadinessEngine
from app.schemas.readiness import (
    PlacementReadinessAnalysis,
    ReadinessCalculateRequest,
    ReadinessWeights,
)
from app.schemas.resume import (
    ExtractedSkills,
    LLMResumeExtraction,
    Project,
    ResumeAnalysis,
    ScoreDetail,
    WeakBullet,
)
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


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return PlacementReadinessEngine()


@pytest.fixture
def sample_resume():
    return ResumeAnalysis(
        ats_score=ScoreDetail(score=85, reason="Good ATS"),
        skills_score=ScoreDetail(score=90, reason="Good skills"),
        projects_score=ScoreDetail(score=85, reason="Good projects"),
        experience_score=ScoreDetail(score=80, reason="Intern experience"),
        formatting_score=ScoreDetail(score=90, reason="Clean"),
        impact_score=ScoreDetail(score=85, reason="Clear bullets"),
        overall_score=86,
        suggestions=[],
        extracted_skills=ExtractedSkills(
            languages=["Python", "C++"],
            frameworks=["FastAPI", "React"],
            tools=["Docker", "Git", "PostgreSQL"],
            other=["Operating Systems", "DBMS", "Computer Networks", "OOP"],
        ),
        education=[],
        experience=[],
        projects=[
            Project(
                name="Cloud API Service",
                description="Backend REST microservice",
                technologies=["Python", "FastAPI", "Docker"],
                bullets=["Handled 1000 req/sec with 99.9% uptime"],
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


@pytest.fixture
def sample_github():
    return GitHubAnalysis(
        profile=GitHubProfileRaw(username="pro_dev", public_repos=6),
        activity=ActivitySummary(
            total_public_repos=6,
            non_fork_repos=5,
            repos_with_readme=5,
            most_starred_count=10,
            total_stars=15,
        ),
        languages=LanguageDistribution(
            primary_language="Python",
            all_languages=["Python", "C++"],
            language_repo_counts={"Python": 4, "C++": 2},
        ),
        technical_categories=[
            TechCategory(name="Docker", detected=True, evidence=["api-repo"]),
            TechCategory(name="REST API", detected=True, evidence=["api-repo"]),
        ],
        complexity_analyses=[
            ComplexityAnalysis(
                repo_name="api-repo",
                complexity_level="advanced",
                evidence=["Uses Docker and FastAPI"],
                confidence="high",
            )
        ],
        strengths=[], gaps=[], technical_patterns=[], recommendations=[], evidence_summary="",
    )


@pytest.fixture
def sample_leetcode():
    return LeetCodeAnalysis(
        profile=LeetCodeProfileRaw(username="pro_lc"),
        problem_statistics=ProblemStatistics(
            total_solved=160,
            easy_solved=50,
            medium_solved=95,
            hard_solved=15,
        ),
        difficulty_distribution=DifficultyDistribution(easy_pct=31, medium_pct=59, hard_pct=10),
        topic_analysis=[
            TopicAnalysis(topic="Arrays", solved_count=50, performance_level="strong", evidence=["50 solved"], confidence="high"),
            TopicAnalysis(topic="Dynamic Programming", solved_count=30, performance_level="strong", evidence=["30 solved"], confidence="high"),
        ],
        strong_topics=["Arrays", "Dynamic Programming"],
        data_source_status=DataSourceStatus(provider="LeetCodeGraphQL", problems_available=True),
    )


@pytest.fixture
def sample_interview():
    return {
        "sessions_count": 2,
        "average_rating": 85,
        "technical_score": 88,
        "behavioral_score": 82,
    }


# ---------------------------------------------------------------------------
# Test 1: Complete Profile (All 7 Categories Scored)
# ---------------------------------------------------------------------------

def test_readiness_complete_profile(engine, sample_resume, sample_github, sample_leetcode, sample_interview):
    req = ReadinessCalculateRequest(
        target_role="Backend Developer",
        resume_analysis=sample_resume,
        github_analysis=sample_github,
        leetcode_analysis=sample_leetcode,
        interview_data=sample_interview,
    )

    res = engine.calculate_readiness(req)

    assert isinstance(res, PlacementReadinessAnalysis)
    assert res.target_role == "Backend Developer"
    assert res.scored_categories_count == 7
    assert res.insufficient_categories_count == 0
    assert res.overall_score is not None
    assert 75 <= res.overall_score <= 98
    assert res.overall_confidence >= 0.80
    assert res.readiness_label in ["Placement Ready", "Advanced"]

    # Verify all 7 categories are 'scored'
    for cat_name, cat_obj in res.categories.items():
        assert cat_obj.status == "scored"
        assert cat_obj.score is not None
        assert cat_obj.confidence > 0.0
        assert len(cat_obj.evidence) > 0

    # Verify normalized weights sum to ~1.0
    total_weights = sum(res.weights_used.values())
    assert abs(total_weights - 1.0) < 0.01

    # Verify historical snapshot structure
    snapshot = res.historical_snapshot
    assert snapshot.overall_score == res.overall_score
    assert snapshot.overall_confidence == res.overall_confidence
    assert len(snapshot.category_scores) == 7


# ---------------------------------------------------------------------------
# Test 2: Partial Profile (Missing LeetCode & Interview Data)
# ---------------------------------------------------------------------------

def test_readiness_partial_profile(engine, sample_resume, sample_github):
    req = ReadinessCalculateRequest(
        target_role="Backend Developer",
        resume_analysis=sample_resume,
        github_analysis=sample_github,
        leetcode_analysis=None,
        interview_data=None,
    )

    res = engine.calculate_readiness(req)

    assert res.insufficient_categories_count >= 1
    assert res.categories["Interview"].status == "insufficient_data"
    assert res.categories["Interview"].score is None
    assert res.categories["Interview"].confidence == 0.0

    # Overall score should still be calculated from available categories
    assert res.overall_score is not None
    assert "Interview" not in res.weights_used

    # Weights of scored categories should be re-normalized to sum to 1.0
    total_weights = sum(res.weights_used.values())
    assert abs(total_weights - 1.0) < 0.01


# ---------------------------------------------------------------------------
# Test 3: Missing Communication Data
# ---------------------------------------------------------------------------

def test_readiness_missing_communication_data(engine):
    # Empty request without resume or github documentation
    req = ReadinessCalculateRequest(
        target_role="Backend Developer",
        resume_analysis=None,
        github_analysis=None,
    )

    res = engine.calculate_readiness(req)

    comm_cat = res.categories["Communication"]
    assert comm_cat.status == "insufficient_data"
    assert comm_cat.score is None
    assert comm_cat.confidence == 0.0
    assert "No resume bullet points or GitHub README" in comm_cat.evidence[0]


# ---------------------------------------------------------------------------
# Test 4: Missing Interview Data
# ---------------------------------------------------------------------------

def test_readiness_missing_interview_data(engine, sample_resume):
    req = ReadinessCalculateRequest(
        target_role="Backend Developer",
        resume_analysis=sample_resume,
        interview_data=None,
    )

    res = engine.calculate_readiness(req)

    interview_cat = res.categories["Interview"]
    assert interview_cat.status == "insufficient_data"
    assert interview_cat.score is None
    assert interview_cat.confidence == 0.0
    assert any("No mock interview" in ev for ev in interview_cat.evidence)


# ---------------------------------------------------------------------------
# Test 5: Custom Weighting Configuration
# ---------------------------------------------------------------------------

def test_readiness_custom_weights(engine, sample_resume, sample_leetcode):
    # Heavy DSA weight (50% DSA, 50% Resume)
    custom_weights = ReadinessWeights(
        resume=0.50,
        dsa=0.50,
        projects=0.0,
        github=0.0,
        cs_fundamentals=0.0,
        communication=0.0,
        interview=0.0,
    )

    req = ReadinessCalculateRequest(
        target_role="Backend Developer",
        weights=custom_weights,
        resume_analysis=sample_resume,
        leetcode_analysis=sample_leetcode,
    )

    res = engine.calculate_readiness(req)

    assert "Resume" in res.weights_used
    assert "DSA" in res.weights_used
    assert abs(res.weights_used["Resume"] - 0.50) < 0.05
    assert abs(res.weights_used["DSA"] - 0.50) < 0.05

    # Check deterministic calculation
    expected_score = int(round(0.50 * res.categories["Resume"].score + 0.50 * res.categories["DSA"].score))
    assert abs(res.overall_score - expected_score) <= 1


# ---------------------------------------------------------------------------
# Test 6: API Endpoint POST /api/ai/readiness/calculate
# ---------------------------------------------------------------------------

def test_api_readiness_calculate_endpoint(client, sample_resume, sample_github, sample_leetcode):
    payload = {
        "target_role": "Backend Developer",
        "weights": {
            "resume": 0.20,
            "dsa": 0.30,
            "projects": 0.20,
            "github": 0.10,
            "cs_fundamentals": 0.10,
            "communication": 0.05,
            "interview": 0.05,
        },
        "resume_analysis": sample_resume.model_dump(),
        "github_analysis": sample_github.model_dump(),
        "leetcode_analysis": sample_leetcode.model_dump(),
    }

    response = client.post("/api/ai/readiness/calculate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "target_role" in data
    assert data["target_role"] == "Backend Developer"
    assert "overall_score" in data
    assert "overall_confidence" in data
    assert "categories" in data
    assert len(data["categories"]) == 7
    assert "historical_snapshot" in data
    assert "scoring_formula_explanation" in data
