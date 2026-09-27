import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.integrations.ai_client import AIClient, AIClientError


@pytest.mark.asyncio
async def test_analyze_skill_gaps_success():
    """Verify successful AI client skill gap analysis call."""
    client = AIClient(base_url="http://localhost:8001")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "target_role": "Backend Developer",
        "summary": "AI summary of skill gaps",
        "skills": [
            {"skill": "Redis", "explanation": "Redis is required for caching.", "recommended_action": "Build Redis project"}
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await client.analyze_skill_gaps({"target_role": "Backend Developer", "profile": {}})
        assert result["target_role"] == "Backend Developer"
        assert "summary" in result


@pytest.mark.asyncio
async def test_analyze_skill_gaps_ai_error():
    """Verify that HTTP/AI error properly raises AIClientError."""
    client = AIClient(base_url="http://localhost:8001")
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal error"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        with pytest.raises(AIClientError):
            await client.analyze_skill_gaps({"target_role": "Backend Developer", "profile": {}})
