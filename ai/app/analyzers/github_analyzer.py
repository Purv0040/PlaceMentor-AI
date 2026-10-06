"""
Rule-based analyzers for GitHub repository data.

These analyzers are fully deterministic — no LLM involved.
Every conclusion is backed by observable evidence (language name, topic tag,
description keyword) so results are transparent and reproducible.
"""
import re
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
        "languages": ["HTML"],  # Plain HTML/CSS app structure or explicit frontend frameworks/components
        "keywords": ["react", "vue", "angular", "svelte", "next", "nuxt", "nextjs", "nuxtjs",
                     "frontend", "portfolio", "tailwind", "webpack", "vite", "bootstrap", "jsx", "tsx", "src/components"],
    },
    "Backend / Server": {
        "languages": [],  # Python, Java, C#, Go alone DO NOT prove backend development without server/framework signals
        "keywords": ["backend", "fastapi", "django", "flask",
                     "express", "expressjs", "fastify", "spring", "springboot", "rails", "gin", "actix", "nest", "nestjs",
                     "server.js", "uvicorn", "gunicorn", "@restcontroller", "routes/", "routes", "controllers/", "controllers"],
    },
    "REST API": {
        "languages": [],
        "keywords": ["rest", "restful", "routes/", "routes", "controllers/", "controllers", "endpoints", "endpoint", "api route", "api routes",
                     "rest api", "restful api", "openapi", "swagger", "fastapi", "express", "flask", "django-rest-framework"],
    },
    "Database": {
        "languages": ["SQL", "PLpgSQL"],
        "keywords": ["database", "sql", "postgresql", "postgres", "mysql", "sqlite",
                     "mongodb", "mongo", "redis", "orm", "prisma", "sqlalchemy", "mongoose"],
    },
    "Authentication": {
        "languages": [],
        "keywords": ["auth", "authentication", "authorization", "jwt", "oauth", "keycloak", "passportjs", "passport"],
    },
    "Machine Learning / AI": {
        "languages": ["Jupyter Notebook"],  # Note: Python alone is NOT an ML indicator unless explicit ML keywords exist!
        "keywords": ["ml", "machine-learning", "deep-learning", "ai", "nlp",
                     "neural", "sklearn", "scikit-learn", "tensorflow", "pytorch", "keras",
                     "transformers", "llm", "gpt"],
    },
    "Data Science": {
        "languages": ["Jupyter Notebook", "R"],
        "keywords": ["data-science", "analytics", "pandas", "numpy", "matplotlib",
                     "seaborn", "eda", "visualization", "dataset", "kaggle"],
    },
    "Deployment / DevOps": {
        "languages": ["Shell", "Dockerfile", "HCL"],
        "keywords": ["devops", "ci-cd", "kubernetes", "k8s", "helm",
                     "terraform", "ansible", "heroku", "aws", "gcp", "azure",
                     "github-actions", ".github/workflows", "cloud-pipeline"],
    },
    "Docker / Containerization": {
        "languages": ["Dockerfile"],
        "keywords": ["docker", "dockerfile", "container", "docker-compose", "containerized"],
    },
    "Testing": {
        "languages": [],
        "keywords": ["tests/", "test/", "tests", "test", "testing", "pytest", "unittest", "jest", "vitest", "mocha", "cypress", "selenium", "tdd", "bdd", "code-coverage", "automated test suite files detected"],
    },
    "Documentation": {
        "languages": ["Markdown"],
        "keywords": ["documentation", "mkdocs", "sphinx", "javadoc"],
    },
}


def _repo_signals(repo: GitHubRepoRaw) -> List[str]:
    """Collect all searchable text signals from a repository as normalized sub-tokens."""
    tokens: List[str] = []

    # Repo name tokens
    if repo.name:
        name_lower = repo.name.lower()
        tokens.append(name_lower)
        if "-" in name_lower or "_" in name_lower:
            tokens.extend([t for t in re.split(r'[\-_]', name_lower) if t])

    if repo.language:
        tokens.append(repo.language.lower())
    for lang in repo.languages.keys():
        tokens.append(lang.lower())

    for topic in repo.topics:
        topic_lower = topic.lower()
        tokens.append(topic_lower)
        if "-" in topic_lower or "_" in topic_lower:
            tokens.extend([t for t in re.split(r'[\-_]', topic_lower) if t])

    if repo.description:
        desc_words = re.findall(r'[a-zA-Z0-9\-]+', repo.description.lower())
        for word in desc_words:
            tokens.append(word)
            if "-" in word and len(word) > 1:
                tokens.extend([w for w in word.split("-") if w])

    for f_sig in repo.file_signals:
        f_lower = f_sig.lower()
        tokens.append(f_lower)
        if "/" in f_lower or "." in f_lower or "-" in f_lower:
            tokens.extend([sub for sub in re.split(r'[/.\-_]', f_lower) if sub])

    for d_sig in getattr(repo, "dependency_signals", []):
        d_lower = d_sig.lower()
        tokens.append(d_lower)
        if "-" in d_lower or "_" in d_lower:
            tokens.extend([sub for sub in re.split(r'[\-_]', d_lower) if sub])

    for r_sig in getattr(repo, "readme_signals", []):
        r_lower = r_sig.lower()
        tokens.append(r_lower)

    for c_sig in getattr(repo, "code_signals", []):
        c_lower = c_sig.lower()
        tokens.append(c_lower)

    return tokens


def _signals_match_keywords(signals: List[str], kw_set: set) -> bool:
    """
    Return True if any signal token matches a keyword in kw_set.
    - Exact token match for any keyword.
    - Substring match for keywords with len >= 4 (e.g. 'docker' in 'dockerized').
    - Short keywords (len < 4 like 'ml', 'ai', 'ui', 'sql') require EXACT token matches
      so 'html' does NOT match 'ml' and 'detail' does NOT match 'ai'.
    """
    signal_set = set(signals)
    for kw in kw_set:
        kw_len = len(kw)
        if kw in signal_set:
            return True
        if kw_len >= 4:
            for signal in signals:
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
            lang_match = any(s in lang_set for s in signals)
            kw_match = _signals_match_keywords(signals, kw_set)

            if lang_match or kw_match:
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
    ({"ci", "cd", "github-actions", ".github/workflows", "pipeline", "workflow"}, 2, "CI/CD integration"),
    ({"auth", "authentication", "jwt", "oauth", "passport"}, 2, "Authentication system"),
    ({"database", "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "orm", "prisma", "sqlalchemy", "mongoose"}, 2, "Database integration"),
    ({"routes/", "routes", "controllers/", "controllers", "endpoints", "rest", "openapi", "swagger"}, 2, "Structured API routing layer"),
    ({"models/", "models", "schema", "schemas"}, 1, "Defined data models & schemas"),
    ({"server.js", "app.py", "main.py", "fastapi", "express", "flask", "django", "nestjs", "springboot", "uvicorn", "gunicorn"}, 2, "Server application entry point"),
    ({"src/components", "react", "vue", "angular", "svelte", "next", "vite", "jsx", "tsx"}, 2, "Structured frontend UI architecture"),
    ({"ml", "machine-learning", "tensorflow", "pytorch", "sklearn", "scikit-learn"}, 3, "Machine learning components"),
    ({"microservice", "distributed", "kafka", "rabbitmq", "grpc"}, 3, "Distributed / microservice architecture"),
    ({"tests/", "test/", "test", "tests", "pytest", "unittest", "jest", "vitest", "cypress", "coverage", "tdd", "automated test suite files detected"}, 2, "Has automated test suite"),
    ({"package.json", "requirements.txt", "pyproject.toml", "pipfile", "pom.xml", "build.gradle"}, 1, "Configured dependency management"),
    ({"vite.config.js", "vite.config.ts", "webpack", "next.config.js", "tsconfig.json"}, 1, "Custom build/bundler configuration"),
    ({"docs", "documentation", "readme", "wiki"}, 1, "Has documentation"),
]


def _score_repo(repo: GitHubRepoRaw) -> tuple:
    """Return (total_points, evidence_list) for a single repo based on architecture & engineering evidence."""
    signals = set(_repo_signals(repo))
    total = 0
    evidence: List[str] = []

    for kw_set, points, label in _COMPLEXITY_SIGNALS:
        if signals & kw_set or any(_signals_match_keywords(list(signals), {kw}) for kw in kw_set):
            total += points
            evidence.append(label)

    # Bonus for full-stack frontend + backend architecture in the same repo
    has_fe = _signals_match_keywords(list(signals), {"react", "vue", "angular", "svelte", "next", "vite", "src/components"})
    has_be = _signals_match_keywords(list(signals), {"server.js", "express", "fastapi", "flask", "django", "routes", "controllers"})
    if has_fe and has_be:
        total += 2
        evidence.append("Full-stack architecture (Frontend + Backend separation)")

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
    beginner_keywords = {"basic", "practice", "tutorial", "exercise", "assignment", "demo", "hello-world", "self-study"}

    for repo in repos:
        if repo.is_fork:
            continue

        signals = set(_repo_signals(repo))
        points, evidence = _score_repo(repo)

        is_explicit_beginner = bool(signals & beginner_keywords) or (repo.size > 0 and repo.size < 100 and not evidence)

        if points >= 7:
            level = "advanced"
            confidence = "high" if len(evidence) >= 3 else "medium"
        elif points >= 3:
            level = "intermediate"
            confidence = "high" if len(evidence) >= 2 else "medium"
        elif is_explicit_beginner or points >= 1:
            level = "beginner"
            confidence = "medium" if len(evidence) >= 1 else "low"
            if not evidence:
                evidence = ["Single-script or basic tutorial/practice codebase"]
        else:
            level = "unknown"
            confidence = "low"
            evidence = ["Insufficient technical complexity signals detected"]

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
