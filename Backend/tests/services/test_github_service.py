import pytest
from unittest.mock import AsyncMock, patch
from app.services.github_service import GitHubService
from app.integrations.github_client import GitHubUserNotFoundError


@pytest.mark.asyncio
async def test_connect_github_success(mock_db):
    service = GitHubService(mock_db)
    mock_profile = {"login": "Purv0040", "name": "Purv Patel", "public_repos": 10}

    with patch.object(service.github_client, "get_user_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.return_value = mock_profile

        result = await service.connect_github("user_123", "Purv0040")
        assert result["github_username"] == "Purv0040"
        assert result["user_id"] == "user_123"


@pytest.mark.asyncio
async def test_connect_github_not_found(mock_db):
    service = GitHubService(mock_db)

    with patch.object(service.github_client, "get_user_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.side_effect = GitHubUserNotFoundError("User not found")

        with pytest.raises(Exception) as exc_info:
            await service.connect_github("user_123", "invalid_username_99999")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_sync_github_calculates_stats(mock_db):
    service = GitHubService(mock_db)
    user_id = "user_456"

    await service.repo.upsert_github_profile(user_id, "Purv0040")

    mock_profile = {"login": "Purv0040", "public_repos": 2}
    mock_repos = [
        {"repo_id": 1, "name": "r1", "language": "Python", "stars": 10, "forks": 2, "has_readme": True, "is_fork": False},
        {"repo_id": 2, "name": "r2", "language": "Python", "stars": 20, "forks": 5, "has_readme": True, "is_fork": False},
    ]

    with patch.object(service.github_client, "get_user_profile", new_callable=AsyncMock) as mock_get_profile, \
         patch.object(service.github_client, "get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_profile.return_value = mock_profile
        mock_get_repos.return_value = mock_repos

        synced = await service.sync_github(user_id)
        assert synced["statistics"]["total_stars"] == 30
        assert synced["statistics"]["total_repositories"] == 2
        assert synced["statistics"]["primary_language"] == "Python"
        assert synced["sync"]["status"] == "synced"
