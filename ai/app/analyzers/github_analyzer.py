"""
Rule-based analyzers for GitHub repository data.

These analyzers are fully deterministic — no LLM involved.
Every conclusion is backed by observable evidence (language name, topic tag,
description keyword) so results are transparent and reproducible.
"""
from typing import Dict, List

from app.schemas.github import (
    ActivitySummary,
    ComplexityAnalysis,
    GitHubProfileRaw,
    GitHubRepoRaw,
    LanguageDistribution,
    TechCategory,
)


# ---------------------------------------------------------------------------
# Technology detection rules
# ---------------------------------------------------------------------------

# Each entry: category name → (languages, topics/description keywords)
_CATEGORY_RULES: Dict[str, Dict[str, List[str]]] = {
    "Frontend": {
        "languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
        "keywords": ["react", "vue", "angular", "svelte", "next", "nuxt",
                     "frontend", "ui", "tailwind", "webpack", "vite"],
    },
    "Backend / Server": {
        "languages": ["Python", "Java", "Go", "Ruby", "PHP", "Rust", "C#", "Kotlin"],
        "keywords": ["backend", "server", "api", "fastapi", "django", "flask",
                     "express", "spring", "rails", "gin", "actix"],
    },
    "REST API": {
        "languages": [],
        "keywords": ["rest", "api", "restful", "openapi", "swagger", "graphql",
                     "endpoint", "routes", "crud"],
    },
    "Database": {
        "languages": ["SQL", "PLpgSQL"],
        "keywords": ["database", "sql", "postgresql", "mysql", "sqlite",
                     "mongodb", "redis", "orm", "prisma", "sqlalchemy"],
    },
    "Authentication": {
        "languages": [],
        "keywords": ["auth", "authentication", "authorization", "jwt", "oauth",
                     "login", "session", "passportjs", "keycloak"],
    },
    "Machine Learning / AI": {
        "languages": ["Jupyter Notebook", "Python"],
        "keywords": ["ml", "machine-learning", "deep-learning", "ai", "nlp",
                     "neural", "sklearn", "tensorflow", "pytorch", "keras",
                     "transformers", "llm", "gpt", "prediction", "classification"],
    },
    "Data Science": {
        "languages": ["Jupyter Notebook", "R", "Python"],
        "keywords": ["data-science", "analytics", "pandas", "numpy", "matplotlib",
                     "seaborn", "eda", "visualization", "dataset", "kaggle"],
    },
    "Deployment / DevOps": {
        "languages": ["Shell", "Dockerfile", "HCL"],
        "keywords": ["deployment", "devops", "ci", "cd", "kubernetes", "helm",
                     "terraform", "ansible", "heroku", "aws", "gcp", "azure",
                     "cloud", "pipeline"],
    },
    "Docker / Containerization": {
        "languages": [],
        "keywords": ["docker", "dockerfile", "container", "docker-compose",
                     "compose", "containerized"],
    },
    "Testing": {
        "languages": [],
        "keywords": ["test", "testing", "pytest", "unittest", "jest", "mocha",
                     "cypress", "selenium", "tdd", "bdd", "coverage"],
    },
    "Documentation": {
        "languages": ["Markdown"],
        "keywords": ["docs", "documentation", "readme", "wiki", "mkdocs",
                     "sphinx", "javadoc"],
    },
}


def _repo_signals(repo: GitHubRepoRaw) -> List[str]:
    """Collect all searchable text signals from a repository."""
    signals: List[str] = []
    if repo.language:
        signals.append(repo.language)
    signals.extend(repo.languages.keys())
    signals.extend(repo.topics)
    if repo.description:
        signals.extend(repo.description.lower().split())
    return [s.lower() for s in signals]


def _signals_match_keywords(signals: List[str], kw_set: set) -> bool:
    """
    Return True if any signal token is in the keyword set, OR
    if any keyword appears as a substring inside any signal token.
    This catches e.g. 'dockerized' matching keyword 'docker'.
    """
    for signal in signals:
        if signal in kw_set:
            return True
        for kw in kw_set:
            if kw in signal:
                return True
    return False


def detect_tech_categories(repos: List[GitHubRepoRaw]) -> List[TechCategory]:
    """
    Determine which technical categories are represented across all repositories.
    Returns one TechCategory per rule, with evidence populated.
    """
    categories: List[TechCategory] = []

    for category_name, rules in _CATEGORY_RULES.items():
        lang_set = {l.lower() for l in rules["languages"]}
        kw_set = set(rules["keywords"])
        evidence: List[str] = []

        for repo in repos:
            signals = _repo_signals(repo)
            matched = (
                any(s in lang_set for s in signals)
                or _signals_match_keywords(signals, kw_set)
            )
            if matched:
                evidence.append(repo.name)

        categories.append(
            TechCategory(
                name=category_name,
                detected=len(evidence) > 0,
                evidence=list(dict.fromkeys(evidence)),  # deduplicate, preserve order
            )
        )

    return categories


# ---------------------------------------------------------------------------
# Complexity estimator
# ---------------------------------------------------------------------------

# Signals -> (points awarded, human-readable label)
_COMPLEXITY_SIGNALS: List[tuple] = [
    ({"docker", "dockerfile", "container", "docker-compose", "compose"}, 2, "Uses Docker/containerisation"),
    ({"kubernetes", "k8s", "helm"}, 3, "Uses Kubernetes"),
    ({"ci", "cd", "github-actions", "pipeline", "workflow"}, 2, "CI/CD integration"),
    ({"auth", "authentication", "jwt", "oauth"}, 2, "Authentication system"),
    ({"database", "sql", "postgresql", "mysql", "mongodb", "redis", "orm"}, 2, "Database integration"),
    ({"rest", "api", "restful", "endpoint", "routes"}, 1, "REST API layer"),
    ({"ml", "machine-learning", "tensorflow", "pytorch", "sklearn"}, 3, "Machine learning components"),
    ({"microservice", "distributed", "kafka", "rabbitmq", "grpc"}, 3, "Distributed / microservice architecture"),
    ({"test", "pytest", "jest", "coverage", "tdd"}, 1, "Has automated tests"),
    ({"docs", "documentation", "readme", "wiki"}, 1, "Has documentation"),
]


def _score_repo(repo: GitHubRepoRaw) -> tuple:
    """Return (total_points, evidence_list) for a single repo."""
    signals = set(_repo_signals(repo))
    total = 0
    evidence: List[str] = []

    for kw_set, points, label in _COMPLEXITY_SIGNALS:
        if signals & kw_set:
            total += points
            evidence.append(label)

    # Bonus for size
    if repo.size > 5000:
        total += 1
        evidence.append("Large codebase (>5 MB)")

    return total, evidence


def _points_to_level_and_confidence(points: int, evidence_count: int) -> tuple:
    if points >= 7:
        level = "advanced"
        confidence = "high" if evidence_count >= 3 else "medium"
    elif points >= 3:
        level = "intermediate"
        confidence = "high" if evidence_count >= 2 else "medium"
    else:
        level = "beginner"
        confidence = "medium" if evidence_count >= 1 else "low"
    return level, confidence


def estimate_complexity(repos: List[GitHubRepoRaw]) -> List[ComplexityAnalysis]:
    """
    Return a ComplexityAnalysis for each non-fork repository.
    Only non-fork repos are analyzed to reflect the author's own work.
    """
    results: List[ComplexityAnalysis] = []

    for repo in repos:
        if repo.is_fork:
            continue

        points, evidence = _score_repo(repo)

        if not evidence:
            evidence = ["No strong complexity signals detected"]

        level, confidence = _points_to_level_and_confidence(points, len(evidence))

        results.append(
            ComplexityAnalysis(
                repo_name=repo.name,
                complexity_level=level,
                evidence=evidence,
                confidence=confidence,
            )
        )

    return results


# ---------------------------------------------------------------------------
# Activity & language aggregators
# ---------------------------------------------------------------------------

def build_activity_summary(profile: GitHubProfileRaw) -> ActivitySummary:
    repos = profile.repositories
    non_forks = [r for r in repos if not r.is_fork]
    with_readme = [r for r in repos if r.has_readme]

    most_recent = None
    if repos:
        pushed = [r.pushed_at for r in repos if r.pushed_at]
        if pushed:
            most_recent = sorted(pushed, reverse=True)[0]

    starred = sorted(repos, key=lambda r: r.stars, reverse=True)
    top = starred[0] if starred else None

    return ActivitySummary(
        total_public_repos=profile.public_repos,
        non_fork_repos=len(non_forks),
        repos_with_readme=len(with_readme),
        most_recent_push=most_recent,
        most_starred_repo=top.name if top else None,
        most_starred_count=top.stars if top else 0,
        total_stars=sum(r.stars for r in repos),
        total_forks=sum(r.forks for r in repos),
    )


def build_language_distribution(repos: List[GitHubRepoRaw]) -> LanguageDistribution:
    """Aggregate language usage from primary repo language."""
    lang_counts: Dict[str, int] = {}

    for repo in repos:
        if repo.is_fork:
            continue
        if repo.language:
            lang_counts[repo.language] = lang_counts.get(repo.language, 0) + 1

    if not lang_counts:
        return LanguageDistribution()

    primary = max(lang_counts, key=lang_counts.__getitem__)
    sorted_langs = sorted(lang_counts, key=lang_counts.__getitem__, reverse=True)

    return LanguageDistribution(
        primary_language=primary,
        all_languages=sorted_langs,
        language_repo_counts=lang_counts,
    )
