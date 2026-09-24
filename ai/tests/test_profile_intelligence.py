"""
Tests for Student Profile Intelligence Engine.
Validates multi-source triangulation, 14 categories normalization, conflict detection,
and graceful handling of partial and missing data sources.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.profile_engine import StudentProfileIntelligenceEngine
from app.schemas.skills import ProfileBuildRequest, StudentIntelligenceProfile
from app.schemas.student import StudentProfile, SelfReportedSkill
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
    return StudentProfileIntelligenceEngine()


@pytest.fixture
def sample_resume():
    return ResumeAnalysis(
        ats_score=ScoreDetail(score=82, reason="Solid formatting and metrics"),
        skills_score=ScoreDetail(score=85, reason="Good language and framework coverage"),
        projects_score=ScoreDetail(score=80, reason="Projects with metrics"),
        experience_score=ScoreDetail(score=75, reason="Internship experience"),
        formatting_score=ScoreDetail(score=90, reason="Standard sections present"),
        impact_score=ScoreDetail(score=80, reason="Clear action verbs"),
        overall_score=82,
        suggestions=["Add more quantitative metrics"],
        extracted_skills=ExtractedSkills(
            languages=["Python", "JavaScript", "SQL"],
            frameworks=["FastAPI", "React", "Docker"],
            tools=["Git", "PostgreSQL", "Linux"],
            other=["REST APIs"],
        ),
        education=[],
        experience=[],
        projects=[
            Project(
                name="E-Commerce API",
                description="Built RESTful microservice with FastAPI and PostgreSQL",
                technologies=["Python", "FastAPI", "PostgreSQL", "Docker"],
                bullets=["Handled 500 req/sec with 99.9% uptime"],
                has_metrics=True,
            ),
            Project(
                name="Portfolio Web App",
                description="Frontend dashboard in React",
                technologies=["React", "JavaScript", "CSS"],
                bullets=["Implemented dark mode and responsive layout"],
                has_metrics=False,
            ),
        ],
        certifications=["AWS Certified Cloud Practitioner"],
        achievements=["Dean's List 2024"],
        missing_sections=[],
        weak_bullets=[
            WeakBullet(
                original_bullet="Worked on website features",
                issues=["vague", "missing metrics"],
                suggestion="Developed user authentication and dashboard features in React",
                evidence_used=["React", "Portfolio Web App"],
            )
        ],
        repeated_words=[],
        generic_phrases=["hard worker"],
        keyword_gaps=["Kubernetes"],
    )


@pytest.fixture
def sample_github():
    return GitHubAnalysis(
        profile=GitHubProfileRaw(
            username="alexdev",
            name="Alex Dev",
            public_repos=6,
            followers=12,
            following=8,
        ),
        activity=ActivitySummary(
            total_public_repos=6,
            non_fork_repos=5,
            repos_with_readme=5,
            most_recent_push="2026-09-01T10:00:00Z",
            most_starred_repo="ecommerce-fastapi",
            most_starred_count=15,
            total_stars=22,
            total_forks=4,
        ),
        languages=LanguageDistribution(
            primary_language="Python",
            all_languages=["Python", "JavaScript", "TypeScript", "HTML"],
            language_repo_counts={"Python": 4, "JavaScript": 2, "TypeScript": 1},
        ),
        technical_categories=[
            TechCategory(name="REST API", detected=True, evidence=["ecommerce-fastapi"]),
            TechCategory(name="Docker", detected=True, evidence=["ecommerce-fastapi"]),
            TechCategory(name="Machine Learning", detected=False, evidence=[]),
        ],
        complexity_analyses=[
            ComplexityAnalysis(
                repo_name="ecommerce-fastapi",
                complexity_level="advanced",
                evidence=["Uses FastAPI, Docker, and PostgreSQL", "Full CRUD with JWT"],
                confidence="high",
            )
        ],
        strengths=["Consistent Python project depth"],
        gaps=["No CI/CD pipeline automation found"],
        technical_patterns=["Backend microservices with FastAPI"],
        recommendations=["Add GitHub Actions workflows"],
        evidence_summary="Active developer with solid Python and API background.",
    )


@pytest.fixture
def sample_leetcode():
    return LeetCodeAnalysis(
        profile=LeetCodeProfileRaw(username="alex_codes", ranking=120000),
        problem_statistics=ProblemStatistics(
            total_solved=145,
            easy_solved=50,
            medium_solved=85,
            hard_solved=10,
            acceptance_rate=68.5,
        ),
        difficulty_distribution=DifficultyDistribution(
            easy_pct=34.5,
            medium_pct=58.6,
            hard_pct=6.9,
        ),
        topic_analysis=[
            TopicAnalysis(
                topic="Arrays",
                solved_count=45,
                difficulty_breakdown={"Easy": 20, "Medium": 22, "Hard": 3},
                performance_level="strong",
                evidence=["45 problems solved with 25 at Medium+ difficulty"],
                confidence="high",
            ),
            TopicAnalysis(
                topic="Dynamic Programming",
                solved_count=28,
                difficulty_breakdown={"Easy": 5, "Medium": 18, "Hard": 5},
                performance_level="strong",
                evidence=["28 problems solved with 5 at Hard difficulty"],
                confidence="high",
            ),
            TopicAnalysis(
                topic="Trees",
                solved_count=18,
                difficulty_breakdown={"Easy": 8, "Medium": 10},
                performance_level="developing",
                evidence=["18 problems solved at Easy/Medium level"],
                confidence="medium",
            ),
            TopicAnalysis(
                topic="Graphs",
                solved_count=2,
                difficulty_breakdown={"Easy": 2},
                performance_level="beginner",
                evidence=["Only 2 Easy problems solved"],
                confidence="medium",
            ),
        ],
        strong_topics=["Arrays", "Dynamic Programming"],
        weak_topics=["Graphs"],
        recommendations=["Practice more Graph traversal problems"],
        data_source_status=DataSourceStatus(
            provider="LeetCodeGraphQL",
            profile_available=True,
            problems_available=True,
            topics_available=True,
        ),
    )


@pytest.fixture
def sample_student_profile():
    return StudentProfile(
        name="Alex Dev",
        email="alex@example.com",
        target_role="Backend Engineer",
        target_companies=["Google", "Uber", "Amazon"],
        graduation_year=2026,
        degree="B.Tech",
        branch="Computer Science",
        institution="Apex Engineering College",
        self_reported_skills=[
            SelfReportedSkill(name="Python", level="Advanced"),
            SelfReportedSkill(name="FastAPI", level="Intermediate"),
            SelfReportedSkill(name="PostgreSQL", level="Intermediate"),
            SelfReportedSkill(name="Docker", level="Intermediate"),
        ],
    )


# ---------------------------------------------------------------------------
# Test 1: Only Resume
# ---------------------------------------------------------------------------

def test_profile_intelligence_only_resume(engine, sample_resume):
    req = ProfileBuildRequest(resume_analysis=sample_resume)
    profile = engine.build_profile(req)

    assert isinstance(profile, StudentIntelligenceProfile)
    assert profile.source_status.resume_analysis is True
    assert profile.source_status.github_analysis is False
    assert profile.source_status.leetcode_analysis is False
    assert profile.source_status.student_profile is False
    assert profile.source_status.total_sources_provided == 1

    # Check 14 categories existence
    cats = profile.categories
    assert cats.programming.overall_level in ["Intermediate", "Advanced"]
    assert cats.resume.ats_score == 82
    assert cats.resume.overall_level == "Strong"
    assert cats.github.overall_level == "Untested"
    assert cats.projects.total_projects_detected == 2
    assert cats.projects.projects_with_metrics_count == 1
    assert cats.communication.bullet_clarity_score == 80

    # Check skills only have 'resume' source
    py_skill = next((s for s in profile.skills if s.skill == "Python"), None)
    assert py_skill is not None
    assert py_skill.source == ["resume"]
    assert 0.65 <= py_skill.confidence <= 0.75
    assert len(py_skill.evidence) > 0


# ---------------------------------------------------------------------------
# Test 2: Resume + GitHub
# ---------------------------------------------------------------------------

def test_profile_intelligence_resume_and_github(engine, sample_resume, sample_github):
    req = ProfileBuildRequest(resume_analysis=sample_resume, github_analysis=sample_github)
    profile = engine.build_profile(req)

    assert profile.source_status.resume_analysis is True
    assert profile.source_status.github_analysis is True
    assert profile.source_status.leetcode_analysis is False
    assert profile.source_status.total_sources_provided == 2

    # Multi-source skill confidence boost
    py_skill = next((s for s in profile.skills if s.skill == "Python"), None)
    assert py_skill is not None
    assert "github" in py_skill.source and "resume" in py_skill.source
    assert py_skill.confidence >= 0.88  # Boosted for dual verification
    assert any("4 analyzed GitHub" in ev for ev in py_skill.evidence)
    assert any("resume" in ev.lower() for ev in py_skill.evidence)

    # Projects aggregation
    assert profile.categories.projects.resume_projects_count == 2
    assert profile.categories.projects.github_repos_count == 5
    assert profile.categories.projects.total_projects_detected == 7

    # GitHub category populated
    assert profile.categories.github.username == "alexdev"
    assert profile.categories.github.overall_level == "Active"
    assert profile.categories.github.readme_coverage_pct > 80.0


# ---------------------------------------------------------------------------
# Test 3: All Sources Triangulation
# ---------------------------------------------------------------------------

def test_profile_intelligence_all_sources(engine, sample_resume, sample_github, sample_leetcode, sample_student_profile):
    req = ProfileBuildRequest(
        student_profile=sample_student_profile,
        resume_analysis=sample_resume,
        github_analysis=sample_github,
        leetcode_analysis=sample_leetcode,
    )
    profile = engine.build_profile(req)

    assert profile.source_status.total_sources_provided == 4
    assert profile.target_role == "Backend Engineer"
    assert profile.student_metadata["name"] == "Alex Dev"

    # DSA Category populated from LeetCode
    assert profile.categories.dsa.overall_level == "Advanced"
    assert any("145" in ev for ev in profile.categories.dsa.evidence)

    # DP skill verified from LeetCode
    dp_skill = next((s for s in profile.skills if s.skill == "Dynamic Programming"), None)
    assert dp_skill is not None
    assert "leetcode" in dp_skill.source
    assert dp_skill.current_level == "Advanced"
    assert any("28 LeetCode" in ev for ev in dp_skill.evidence)

    # Check overall readiness level
    assert profile.overall_readiness_level in ["Placement Ready", "Advanced"]
    assert len(profile.strengths) >= 2
    assert profile.executive_summary != ""


# ---------------------------------------------------------------------------
# Test 4: Conflict Handling
# ---------------------------------------------------------------------------

def test_profile_intelligence_conflict_detection(engine, sample_github, sample_leetcode):
    # Student claims "Advanced" in Kotlin and "Advanced" in Graphs,
    # but GitHub has 0 Kotlin and LeetCode has only 2 Easy Graph problems solved.
    conflicting_student = StudentProfile(
        name="Claimant",
        self_reported_skills=[
            SelfReportedSkill(name="Kotlin", level="Advanced"),
            SelfReportedSkill(name="Graphs", level="Advanced"),
        ],
    )

    req = ProfileBuildRequest(
        student_profile=conflicting_student,
        github_analysis=sample_github,  # GitHub has 0 Kotlin
        leetcode_analysis=sample_leetcode,  # LeetCode has 2 Easy Graphs (beginner rating)
    )

    profile = engine.build_profile(req)

    # Verify conflicts list is populated
    assert len(profile.conflicts) >= 2

    # Check Kotlin conflict
    kotlin_conflict = next((c for c in profile.conflicts if c.skill_or_topic == "Kotlin"), None)
    assert kotlin_conflict is not None
    assert "0 public GitHub repositories" in kotlin_conflict.conflict
    assert "student_profile" in kotlin_conflict.sources
    assert kotlin_conflict.resolution_rule != ""

    # Check Graphs conflict
    graphs_conflict = next((c for c in profile.conflicts if c.skill_or_topic == "Graphs"), None)
    assert graphs_conflict is not None
    assert "only 2 solved" in graphs_conflict.conflict.lower()
    assert graphs_conflict.severity == "high"

    # Check Kotlin normalized skill confidence was penalized
    kotlin_skill = next((s for s in profile.skills if s.skill == "Kotlin"), None)
    assert kotlin_skill is not None
    assert kotlin_skill.confidence <= 0.50  # Penalized due to conflict


# ---------------------------------------------------------------------------
# Test 5: Missing Sources / Empty Input
# ---------------------------------------------------------------------------

def test_profile_intelligence_missing_sources(engine):
    req = ProfileBuildRequest()
    profile = engine.build_profile(req)

    assert isinstance(profile, StudentIntelligenceProfile)
    assert profile.source_status.total_sources_provided == 0
    assert profile.overall_readiness_level == "Untested"
    assert len(profile.skills) == 0
    assert len(profile.conflicts) == 0

    # Verify all 14 categories handle empty data without error
    cats = profile.categories
    assert cats.programming.overall_level == "Not Detected"
    assert cats.dsa.overall_level == "Untested"
    assert cats.backend.overall_level == "Not Detected"
    assert cats.frontend.overall_level == "Not Detected"
    assert cats.machine_learning.overall_level == "Not Detected"
    assert cats.data_science.overall_level == "Not Detected"
    assert cats.databases.overall_level == "Not Detected"
    assert cats.devops.overall_level == "Not Detected"
    assert cats.cloud.overall_level == "Not Detected"
    assert cats.cs_fundamentals.overall_level == "Not Detected"
    assert cats.projects.overall_level == "Untested"
    assert cats.resume.overall_level == "Untested"
    assert cats.github.overall_level == "Untested"
    assert cats.communication.overall_level == "Untested"


# ---------------------------------------------------------------------------
# Test 6: API Endpoint POST /api/ai/profile/build
# ---------------------------------------------------------------------------

def test_api_profile_build_endpoint(client, sample_resume, sample_github, sample_leetcode, sample_student_profile):
    payload = {
        "student_profile": sample_student_profile.model_dump(),
        "resume_analysis": sample_resume.model_dump(),
        "github_analysis": sample_github.model_dump(),
        "leetcode_analysis": sample_leetcode.model_dump(),
    }

    response = client.post("/api/ai/profile/build", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "categories" in data
    assert "skills" in data
    assert "conflicts" in data
    assert "source_status" in data
    assert data["source_status"]["total_sources_provided"] == 4
    assert data["overall_readiness_level"] in ["Placement Ready", "Advanced"]

    # Check 14 categories present in JSON response
    cat_keys = [
        "programming", "dsa", "backend", "frontend", "machine_learning",
        "data_science", "databases", "devops", "cloud", "cs_fundamentals",
        "projects", "resume", "github", "communication"
    ]
    for k in cat_keys:
        assert k in data["categories"], f"Missing category {k} in API response"
