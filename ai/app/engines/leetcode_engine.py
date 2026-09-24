"""
LeetCode Intelligence Orchestrator.

Pipeline:
  1. Fetch raw data via BaseLeetCodeProvider (provider-agnostic).
  2. Compute deterministic topic analysis (no LLM).
  3. Generate evidence-based recommendations (no LLM).
  4. Assemble and return a validated LeetCodeAnalysis.

The LLM is intentionally NOT used in this module because:
  - Topic performance is derived from a transparent rule table.
  - Recommendations are generated deterministically from observable signals.
  - LeetCode data is structured; narrative interpretation adds little value
    compared to the hallucination risk.
"""
import logging

from app.analyzers.leetcode_analyzer import (
    analyze_topics,
    build_difficulty_distribution,
    generate_recommendations,
)
from app.schemas.leetcode import (
    DataSourceStatus,
    LeetCodeAnalysis,
    LeetCodeProfileRaw,
    ProblemStatistics,
)
from app.services.leetcode_service import (
    BaseLeetCodeProvider,
    LeetCodeGraphQLProvider,
    LeetCodeRawBundle,
    LeetCodeUserNotFoundError,
    get_leetcode_provider,
)

logger = logging.getLogger(__name__)


class LeetCodeIntelligence:
    """
    Orchestrates the LeetCode analysis pipeline.

    Accepts an optional `provider` argument so tests can inject a mock without
    touching environment variables.
    """

    def __init__(self, provider: BaseLeetCodeProvider | None = None) -> None:
        self.provider: BaseLeetCodeProvider = provider or get_leetcode_provider()

    def analyze(self, username: str) -> LeetCodeAnalysis:
        """
        Run the full LeetCode intelligence pipeline.

        Raises:
            LeetCodeUserNotFoundError: if the username does not exist.
            LeetCodeAPIError: for connectivity / GraphQL errors.
        """
        logger.info(f"[LeetCodeIntelligence] Fetching data for '{username}'")
        bundle: LeetCodeRawBundle = self.provider.fetch_all(username)

        # Ensure we at least have a profile placeholder
        profile = bundle.profile or LeetCodeProfileRaw(username=username)
        stats   = bundle.stats  or ProblemStatistics()

        logger.info("[LeetCodeIntelligence] Running deterministic analysis...")

        topic_analyses = analyze_topics(bundle.topic_tags)
        difficulty_dist = build_difficulty_distribution(stats)
        recommendations = generate_recommendations(stats, topic_analyses)

        strong_topics = [t.topic for t in topic_analyses if t.performance_level == "strong"]
        weak_topics   = [
            t.topic for t in topic_analyses
            if t.performance_level in ("beginner", "untested")
        ]

        # Try contest data if the provider supports it
        contest = None
        if isinstance(self.provider, LeetCodeGraphQLProvider):
            try:
                contest = self.provider.fetch_contest_info(username)
                if contest:
                    bundle.status.contest_available = True
            except Exception as e:
                logger.warning(f"Contest fetch skipped: {e}")
                bundle.status.notes.append(f"Contest data unavailable: {e}")

        logger.info("[LeetCodeIntelligence] Assembling LeetCodeAnalysis...")
        return LeetCodeAnalysis(
            profile=profile,
            problem_statistics=stats,
            difficulty_distribution=difficulty_dist,
            topic_analysis=topic_analyses,
            strong_topics=strong_topics,
            weak_topics=weak_topics,
            contest=contest,
            recent_activity=bundle.recent_submissions,
            recommendations=recommendations,
            data_source_status=bundle.status,
        )
