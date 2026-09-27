import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.integrations.leetcode_client import (
    LeetCodeAPIClient,
    LeetCodeUserNotFoundError,
    LeetCodeAPIError
)


@pytest.mark.asyncio
async def test_get_user_profile_success():
    client = LeetCodeAPIClient(endpoint_url="https://leetcode.com/graphql")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "matchedUser": {
                "username": "test_lc_user",
                "profile": {
                    "realName": "Test User",
                    "aboutMe": "DSA student",
                    "ranking": 54321,
                    "reputation": 100,
                    "userAvatar": "https://assets.leetcode.com/avatar.png"
                }
            }
        }
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        profile = await client.get_user_profile("test_lc_user")
        assert profile["username"] == "test_lc_user"
        assert profile["real_name"] == "Test User"
        assert profile["ranking"] == 54321


@pytest.mark.asyncio
async def test_get_user_profile_not_found():
    client = LeetCodeAPIClient(endpoint_url="https://leetcode.com/graphql")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "matchedUser": None
        }
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(LeetCodeUserNotFoundError):
            await client.get_user_profile("non_existent_lc_user_12345")


@pytest.mark.asyncio
async def test_get_solved_problems():
    client = LeetCodeAPIClient(endpoint_url="https://leetcode.com/graphql")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "matchedUser": {
                "username": "test_lc_user",
                "submitStats": {
                    "acSubmissionNum": [
                        {"difficulty": "All", "count": 100, "submissions": 200},
                        {"difficulty": "Easy", "count": 50, "submissions": 80},
                        {"difficulty": "Medium", "count": 40, "submissions": 90},
                        {"difficulty": "Hard", "count": 10, "submissions": 30}
                    ]
                }
            },
            "allQuestionsCount": [
                {"difficulty": "All", "count": 3000},
                {"difficulty": "Easy", "count": 800},
                {"difficulty": "Medium", "count": 1500},
                {"difficulty": "Hard", "count": 700}
            ]
        }
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        stats = await client.get_solved_problems("test_lc_user")
        assert stats["total_solved"] == 100
        assert stats["easy_solved"] == 50
        assert stats["medium_solved"] == 40
        assert stats["hard_solved"] == 10
        assert stats["acceptance_rate"] == 50.0
