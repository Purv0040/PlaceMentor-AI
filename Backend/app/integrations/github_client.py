import logging
import httpx
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    """Base exception for GitHub API client errors."""
    pass


class GitHubUserNotFoundError(GitHubClientError):
    """Exception raised when a GitHub username is not found."""
    pass


class GitHubRateLimitError(GitHubClientError):
    """Exception raised when GitHub API rate limits are hit."""
    pass


class GitHubAPIError(GitHubClientError):
    """Exception raised when GitHub API returns unexpected error."""
    pass


class GitHubAPIClient:
    """Async HTTP Client for interacting with the public GitHub REST API."""

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.GITHUB_API_URL).rstrip("/")
        self.token = token or settings.GITHUB_TOKEN

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Placement-Copilot-Backend/1.0"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch user profile metadata from GitHub API."""
        clean_user = username.strip().lstrip("@")
        url = f"{self.base_url}/users/{clean_user}"
        logger.info("Fetching GitHub profile for '%s' from %s", clean_user, url)

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url, headers=self._get_headers())
                
                if res.status_code == 404:
                    raise GitHubUserNotFoundError(f"GitHub user '{clean_user}' not found.")
                elif res.status_code == 429 or (res.status_code == 403 and "rate limit" in res.text.lower()):
                    raise GitHubRateLimitError("GitHub API rate limit exceeded. Please try again later.")
                elif res.status_code != 200:
                    raise GitHubAPIError(f"GitHub API error HTTP {res.status_code}: {res.text[:200]}")

                data = res.json()
                return {
                    "id": data.get("id"),
                    "login": data.get("login", clean_user),
                    "name": data.get("name"),
                    "avatar_url": data.get("avatar_url"),
                    "bio": data.get("bio"),
                    "company": data.get("company"),
                    "location": data.get("location"),
                    "blog": data.get("blog"),
                    "public_repos": data.get("public_repos", 0),
                    "followers": data.get("followers", 0),
                    "following": data.get("following", 0),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "html_url": data.get("html_url", f"https://github.com/{clean_user}")
                }
        except httpx.RequestError as e:
            logger.error("Network error fetching GitHub profile: %s", e)
            raise GitHubAPIError(f"GitHub API connection failed: {type(e).__name__}")
        except Exception as e:
            if isinstance(e, GitHubClientError):
                raise e
            logger.error("Unexpected error fetching GitHub profile: %s", e)
            raise GitHubAPIError(f"Failed to fetch GitHub profile: {str(e)}")

    async def get_user_repos(
        self,
        username: str,
        page: int = 1,
        per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch repositories for GitHub user with pagination."""
        clean_user = username.strip().lstrip("@")
        url = f"{self.base_url}/users/{clean_user}/repos?page={page}&per_page={per_page}&sort=pushed"
        logger.info("Fetching GitHub repos for '%s' (page %d)", clean_user, page)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.get(url, headers=self._get_headers())
                
                if res.status_code == 404:
                    raise GitHubUserNotFoundError(f"GitHub user '{clean_user}' not found.")
                elif res.status_code == 429 or (res.status_code == 403 and "rate limit" in res.text.lower()):
                    raise GitHubRateLimitError("GitHub API rate limit exceeded.")
                elif res.status_code != 200:
                    raise GitHubAPIError(f"GitHub API error HTTP {res.status_code}: {res.text[:200]}")

                raw_repos = res.json()
                if not isinstance(raw_repos, list):
                    return []

                parsed_repos: List[Dict[str, Any]] = []
                for repo in raw_repos:
                    parsed_repos.append({
                        "repo_id": repo.get("id"),
                        "name": repo.get("name", ""),
                        "full_name": repo.get("full_name", repo.get("name", "")),
                        "description": repo.get("description"),
                        "html_url": repo.get("html_url"),
                        "language": repo.get("language"),
                        "languages": {repo["language"]: 1000} if repo.get("language") else {},
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "topics": repo.get("topics", []),
                        "has_readme": bool(repo.get("has_readme", True)),
                        "is_fork": repo.get("fork", False),
                        "size": repo.get("size", 0),
                        "created_at": repo.get("created_at"),
                        "updated_at": repo.get("updated_at"),
                        "pushed_at": repo.get("pushed_at"),
                    })

                return parsed_repos
        except httpx.RequestError as e:
            logger.error("Network error fetching GitHub repositories: %s", e)
            raise GitHubAPIError(f"GitHub API connection failed: {type(e).__name__}")
        except Exception as e:
            if isinstance(e, GitHubClientError):
                raise e
            logger.error("Unexpected error fetching GitHub repos: %s", e)
            raise GitHubAPIError(f"Failed to fetch GitHub repositories: {str(e)}")


# Alias for backward compatibility with pre-existing integration exports
GitHubClient = GitHubAPIClient

