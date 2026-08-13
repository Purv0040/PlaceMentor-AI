"""GitHub API client abstraction for fetching public GitHub data using httpx."""

import base64
from typing import Dict, List, Optional, Any
import httpx

from config import settings
from utils.constants import GITHUB_API_BASE_URL
from utils.exceptions import GitHubUserNotFoundError, GitHubRateLimitError, GitHubAPIError
from utils.logger import logger


class GitHubClient:
    """HTTP client for interacting with the official GitHub REST API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PlaceMentor-AI-GitHub-Analyzer/1.0"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _handle_error_status(self, response: httpx.Response, username: str) -> None:
        """Parse HTTP error statuses and raise explicit domain exceptions."""
        if response.status_code == 404:
            raise GitHubUserNotFoundError(username=username)
        elif response.status_code in (403, 429):
            rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
            if rate_limit_remaining == "0" or response.status_code == 429:
                raise GitHubRateLimitError()
            raise GitHubAPIError(
                message=f"GitHub API access forbidden: {response.text}",
                status_code=response.status_code
            )
        elif response.status_code >= 400:
            raise GitHubAPIError(
                message=f"GitHub API returned error HTTP {response.status_code}: {response.text}",
                status_code=response.status_code
            )

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch public profile details for a given GitHub username."""
        url = f"{GITHUB_API_BASE_URL}/users/{username}"
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                res = await client.get(url)
                if res.status_code != 200:
                    self._handle_error_status(res, username)
                return res.json()
            except httpx.RequestError as exc:
                logger.error(f"Network error fetching GitHub profile for {username}: {exc}")
                raise GitHubAPIError(message=f"Network communication failure with GitHub API: {str(exc)}")

    async def get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Fetch all public repositories for a given GitHub username."""
        url = f"{GITHUB_API_BASE_URL}/users/{username}/repos?per_page=100&sort=updated"
        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            try:
                res = await client.get(url)
                if res.status_code != 200:
                    self._handle_error_status(res, username)
                return res.json()
            except httpx.RequestError as exc:
                logger.error(f"Network error fetching repositories for {username}: {exc}")
                raise GitHubAPIError(message=f"Network failure while fetching user repositories: {str(exc)}")

    async def get_repository_readme(self, username: str, repo_name: str) -> Optional[str]:
        """Fetch raw text content of a repository's README if available."""
        url = f"{GITHUB_API_BASE_URL}/repos/{username}/{repo_name}/readme"
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                res = await client.get(url)
                if res.status_code == 404:
                    return None
                if res.status_code != 200:
                    return None
                data = res.json()
                content_b64 = data.get("content", "")
                if content_b64:
                    decoded = base64.b64decode(content_b64.encode("utf-8")).decode("utf-8", errors="ignore")
                    return decoded
                return None
            except Exception as exc:
                logger.warning(f"Could not fetch README for {username}/{repo_name}: {exc}")
                return None

    async def get_user_events(self, username: str) -> List[Dict[str, Any]]:
        """Fetch recent public activity events for a given user."""
        url = f"{GITHUB_API_BASE_URL}/users/{username}/events/public?per_page=100"
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                res = await client.get(url)
                if res.status_code != 200:
                    return []
                return res.json()
            except Exception as exc:
                logger.warning(f"Could not fetch public activity events for {username}: {exc}")
                return []
