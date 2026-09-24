"""
GitHub Intelligence Orchestrator.

Wires together:
  GitHubService  →  raw API data
  github_analyzer  →  deterministic categorisation / scoring
  LLMService  →  narrative interpretation
  GitHubAnalysis  →  validated output
"""
import logging
from typing import List

from app.analyzers.github_analyzer import (
    build_activity_summary,
    build_language_distribution,
    detect_tech_categories,
    estimate_complexity,
)
from app.prompts.github_prompts import GITHUB_INTERPRETATION_PROMPT
from app.schemas.github import (
    ComplexityAnalysis,
    GitHubAnalysis,
    GitHubProfileRaw,
    LLMGitHubInterpretation,
    TechCategory,
)
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class GitHubIntelligence:
    """
    Orchestrates the full GitHub analysis pipeline.

    Pipeline:
        1. Fetch raw data via GitHubService (respects caching).
        2. Compute deterministic signals (categories, complexity, activity, langs).
        3. Feed structured summary to LLM for narrative interpretation.
        4. Assemble and return a validated GitHubAnalysis.
    """

    def __init__(self) -> None:
        self.github_service = GitHubService()
        self.llm_service = LLMService()

    def analyze(self, username: str) -> GitHubAnalysis:
        """
        Run the full GitHub intelligence pipeline for `username`.

        Raises:
            GitHubUserNotFoundError: if the user doesn't exist.
            GitHubRateLimitError: if the API rate limit is hit.
            GitHubAPIError: for other GitHub API failures.
            ValueError: if LLM structured output cannot be repaired.
        """
        # 1 — Collect raw data
        logger.info(f"[GitHubIntelligence] Fetching profile for '{username}'")
        profile: GitHubProfileRaw = self.github_service.get_profile(username)

        # 2 — Deterministic analysis (no LLM)
        logger.info("[GitHubIntelligence] Running deterministic analysis...")
        activity = build_activity_summary(profile)
        languages = build_language_distribution(profile.repositories)
        tech_categories: List[TechCategory] = detect_tech_categories(profile.repositories)
        complexity_analyses: List[ComplexityAnalysis] = estimate_complexity(profile.repositories)

        # 3 — LLM interpretation
        logger.info("[GitHubIntelligence] Requesting LLM interpretation...")
        detected_cats = [c for c in tech_categories if c.detected]
        cat_summary = "\n".join(
            f"  - {c.name}: {', '.join(c.evidence[:3])}" for c in detected_cats
        ) or "  None detected"

        complexity_summary = "\n".join(
            f"  - {ca.repo_name}: {ca.complexity_level} (confidence: {ca.confidence}) — {'; '.join(ca.evidence[:3])}"
            for ca in complexity_analyses[:10]  # cap to avoid huge prompts
        ) or "  No repositories analysed"

        prompt = GITHUB_INTERPRETATION_PROMPT.format(
            username=profile.username,
            public_repos=profile.public_repos,
            non_fork_repos=activity.non_fork_repos,
            total_stars=activity.total_stars,
            primary_language=languages.primary_language or "None detected",
            all_languages=", ".join(languages.all_languages) or "None",
            technical_categories=cat_summary,
            complexity_analyses=complexity_summary,
            most_recent_push=activity.most_recent_push or "Unknown",
            most_starred_repo=activity.most_starred_repo or "None",
            most_starred_count=activity.most_starred_count,
        )

        interpretation: LLMGitHubInterpretation = self.llm_service.generate_structured(
            prompt=prompt,
            response_model=LLMGitHubInterpretation,
            max_retries=3,
        )

        # 4 — Assemble final validated result
        logger.info("[GitHubIntelligence] Assembling GitHubAnalysis...")
        return GitHubAnalysis(
            profile=profile,
            activity=activity,
            languages=languages,
            technical_categories=tech_categories,
            complexity_analyses=complexity_analyses,
            strengths=interpretation.strengths,
            gaps=interpretation.gaps,
            technical_patterns=interpretation.technical_patterns,
            recommendations=interpretation.recommendations,
            evidence_summary=interpretation.evidence_summary,
        )
