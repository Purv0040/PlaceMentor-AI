import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.integrations.ai_client import AIClient, AIClientError

@pytest.mark.asyncio
async def test_ai_client_health_failure():
    client = AIClient(base_url="http://invalid-localhost:9999")
    healthy = await client.check_health()
    assert healthy is False

@pytest.mark.asyncio
async def test_ai_client_pdf_analysis_mocked():
    client = AIClient(base_url="http://localhost:8001")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "overall_score": 85,
        "ats_score": {"score": 85, "reason": "Good formatting"},
        "suggestions": ["Add Redis caching experience"]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        res = await client.analyze_resume_pdf(b"%PDF-1.4 test bytes")
        assert res["overall_score"] == 85
        assert "suggestions" in res
