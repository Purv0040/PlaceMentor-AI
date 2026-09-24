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

            # Attach README detection
            repos_with_readme = self._mark_readme_presence(repos)

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
                repositories=repos_with_readme,
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
