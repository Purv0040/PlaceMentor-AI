"""Unit tests for GitHub HTTP client abstraction with mocked HTTP requests."""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from services.github_client import GitHubClient
from utils.exceptions import GitHubUserNotFoundError, GitHubRateLimitError, GitHubAPIError


def test_get_user_profile_success():
    async def _test():
        client = GitHubClient(token="dummy_token")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "octocat",
            "name": "The Octocat",
            "public_repos": 10
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            profile = await client.get_user_profile("octocat")
            assert profile["login"] == "octocat"
            assert profile["name"] == "The Octocat"

    asyncio.run(_test())


def test_get_user_profile_not_found():
    async def _test():
        client = GitHubClient()
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            with pytest.raises(GitHubUserNotFoundError):
                await client.get_user_profile("nonexistent_user_12345")

    asyncio.run(_test())


def test_get_user_profile_rate_limited():
    async def _test():
        client = GitHubClient()
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.headers = {"X-RateLimit-Remaining": "0"}

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            with pytest.raises(GitHubRateLimitError):
                await client.get_user_profile("someuser")

    asyncio.run(_test())
