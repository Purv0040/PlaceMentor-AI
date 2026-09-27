import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.leetcode_service import LeetCodeService
from app.integrations.leetcode_client import LeetCodeUserNotFoundError, LeetCodeAPIError
from app.integrations.ai_client import AIClientError


@pytest.mark.asyncio
async def test_connect_leetcode_empty_username(mock_db):
    service = LeetCodeService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.connect_leetcode("user_1", "   ")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_connect_leetcode_user_not_found(mock_db):
    service = LeetCodeService(mock_db)
    with patch.object(service.leetcode_client, "get_user_profile", new_callable=AsyncMock) as mock_profile:
        mock_profile.side_effect = LeetCodeUserNotFoundError("User not found")
        with pytest.raises(HTTPException) as exc_info:
            await service.connect_leetcode("user_1", "invalid_lc_user_99")
        assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_connect_leetcode_success(mock_db):
    service = LeetCodeService(mock_db)
    mock_profile_data = {
        "username": "digisha_lc",
        "real_name": "Digisha",
        "avatar_url": "https://lc.com/avatar.jpg"
    }

    with patch.object(service.leetcode_client, "get_user_profile", new_callable=AsyncMock) as mock_profile:
        mock_profile.return_value = mock_profile_data
        res = await service.connect_leetcode("user_1", "@digisha_lc")
        assert res["leetcode_username"] == "digisha_lc"
        assert res["user_id"] == "user_1"


@pytest.mark.asyncio
async def test_sync_leetcode_not_connected(mock_db):
    service = LeetCodeService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.sync_leetcode("non_existent_user")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_sync_leetcode_success(mock_db):
    service = LeetCodeService(mock_db)
    user_id = "user_2"

    await service.repo.upsert_leetcode_profile(user_id, "digisha_lc", {"username": "digisha_lc"})

    with patch.object(service.leetcode_client, "get_user_profile", new_callable=AsyncMock) as mock_profile, \
         patch.object(service.leetcode_client, "get_solved_problems", new_callable=AsyncMock) as mock_solved, \
         patch.object(service.leetcode_client, "get_topic_tags", new_callable=AsyncMock) as mock_topics, \
         patch.object(service.leetcode_client, "get_contest_info", new_callable=AsyncMock) as mock_contest, \
         patch.object(service.leetcode_client, "get_recent_submissions", new_callable=AsyncMock) as mock_recent:

        mock_profile.return_value = {"username": "digisha_lc", "ranking": 5000}
        mock_solved.return_value = {"total_solved": 250, "easy_solved": 100, "medium_solved": 120, "hard_solved": 30}
        mock_topics.return_value = [{"tagName": "Array", "problemsSolved": 50}]
        mock_contest.return_value = {"rating": 1750.0}
        mock_recent.return_value = [{"title": "Two Sum"}]

        res = await service.sync_leetcode(user_id)
        assert res["statistics"]["total_solved"] == 250
        assert res["sync"]["status"] == "synced"


@pytest.mark.asyncio
async def test_analyze_leetcode_ai_error(mock_db):
    service = LeetCodeService(mock_db)
    user_id = "user_3"

    await service.repo.upsert_leetcode_profile(user_id, "digisha_lc", {"username": "digisha_lc"})
    await service.repo.update_sync_status(user_id, "synced", is_success=True)

    with patch.object(service.ai_client, "analyze_leetcode", new_callable=AsyncMock) as mock_ai:
        mock_ai.side_effect = AIClientError("AI service error")
        with pytest.raises(HTTPException) as exc_info:
            await service.analyze_leetcode(user_id)
        assert exc_info.value.status_code == 502
