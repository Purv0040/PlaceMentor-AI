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
        raw_analysis = GitHubAnalysis(
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

        return _validate_and_sanitize_analysis(raw_analysis)


def _validate_and_sanitize_analysis(analysis: GitHubAnalysis) -> GitHubAnalysis:
    """
    Validation and Sanitization Layer:
    Guarantees strict alignment between deterministic evidence, LLM narrative, and response schema.

    Enforces:
    1. Every detected=true category MUST have non-empty evidence list.
    2. If category.detected is false, evidence MUST be empty list.
    3. Strengths do not claim non-primary languages as primary, nor claim un-detected tech.
    4. Gaps do not claim missing tech that was actually detected as true.
    5. Recommendations match remaining gaps.
    6. Technical patterns and evidence summary do not mention un-detected frameworks (FastAPI, PyTorch, Docker, etc.).
    7. Complexity 'beginner' requires evidence; otherwise 'unknown'.
    """
    detected_names = {c.name for c in analysis.technical_categories if c.detected and c.evidence}

    # 1 & 2. Sanitize categories
    for cat in analysis.technical_categories:
        if cat.detected and not cat.evidence:
            cat.detected = False
            cat.evidence = []
        elif not cat.detected:
            cat.evidence = []

    # Un-detected tech keywords to scrub if hallucinated
    unsupported_techs = []
    if "Docker / Containerization" not in detected_names:
        unsupported_techs.extend(["docker", "containerized", "kubernetes", "k8s"])
    if "Machine Learning / AI" not in detected_names:
        unsupported_techs.extend(["pytorch", "tensorflow", "sklearn", "deep learning", "machine learning"])
    if "Backend / Server" not in detected_names:
        unsupported_techs.extend(["fastapi", "django", "flask", "express", "spring boot"])
    if "REST API" not in detected_names:
        unsupported_techs.extend(["rest api", "restful", "openapi", "swagger"])

    primary_lang = analysis.languages.primary_language

    # 3. Sanitize strengths
    sanitized_strengths = []
    for s in analysis.strengths:
        s_lower = s.lower()
        if "strong python" in s_lower and primary_lang != "Python":
            continue
        if any(tech in s_lower for tech in unsupported_techs):
            continue
        sanitized_strengths.append(s)

    if not sanitized_strengths:
        if primary_lang:
            sanitized_strengths.append(f"Demonstrated primary language proficiency in {primary_lang}.")
        else:
            sanitized_strengths.append("Active public GitHub profile with repository contributions.")

    # 4. Sanitize gaps
    sanitized_gaps = []
    for g in analysis.gaps:
        g_lower = g.lower()
        if ("docker" in g_lower or "container" in g_lower) and "Docker / Containerization" in detected_names:
            continue
        if ("ci/cd" in g_lower or "workflow" in g_lower or "devops" in g_lower) and "Deployment / DevOps" in detected_names:
            continue
        if ("testing" in g_lower or "test" in g_lower) and "Testing" in detected_names:
            continue
        if "database" in g_lower and "Database" in detected_names:
            continue
        sanitized_gaps.append(g)

    if not sanitized_gaps:
        if "Docker / Containerization" not in detected_names:
            sanitized_gaps.append("No containerization evidence (Docker/Dockerfile) detected in repository configurations.")
        if "Deployment / DevOps" not in detected_names:
            sanitized_gaps.append("No automated CI/CD workflows or cloud deployment manifests observed.")

    # 5. Sanitize recommendations
    sanitized_recs = []
    for r in analysis.recommendations:
        r_lower = r.lower()
        if ("docker" in r_lower or "container" in r_lower) and "Docker / Containerization" in detected_names:
            continue
        if ("ci/cd" in r_lower or "actions" in r_lower or "workflow" in r_lower) and "Deployment / DevOps" in detected_names:
            continue
        if ("unit test" in r_lower or "testing" in r_lower) and "Testing" in detected_names:
            continue
        sanitized_recs.append(r)

    if not sanitized_recs:
        if "Docker / Containerization" not in detected_names:
            sanitized_recs.append("Add a Dockerfile and docker-compose.yml to containerize core applications.")
        if "Deployment / DevOps" not in detected_names:
            sanitized_recs.append("Implement GitHub Actions workflows (.github/workflows) for automated linting and testing.")

    # 6. Sanitize technical patterns
    sanitized_patterns = []
    for tp in analysis.technical_patterns:
        tp_lower = tp.lower()
        if any(tech in tp_lower for tech in unsupported_techs):
            continue
        sanitized_patterns.append(tp)

    if not sanitized_patterns:
        if detected_names:
            sanitized_patterns.append(f"Architecture focus aligns with {', '.join(sorted(detected_names))}.")
        else:
            sanitized_patterns.append("General software development with standard repository organization.")

    # 7. Sanitize evidence summary
    summary = analysis.evidence_summary
    summary_lower = summary.lower()
    for tech in unsupported_techs:
        if tech in summary_lower:
            cat_summary = f"Detected technical domains include {', '.join(sorted(detected_names))}." if detected_names else "No specialized technical categories were detected."
            summary = f"GitHub portfolio for @{analysis.profile.username} features {primary_lang or 'general'} code. {cat_summary} Insights are strictly grounded in observable repository evidence."
            break

    # 8. Sanitize complexity analyses
    for ca in analysis.complexity_analyses:
        if ca.complexity_level == "beginner" and ca.evidence == ["No strong complexity signals detected"]:
            ca.complexity_level = "unknown"
            ca.confidence = "low"
            ca.evidence = ["Insufficient technical complexity signals detected"]

    analysis.strengths = sanitized_strengths
    analysis.gaps = sanitized_gaps
    analysis.technical_patterns = sanitized_patterns
    analysis.recommendations = sanitized_recs
    analysis.evidence_summary = summary

    return analysis
