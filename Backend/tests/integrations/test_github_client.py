import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.integrations.github_client import (
    GitHubAPIClient,
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError
)


@pytest.mark.asyncio
async def test_github_client_get_user_profile_success():
    client = GitHubAPIClient()
    mock_resp = httpx.Response(200, json={
        "id": 123,
        "login": "testuser",
        "name": "Test User",
        "public_repos": 10
    })

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        res = await client.get_user_profile("testuser")
        assert res["login"] == "testuser"
        assert res["public_repos"] == 10


@pytest.mark.asyncio
async def test_github_client_user_not_found():
    client = GitHubAPIClient()
    mock_resp = httpx.Response(404, json={"message": "Not Found"})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        with pytest.raises(GitHubUserNotFoundError):
            await client.get_user_profile("nonexistent_user_9999")
