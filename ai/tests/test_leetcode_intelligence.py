"""
Tests for LeetCode Intelligence module.

All external calls are mocked — no network required.
"""
import pytest
from fastapi.testclient import TestClient

from app.analyzers.leetcode_analyzer import (
    CANONICAL_TOPICS,
    analyze_topics,
    build_difficulty_distribution,
    generate_recommendations,
)
from app.engines.leetcode_engine import LeetCodeIntelligence
from app.main import app
from app.schemas.leetcode import (
    DataSourceStatus,
    LeetCodeProfileRaw,
    ProblemStatistics,
    RecentSubmission,
)
from app.services.leetcode_service import (
    BaseLeetCodeProvider,
    LeetCodeAPIError,
    LeetCodeRawBundle,
    LeetCodeUserNotFoundError,
)

client = TestClient(app)


# ---------------------------------------------------------------------------
# Mock provider helpers
# ---------------------------------------------------------------------------


def _make_bundle(
    username: str = "testuser",
    total: int = 100,
    easy: int = 50,
    medium: int = 40,
    hard: int = 10,
    tags: list = None,
    recent: list = None,
    profile_ok: bool = True,
) -> LeetCodeRawBundle:
    bundle = LeetCodeRawBundle()
    bundle.status = DataSourceStatus(provider="MockProvider")

    if profile_ok:
        bundle.profile = LeetCodeProfileRaw(username=username, ranking=5000)
        bundle.status.profile_available = True

    bundle.stats = ProblemStatistics(
        total_solved=total,
        easy_solved=easy,
        medium_solved=medium,
        hard_solved=hard,
        total_questions=3000,
        easy_total=800,
        medium_total=1700,
        hard_total=500,
    )
    bundle.status.problems_available = True

    bundle.topic_tags = tags or []
    bundle.status.topics_available = bool(bundle.topic_tags)

    bundle.recent_submissions = recent or []
    bundle.status.recent_activity_available = bool(bundle.recent_submissions)

    return bundle


class MockProvider(BaseLeetCodeProvider):
    """Configurable mock that never hits the network."""

    def __init__(self, bundle: LeetCodeRawBundle | None = None, raise_exc=None):
        self._bundle = bundle
        self._raise = raise_exc

    def _maybe_raise(self):
        if self._raise:
            raise self._raise

    def fetch_profile(self, username: str) -> LeetCodeProfileRaw:
        self._maybe_raise()
        return self._bundle.profile

    def fetch_solved_problems(self, username: str) -> ProblemStatistics:
        self._maybe_raise()
        return self._bundle.stats

    def fetch_topic_data(self, username: str):
        self._maybe_raise()
        return self._bundle.topic_tags

    def fetch_recent_activity(self, username: str):
        self._maybe_raise()
        return self._bundle.recent_submissions

    def fetch_all(self, username: str) -> LeetCodeRawBundle:
        self._maybe_raise()
        return self._bundle


# ---------------------------------------------------------------------------
# Unit tests — deterministic topic analyzer
# ---------------------------------------------------------------------------


class TestAnalyzeTopics:
    def test_all_canonical_topics_present(self):
        """Every canonical topic must appear in the output, even with no data."""
        result = analyze_topics([])
        output_names = [t.topic for t in result]
        for topic in CANONICAL_TOPICS:
            assert topic in output_names

    def test_untested_when_no_data(self):
        result = analyze_topics([])
        for t in result:
            assert t.performance_level == "untested"
            assert t.confidence == "low"
            assert t.solved_count == 0

    def test_strong_with_many_solves(self):
        tags = [{"tagName": "Array", "slug": "array", "problemsSolved": 20, "tier": "fundamental"}]
        result = analyze_topics(tags)
        arrays = next(t for t in result if t.topic == "Arrays")
        # 20 solved but no medium/hard breakdown available → developing or strong
        assert arrays.solved_count == 20
        assert arrays.performance_level in ("developing", "strong")

    def test_beginner_with_few_solves(self):
        tags = [{"tagName": "Dynamic Programming", "slug": "dynamic-programming", "problemsSolved": 2, "tier": "advanced"}]
        result = analyze_topics(tags)
        dp = next(t for t in result if t.topic == "Dynamic Programming")
        assert dp.performance_level == "beginner"
        assert dp.solved_count == 2

    def test_slug_mapping_variants(self):
        """Linked-list slug variants should map to 'Linked Lists'."""
        tags = [{"tagName": "Linked List", "slug": "linked-list", "problemsSolved": 8, "tier": "fundamental"}]
        result = analyze_topics(tags)
        ll = next(t for t in result if t.topic == "Linked Lists")
        assert ll.solved_count == 8

    def test_evidence_always_populated(self):
        result = analyze_topics([])
        for t in result:
            assert len(t.evidence) >= 1


class TestDifficultyDistribution:
    def test_distribution_sums_to_100(self):
        stats = ProblemStatistics(
            total_solved=100, easy_solved=50, medium_solved=40, hard_solved=10
        )
        dist = build_difficulty_distribution(stats)
        total = dist.easy_pct + dist.medium_pct + dist.hard_pct
        assert abs(total - 100.0) < 0.5

    def test_zero_solved(self):
        stats = ProblemStatistics(total_solved=0)
        dist = build_difficulty_distribution(stats)
        assert dist.easy_pct == 0.0
        assert dist.medium_pct == 0.0
        assert dist.hard_pct == 0.0


class TestGenerateRecommendations:
    def test_zero_solved_recommends_start(self):
        stats = ProblemStatistics(total_solved=0)
        recs = generate_recommendations(stats, analyze_topics([]))
        assert any("Start solving" in r for r in recs)

    def test_no_hard_recommends_hard(self):
        stats = ProblemStatistics(
            total_solved=50, easy_solved=40, medium_solved=10, hard_solved=0
        )
        recs = generate_recommendations(stats, analyze_topics([]))
        assert any("Hard" in r for r in recs)

    def test_untested_topics_flagged(self):
        stats = ProblemStatistics(
            total_solved=50, easy_solved=30, medium_solved=15, hard_solved=5
        )
        recs = generate_recommendations(stats, analyze_topics([]))
        # All topics untested → should mention common interview topics
        assert any("No problems solved" in r or "common interview" in r.lower() for r in recs)


# ---------------------------------------------------------------------------
# Integration tests — LeetCodeIntelligence orchestrator
# ---------------------------------------------------------------------------


class TestLeetCodeIntelligence:
    def test_valid_profile(self):
        tags = [
            {"tagName": "Array", "slug": "array", "problemsSolved": 30, "tier": "fundamental"},
            {"tagName": "Dynamic Programming", "slug": "dynamic-programming", "problemsSolved": 12, "tier": "advanced"},
        ]
        bundle = _make_bundle(tags=tags, recent=[RecentSubmission(title="Two Sum")])
        engine = LeetCodeIntelligence(provider=MockProvider(bundle=bundle))
        result = engine.analyze("testuser")

        assert result.profile.username == "testuser"
        assert result.problem_statistics.total_solved == 100
        assert len(result.topic_analysis) == len(CANONICAL_TOPICS)
        assert result.data_source_status.problems_available is True
        assert len(result.recent_activity) == 1

    def test_empty_topics(self):
        bundle = _make_bundle(tags=[])
        engine = LeetCodeIntelligence(provider=MockProvider(bundle=bundle))
        result = engine.analyze("testuser")

        assert all(t.performance_level == "untested" for t in result.topic_analysis)
        assert result.data_source_status.topics_available is False
        assert len(result.weak_topics) == len(CANONICAL_TOPICS)

    def test_strong_and_weak_classification(self):
        tags = [
            {"tagName": "Array", "slug": "array", "problemsSolved": 30, "tier": "fundamental"},
        ]
        bundle = _make_bundle(tags=tags)
        engine = LeetCodeIntelligence(provider=MockProvider(bundle=bundle))
        result = engine.analyze("testuser")

        # Arrays should be in strong or developing; DP (0 solves) should be weak
        dp = next(t for t in result.topic_analysis if t.topic == "Dynamic Programming")
        assert dp.performance_level == "untested"
        assert "Dynamic Programming" in result.weak_topics

    def test_profile_unavailable(self):
        """When profile fails, we get a placeholder but no crash."""
        bundle = _make_bundle(profile_ok=False)
        engine = LeetCodeIntelligence(provider=MockProvider(bundle=bundle))
        result = engine.analyze("testuser")
        assert result.profile.username == "testuser"
        assert result.data_source_status.profile_available is False


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


def _mock_engine_analyze(bundle: LeetCodeRawBundle):
    """Patches LeetCodeIntelligence.analyze via monkeypatch."""
    tags = bundle.topic_tags

    def _analyze(self, username):
        from app.analyzers.leetcode_analyzer import (
            analyze_topics,
            build_difficulty_distribution,
            generate_recommendations,
        )
        from app.schemas.leetcode import LeetCodeAnalysis

        profile = bundle.profile or LeetCodeProfileRaw(username=username)
        stats = bundle.stats or ProblemStatistics()
        topic_analyses = analyze_topics(tags)
        return LeetCodeAnalysis(
            profile=profile,
            problem_statistics=stats,
            difficulty_distribution=build_difficulty_distribution(stats),
            topic_analysis=topic_analyses,
            strong_topics=[t.topic for t in topic_analyses if t.performance_level == "strong"],
            weak_topics=[t.topic for t in topic_analyses if t.performance_level in ("beginner", "untested")],
            recent_activity=bundle.recent_submissions,
            recommendations=generate_recommendations(stats, topic_analyses),
            data_source_status=bundle.status,
        )

    return _analyze


class TestLeetCodeAPIEndpoints:
    def test_valid_request(self, monkeypatch):
        bundle = _make_bundle()
        monkeypatch.setattr(
            "app.engines.leetcode_engine.LeetCodeIntelligence.analyze",
            _mock_engine_analyze(bundle),
        )
        resp = client.post("/api/ai/leetcode/analyze", json={"username": "testuser"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["username"] == "testuser"
        assert "topic_analysis" in data
        assert "data_source_status" in data
        assert len(data["topic_analysis"]) == len(CANONICAL_TOPICS)

    def test_not_found(self, monkeypatch):
        monkeypatch.setattr(
            "app.engines.leetcode_engine.LeetCodeIntelligence.analyze",
            lambda self, u: (_ for _ in ()).throw(
                LeetCodeUserNotFoundError(f"User '{u}' not found.")
            ),
        )
        resp = client.post("/api/ai/leetcode/analyze", json={"username": "ghost_xyz"})
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_api_failure(self, monkeypatch):
        monkeypatch.setattr(
            "app.engines.leetcode_engine.LeetCodeIntelligence.analyze",
            lambda self, u: (_ for _ in ()).throw(LeetCodeAPIError("Timeout")),
        )
        resp = client.post("/api/ai/leetcode/analyze", json={"username": "someuser"})
        assert resp.status_code == 502

    def test_empty_username_rejected(self):
        resp = client.post("/api/ai/leetcode/analyze", json={"username": ""})
        assert resp.status_code == 422

    def test_unavailable_data_still_returns_200(self, monkeypatch):
        """When topic and activity data are unavailable, we still return a valid response."""
        bundle = _make_bundle(tags=[], recent=[])
        monkeypatch.setattr(
            "app.engines.leetcode_engine.LeetCodeIntelligence.analyze",
            _mock_engine_analyze(bundle),
        )
        resp = client.post("/api/ai/leetcode/analyze", json={"username": "testuser"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["data_source_status"]["topics_available"] is False
        assert data["data_source_status"]["recent_activity_available"] is False
