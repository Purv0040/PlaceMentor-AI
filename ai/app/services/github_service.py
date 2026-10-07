"""
GitHub API client service.

All GitHub API interactions are isolated here so the rest of the application
never depends on GitHub API implementation details directly.

Caching hook: The `_cache` dict is intentionally simple (in-process TTL-free
dict) so it can be swapped for Redis / diskcache later without changing any
caller code.  Replace `_get_cached` / `_set_cached` to wire up a real cache.
"""
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from app.schemas.github import GitHubProfileRaw, GitHubRepoRaw

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class GitHubUserNotFoundError(Exception):
    """Raised when the requested GitHub user does not exist (HTTP 404)."""


class GitHubRateLimitError(Exception):
    """Raised when the GitHub API rate limit is exceeded (HTTP 403 / 429)."""


class GitHubAPIError(Exception):
    """Raised for any unexpected GitHub API errors."""


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class GitHubService:
    """
    Thin client for the GitHub REST API (v3).

    Usage::

        service = GitHubService()
        profile = await service.get_profile("torvalds")
    """

    BASE_URL = "https://api.github.com"
    MAX_REPOS_PER_PAGE = 100  # GitHub's maximum per page
    MAX_PAGES = 3             # Collect up to 300 repos to avoid excessive calls

    # In-process cache keyed by lowercase username
    _cache: Dict[str, GitHubProfileRaw] = {}

    def __init__(self) -> None:
        token = os.getenv("GITHUB_TOKEN", "")
        headers: Dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._headers = headers

    # ------------------------------------------------------------------
    # Cache helpers (swap these out for Redis etc.)
    # ------------------------------------------------------------------

    def _get_cached(self, username: str) -> Optional[GitHubProfileRaw]:
        return self._cache.get(username.lower())

    def _set_cached(self, username: str, profile: GitHubProfileRaw) -> None:
        self._cache[username.lower()] = profile

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _raise_for_github_status(self, response: httpx.Response, username: str) -> None:
        """Translate GitHub HTTP errors into meaningful exceptions."""
        if response.status_code == 404:
            raise GitHubUserNotFoundError(
                f"GitHub user '{username}' does not exist."
            )
        if response.status_code in (403, 429):
            reset = response.headers.get("X-RateLimit-Reset", "unknown")
            raise GitHubRateLimitError(
                f"GitHub API rate limit exceeded. Reset at epoch {reset}."
            )
        response.raise_for_status()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_profile(self, username: str) -> GitHubProfileRaw:
        """
        Collect a user's GitHub profile and their public repositories.

        Returns a cached result if one exists for this session.
        Raises GitHubUserNotFoundError, GitHubRateLimitError, GitHubAPIError.
        """
        cached = self._get_cached(username)
        if cached:
            logger.info(f"Cache hit for GitHub user '{username}'.")
            return cached

        logger.info(f"Fetching GitHub profile for '{username}'...")
        try:
            with httpx.Client(headers=self._headers, timeout=15.0) as client:
                profile_data = self._fetch_user(client, username)
                repos = self._fetch_repos(client, username)

                # Attach README detection & lightweight file evidence inside active client context
                repos_with_readme = self._mark_readme_presence(repos)
                repos_enriched = self._enrich_lightweight_evidence(client, username, repos_with_readme)

            profile = GitHubProfileRaw(
                username=profile_data.get("login", username),
                name=profile_data.get("name"),
                bio=profile_data.get("bio"),
                public_repos=profile_data.get("public_repos", 0),
                followers=profile_data.get("followers", 0),
                following=profile_data.get("following", 0),
                location=profile_data.get("location"),
                company=profile_data.get("company"),
                blog=profile_data.get("blog"),
                repositories=repos_enriched,
            )

            self._set_cached(username, profile)
            return profile

        except (GitHubUserNotFoundError, GitHubRateLimitError):
            raise
        except httpx.TimeoutException as e:
            raise GitHubAPIError(f"Timeout while fetching GitHub data: {e}")
        except httpx.HTTPStatusError as e:
            raise GitHubAPIError(f"HTTP error from GitHub API: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching GitHub data: {e}")
            raise GitHubAPIError(f"Unexpected error: {e}")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_user(self, client: httpx.Client, username: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/users/{username}"
        response = client.get(url)
        self._raise_for_github_status(response, username)
        return response.json()

    def _fetch_repos(self, client: httpx.Client, username: str) -> List[GitHubRepoRaw]:
        """Paginate through the user's public repos (up to MAX_PAGES pages)."""
        repos: List[GitHubRepoRaw] = []

        for page in range(1, self.MAX_PAGES + 1):
            url = f"{self.BASE_URL}/users/{username}/repos"
            params = {
                "per_page": self.MAX_REPOS_PER_PAGE,
                "page": page,
                "sort": "pushed",
                "direction": "desc",
            }
            response = client.get(url, params=params)
            self._raise_for_github_status(response, username)

            page_data: List[Dict] = response.json()
            if not page_data:
                break  # No more repos

            for raw in page_data:
                try:
                    repo = GitHubRepoRaw.model_validate(raw)
                    repos.append(repo)
                except Exception as e:
                    logger.warning(f"Could not parse repo '{raw.get('name')}': {e}")

            if len(page_data) < self.MAX_REPOS_PER_PAGE:
                break  # Last page

        return repos

    def _mark_readme_presence(self, repos: List[GitHubRepoRaw]) -> List[GitHubRepoRaw]:
        """
        README detection is expensive (one API call per repo), so we infer
        presence heuristically: repos with a size > 0 are assumed to potentially
        have one.  A real implementation could batch-check using the contents API.
        We set has_readme = True for non-empty repos as a conservative default.
        """
        for repo in repos:
            repo.has_readme = repo.size > 0
        return repos

    def _enrich_lightweight_evidence(
        self,
        client: httpx.Client,
        username: str,
        repos: List[GitHubRepoRaw]
    ) -> List[GitHubRepoRaw]:
        """
        Fetches full repository tree (Git Trees API), dependency signals, README signals,
        and code signals for top non-fork repositories.
        """
        non_forks = [r for r in repos if not r.is_fork][:10]  # Cap at top 10 most recent non-fork repos
        for repo in non_forks:
            file_signals: List[str] = []
            dependency_signals: List[str] = []
            readme_signals: List[str] = []
            code_signals: List[str] = []
            tree_items: List[Dict[str, Any]] = []
            branch = repo.default_branch or "main"

            # 1. Git Trees API call
            try:
                tree_url = f"{self.BASE_URL}/repos/{username}/{repo.name}/git/trees/{branch}?recursive=1"
                res = client.get(tree_url, timeout=6.0)

                # Fallback to master if main returned 404
                if res.status_code == 404 and branch != "master":
                    branch = "master"
                    tree_url = f"{self.BASE_URL}/repos/{username}/{repo.name}/git/trees/{branch}?recursive=1"
                    res = client.get(tree_url, timeout=6.0)

                if res.status_code == 200:
                    tree_data = res.json()
                    tree_items = tree_data.get("tree", [])
                else:
                    logger.error(
                        "GitHub API tree error repo=%s status=%s branch=%s response=%s",
                        repo.name, res.status_code, branch, res.text[:200]
                    )
            except Exception as e:
                logger.error("Failed to fetch git tree for repo=%s branch=%s error=%s", repo.name, branch, e)

            # 2. Extract file_signals from tree paths
            paths = [item.get("path", "") for item in tree_items]
            for path in paths:
                path_lower = path.lower()
                basename = path.split("/")[-1].lower()

                if basename in (
                    "dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yaml",
                    "package.json", "requirements.txt", "pyproject.toml", "pipfile",
                    "pom.xml", "build.gradle", "tsconfig.json", "angular.json",
                    "manage.py", "app.py", "main.py", "server.js", "vite.config.js",
                    "vite.config.ts", "next.config.js", "next.config.mjs"
                ):
                    file_signals.append(basename)

                if ".github/workflows" in path_lower:
                    file_signals.append(".github/workflows")
                if "/components/" in path_lower or path_lower.startswith("src/components"):
                    file_signals.append("src/components")
                if "routes/" in path_lower or basename == "routes":
                    file_signals.append("routes/")
                if "controllers/" in path_lower or basename == "controllers":
                    file_signals.append("controllers/")
                if "models/" in path_lower or basename == "models":
                    file_signals.append("models/")
                if "tests/" in path_lower or "test/" in path_lower or basename.startswith("test_") or basename.endswith(".test.js") or basename.endswith(".spec.ts"):
                    file_signals.append("tests/")

            file_signals = list(dict.fromkeys(file_signals))

            # 3. Extract dependencies
            if any(f in file_signals for f in ["package.json", "requirements.txt", "pyproject.toml", "pipfile", "pom.xml"]):
                dep_signals = self._extract_dependencies(client, username, repo.name, branch, file_signals)
                dependency_signals.extend(dep_signals)

            # 4. Extract README signals
            if repo.has_readme or any("readme" in p.lower() for p in paths):
                r_signals = self._extract_readme_signals(client, username, repo.name, branch)
                readme_signals.extend(r_signals)

            # 5. Extract Code signals
            c_signals = self._extract_code_signals(paths, dependency_signals, file_signals)
            code_signals.extend(c_signals)

            repo.file_signals = file_signals
            repo.dependency_signals = list(dict.fromkeys(dependency_signals))
            repo.readme_signals = list(dict.fromkeys(readme_signals))
            repo.code_signals = list(dict.fromkeys(code_signals))

            logger.info(
                "GitHub evidence debug repo=%s branch=%s tree_items=%s file_signals=%s dep_signals=%s readme_signals=%s code_signals=%s",
                repo.name, branch, len(tree_items), repo.file_signals, repo.dependency_signals, repo.readme_signals, repo.code_signals
            )

        return repos

    def _extract_dependencies(
        self, client: httpx.Client, username: str, repo_name: str, branch: str, file_signals: List[str]
    ) -> List[str]:
        deps: List[str] = []
        raw_base = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}"

        if "package.json" in file_signals:
            try:
                res = client.get(f"{raw_base}/package.json", timeout=4.0)
                if res.status_code == 200:
                    pkg_data = res.json()
                    all_deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                    key_pkgs = ["react", "vue", "angular", "next", "express", "nestjs", "vite", "tailwindcss",
                                "mongodb", "mongoose", "prisma", "pg", "mysql2", "jest", "vitest", "cypress",
                                "jsonwebtoken", "passport", "bcrypt"]
                    for pkg in key_pkgs:
                        if pkg in all_deps:
                            deps.append(pkg)
            except Exception as e:
                logger.debug("Failed parsing package.json for %s: %s", repo_name, e)

        if "requirements.txt" in file_signals:
            try:
                res = client.get(f"{raw_base}/requirements.txt", timeout=4.0)
                if res.status_code == 200:
                    text = res.text.lower()
                    key_py = ["fastapi", "flask", "django", "uvicorn", "gunicorn", "scikit-learn", "sklearn",
                              "tensorflow", "torch", "pytorch", "pandas", "numpy", "pytest", "pymongo",
                              "sqlalchemy", "psycopg2", "python-jose", "passlib", "celery"]
                    for py_pkg in key_py:
                        if py_pkg in text:
                            deps.append(py_pkg)
            except Exception as e:
                logger.debug("Failed parsing requirements.txt for %s: %s", repo_name, e)

        return list(dict.fromkeys(deps))

    def _extract_readme_signals(
        self, client: httpx.Client, username: str, repo_name: str, branch: str
    ) -> List[str]:
        readme_techs: List[str] = []
        raw_base = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}"
        for fname in ["README.md", "readme.md", "README.MD"]:
            try:
                res = client.get(f"{raw_base}/{fname}", timeout=4.0)
                if res.status_code == 200:
                    content = res.text[:3000].lower()
                    tech_keywords = {
                        "react": "React", "vue": "Vue", "angular": "Angular", "next.js": "Next.js",
                        "fastapi": "FastAPI", "flask": "Flask", "django": "Django", "express": "Express",
                        "spring boot": "Spring Boot", "docker": "Docker", "kubernetes": "Kubernetes",
                        "mongodb": "MongoDB", "postgresql": "PostgreSQL", "mysql": "MySQL",
                        "pytorch": "PyTorch", "tensorflow": "TensorFlow", "scikit-learn": "scikit-learn",
                        "jwt": "JWT", "oauth": "OAuth", "pytest": "pytest", "jest": "Jest"
                    }
                    for kw, label in tech_keywords.items():
                        if kw in content:
                            readme_techs.append(label)
                    break
            except Exception as e:
                logger.debug("Failed reading README for %s: %s", repo_name, e)
        return list(dict.fromkeys(readme_techs))

    def _extract_code_signals(
        self, paths: List[str], dependency_signals: List[str], file_signals: List[str]
    ) -> List[str]:
        code_sigs: List[str] = []
        paths_lower = [p.lower() for p in paths]

        if any("react" in d for d in dependency_signals) or any(p.endswith(".jsx") or p.endswith(".tsx") for p in paths_lower):
            code_sigs.append("React UI components detected")
        if "fastapi" in dependency_signals or any("main.py" in f for f in file_signals):
            code_sigs.append("Python entry point detected")
        if "express" in dependency_signals or any("server.js" in f for f in file_signals):
            code_sigs.append("Node server entry point detected")
        if any("test" in p for p in paths_lower):
            code_sigs.append("Automated test suite files detected")

        return list(dict.fromkeys(code_sigs))
