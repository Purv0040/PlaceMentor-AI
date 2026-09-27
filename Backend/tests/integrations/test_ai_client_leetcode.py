import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.integrations.ai_client import AIClient, AIClientError


@pytest.mark.asyncio
async def test_analyze_leetcode_success():
    client = AIClient(base_url="http://localhost:8001")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "profile": {"username": "digisha_prep", "ranking": 12000},
        "problem_statistics": {"total_solved": 342},
        "strong_topics": ["Arrays", "Trees"],
        "weak_topics": ["Dynamic Programming"],
        "recommendations": ["Solve more Medium DP problems"]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        result = await client.analyze_leetcode("digisha_prep")
        assert result["profile"]["username"] == "digisha_prep"
        assert "recommendations" in result


@pytest.mark.asyncio
async def test_analyze_leetcode_ai_error():
    client = AIClient(base_url="http://localhost:8001")
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error in AI microservice"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(AIClientError):
            await client.analyze_leetcode("digisha_prep")
