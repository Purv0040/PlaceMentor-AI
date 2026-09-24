"""
Tests for GitHub Intelligence module.

All GitHub API calls are mocked — no network required.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.analyzers.github_analyzer import (
    build_activity_summary,
    build_language_distribution,
    detect_tech_categories,
    estimate_complexity,
)
from app.engines.github_engine import GitHubIntelligence
from app.schemas.github import (
    GitHubProfileRaw,
    GitHubRepoRaw,
    LLMGitHubInterpretation,
)
from app.services.github_service import (
    GitHubAPIError,
    GitHubRateLimitError,
    GitHubUserNotFoundError,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_repo(
    name: str,
    language: str = "Python",
    stars: int = 0,
    forks: int = 0,
    topics: list = None,
    description: str = "",
    is_fork: bool = False,
    size: int = 100,
    pushed_at: str = "2024-01-01T00:00:00Z",
) -> GitHubRepoRaw:
    return GitHubRepoRaw(
        name=name,
        description=description,
        language=language,
        languages={language: 10000} if language else {},
        stargazers_count=stars,
        forks_count=forks,
        topics=topics or [],
        has_readme=size > 0,
        fork=is_fork,
        updated_at=pushed_at,
        pushed_at=pushed_at,
        size=size,
    )


def _make_profile(repos: list = None, public_repos: int = None) -> GitHubProfileRaw:
    repos = repos or []
    return GitHubProfileRaw(
        username="testuser",
        name="Test User",
        bio="Developer",
        public_repos=public_repos if public_repos is not None else len(repos),
        followers=10,
        following=5,
        repositories=repos,
    )


MOCK_LLM_INTERPRETATION = LLMGitHubInterpretation(
    strengths=["Strong Python presence across multiple repositories."],
    gaps=["No frontend repositories detected."],
    technical_patterns=["Predominantly backend Python development."],
    recommendations=["Add a React or Vue project to demonstrate frontend skills."],
    evidence_summary=(
        "The portfolio contains 2 Python repositories with ML and API topics. "
        "No frontend or Docker usage was detected."
    ),
)


# ---------------------------------------------------------------------------
# Unit tests — deterministic analyzers (no mocking needed)
# ---------------------------------------------------------------------------

class TestTechCategoryDetection:
    def test_detects_ml_from_topics(self):
        repo = _make_repo("ml-project", topics=["machine-learning", "sklearn"])
        cats = detect_tech_categories([repo])
        ml_cat = next(c for c in cats if c.name == "Machine Learning / AI")
        assert ml_cat.detected is True
        assert "ml-project" in ml_cat.evidence

    def test_detects_docker_from_description(self):
        repo = _make_repo("my-app", description="A dockerized web application")
        cats = detect_tech_categories([repo])
        docker_cat = next(c for c in cats if c.name == "Docker / Containerization")
        assert docker_cat.detected is True

    def test_no_false_positive_for_empty_repo(self):
        repo = _make_repo("empty-repo", language="", description="", topics=[])
        cats = detect_tech_categories([repo])
        # ML / Docker should not be detected for an empty repo
        ml_cat = next(c for c in cats if c.name == "Machine Learning / AI")
        assert ml_cat.detected is False

    def test_detects_frontend_from_language(self):
        repo = _make_repo("portfolio", language="JavaScript")
        cats = detect_tech_categories([repo])
        fe_cat = next(c for c in cats if c.name == "Frontend")
        assert fe_cat.detected is True

    def test_different_technologies_repos(self):
        repos = [
            _make_repo("api-server", topics=["rest", "api", "postgresql"]),
            _make_repo("docker-app", description="Containerized with docker-compose"),
            _make_repo("ml-model", language="Jupyter Notebook", topics=["deep-learning"]),
        ]
        cats = detect_tech_categories(repos)
        detected_names = {c.name for c in cats if c.detected}
        assert "REST API" in detected_names
        assert "Docker / Containerization" in detected_names
        assert "Machine Learning / AI" in detected_names


class TestComplexityEstimator:
    def test_beginner_repo(self):
        repo = _make_repo("hello-world", description="My first project", size=10)
        results = estimate_complexity([repo])
        assert len(results) == 1
        assert results[0].complexity_level == "beginner"
        assert results[0].confidence in ("low", "medium")

    def test_intermediate_repo(self):
        repo = _make_repo(
            "web-app",
            topics=["rest", "api", "postgresql", "authentication"],
            description="A REST API with auth and database",
        )
        results = estimate_complexity([repo])
        assert results[0].complexity_level == "intermediate"

    def test_advanced_repo(self):
        repo = _make_repo(
            "ml-platform",
            topics=["machine-learning", "docker", "kubernetes", "ci", "auth"],
            description="ML platform with Docker, K8s and CI/CD",
            size=6000,
        )
        results = estimate_complexity([repo])
        assert results[0].complexity_level == "advanced"
        assert results[0].confidence in ("high", "medium")

    def test_forks_are_excluded(self):
        fork_repo = _make_repo("someone-elses-repo", is_fork=True)
        results = estimate_complexity([fork_repo])
        assert results == []

    def test_evidence_is_always_present(self):
        repo = _make_repo("empty-repo", language="", description="", topics=[])
        results = estimate_complexity([repo])
        assert len(results[0].evidence) >= 1  # always has at least a fallback


class TestActivityAndLanguage:
    def test_activity_summary(self):
        repos = [
            _make_repo("repo-a", stars=10, pushed_at="2024-05-01T00:00:00Z"),
            _make_repo("repo-b", stars=50, pushed_at="2024-01-01T00:00:00Z"),
            _make_repo("fork-repo", is_fork=True),
        ]
        profile = _make_profile(repos)
        activity = build_activity_summary(profile)
        assert activity.non_fork_repos == 2
        assert activity.total_stars == 60
        assert activity.most_starred_repo == "repo-b"
        assert activity.most_recent_push == "2024-05-01T00:00:00Z"

    def test_language_distribution(self):
        repos = [
            _make_repo("a", language="Python"),
            _make_repo("b", language="Python"),
            _make_repo("c", language="JavaScript"),
            _make_repo("d", is_fork=True, language="Go"),  # fork — excluded
        ]
        dist = build_language_distribution(repos)
        assert dist.primary_language == "Python"
        assert "Python" in dist.all_languages
        assert dist.language_repo_counts["Python"] == 2
        assert "Go" not in dist.language_repo_counts  # fork excluded

    def test_empty_repos(self):
        profile = _make_profile([])
        activity = build_activity_summary(profile)
        assert activity.total_stars == 0
        assert activity.most_starred_repo is None

        dist = build_language_distribution([])
        assert dist.primary_language is None


# ---------------------------------------------------------------------------
# Integration tests — GitHubIntelligence orchestrator (mocked)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_github_service_valid(monkeypatch):
    """Mock GitHubService.get_profile to return a predefined profile."""
    repos = [
        _make_repo("ml-project", language="Python", topics=["machine-learning"], stars=5),
        _make_repo("api-service", topics=["rest", "api", "postgresql"], description="REST API with auth"),
    ]
    profile = _make_profile(repos)

    monkeypatch.setattr(
        "app.services.github_service.GitHubService.get_profile",
        lambda self, username: profile,
    )


@pytest.fixture
def mock_github_service_empty(monkeypatch):
    """Mock GitHubService.get_profile to return a profile with no repos."""
    profile = _make_profile([])
    monkeypatch.setattr(
        "app.services.github_service.GitHubService.get_profile",
        lambda self, username: profile,
    )


@pytest.fixture
def mock_llm_github(monkeypatch):
    """Mock LLMService.generate_structured to return a canned interpretation."""
    monkeypatch.setattr(
        "app.services.llm_service.LLMService.generate_structured",
        lambda self, prompt, response_model, **kwargs: MOCK_LLM_INTERPRETATION,
    )


def test_github_intelligence_valid(mock_github_service_valid, mock_llm_github):
    engine = GitHubIntelligence()
    result = engine.analyze("testuser")

    assert result.profile.username == "testuser"
    assert result.activity.total_stars == 5
    assert len(result.technical_categories) > 0
    # ML category should be detected
    ml_cat = next((c for c in result.technical_categories if c.name == "Machine Learning / AI"), None)
    assert ml_cat is not None
    assert ml_cat.detected is True
    assert len(result.strengths) >= 1
    assert len(result.recommendations) >= 1


def test_github_intelligence_empty_repos(mock_github_service_empty, mock_llm_github):
    engine = GitHubIntelligence()
    result = engine.analyze("testuser")
    assert result.activity.total_stars == 0
    assert result.languages.primary_language is None
    # All categories should be undetected
    assert all(not c.detected for c in result.technical_categories)


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------

def test_api_github_analyze_valid(mock_github_service_valid, mock_llm_github):
    response = client.post("/api/ai/github/analyze", json={"username": "testuser"})
    assert response.status_code == 200
    data = response.json()
    assert data["profile"]["username"] == "testuser"
    assert "technical_categories" in data
    assert "strengths" in data
    assert "recommendations" in data


def test_api_github_analyze_not_found(monkeypatch):
    monkeypatch.setattr(
        "app.services.github_service.GitHubService.get_profile",
        lambda self, u: (_ for _ in ()).throw(GitHubUserNotFoundError(f"User '{u}' not found.")),
    )
    response = client.post("/api/ai/github/analyze", json={"username": "nonexistent_xyz_abc"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_api_github_analyze_rate_limit(monkeypatch):
    monkeypatch.setattr(
        "app.services.github_service.GitHubService.get_profile",
        lambda self, u: (_ for _ in ()).throw(GitHubRateLimitError("Rate limit exceeded.")),
    )
    response = client.post("/api/ai/github/analyze", json={"username": "someuser"})
    assert response.status_code == 429


def test_api_github_analyze_api_failure(monkeypatch):
    monkeypatch.setattr(
        "app.services.github_service.GitHubService.get_profile",
        lambda self, u: (_ for _ in ()).throw(GitHubAPIError("Connection failed.")),
    )
    response = client.post("/api/ai/github/analyze", json={"username": "someuser"})
    assert response.status_code == 502


def test_api_github_analyze_empty_username():
    response = client.post("/api/ai/github/analyze", json={"username": ""})
    assert response.status_code == 422  # Pydantic min_length validation
