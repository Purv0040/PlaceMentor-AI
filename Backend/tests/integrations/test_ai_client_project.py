import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.integrations.ai_client import AIClient, AIClientError


@pytest.mark.asyncio
async def test_analyze_project_success():
    client = AIClient(base_url="http://localhost:8001")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "score": 92,
        "score_badge": "Production Grade",
        "complexity_score": 90,
        "architecture_tags": ["Microservices", "REST API"],
        "evidence_bullets": ["Engineered PlaceMentor AI with sub-200ms latency."],
        "strengths": ["Solid full-stack architecture"],
        "weaknesses": ["Needs load testing documentation"],
        "recommendations": ["Add automated CI/CD pipeline"]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        payload = {
            "title": "PlaceMentor AI",
            "description": "Full-stack AI placement platform",
            "technologies": ["React", "FastAPI"]
        }
        result = await client.analyze_project(payload)
        assert result["score"] == 92
        assert result["score_badge"] == "Production Grade"
        assert "evidence_bullets" in result


@pytest.mark.asyncio
async def test_analyze_project_ai_error():
    client = AIClient(base_url="http://localhost:8001")
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with pytest.raises(AIClientError):
            await client.analyze_project({"title": "Test Proj"})
