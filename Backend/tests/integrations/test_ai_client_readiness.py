import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.integrations.ai_client import AIClient, AIClientError


@pytest.mark.asyncio
async def test_calculate_readiness_success():
    client = AIClient(base_url="http://localhost:8001")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "target_role": "Backend Developer",
        "overall_score": 78,
        "overall_confidence": 0.85,
        "readiness_label": "Advanced",
        "strengths": ["Solid ATS score"],
        "key_gaps": ["Add System Design project"]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        payload = {"target_role": "Backend Developer"}
        result = await client.calculate_readiness(payload)
        assert result["overall_score"] == 78
        assert result["readiness_label"] == "Advanced"


@pytest.mark.asyncio
async def test_calculate_readiness_ai_error():
    client = AIClient(base_url="http://localhost:8001")
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal AI Error"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(AIClientError):
            await client.calculate_readiness({"target_role": "Backend Developer"})
