"""Unit tests for LeetCode Client with mocked HTTP requests."""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from services.leetcode_client import LeetCodeClient
from utils.exceptions import LeetCodeUserNotFoundError, LeetCodeDataUnavailableError


def test_get_user_data_success():
    async def _test():
        client = LeetCodeClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "matchedUser": {
                    "username": "tourist",
                    "submitStatsGlobal": {
                        "acSubmissionNum": [
                            {"difficulty": "All", "count": 400}
                        ]
                    }
                },
                "userContestRanking": {"rating": 1900}
            }
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            data = await client.get_user_data("tourist")
            assert data["matchedUser"]["username"] == "tourist"

    asyncio.run(_test())


def test_get_user_data_not_found():
    async def _test():
        client = LeetCodeClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "That user does not exist."}],
            "data": {"matchedUser": None}
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            with pytest.raises(LeetCodeUserNotFoundError):
                await client.get_user_data("nonexistent_user_999")

    asyncio.run(_test())
