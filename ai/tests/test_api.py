from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-placement-copilot"
    }

def test_ai_test_endpoint():
    response = client.post(
        "/api/ai/test",
        json={"message": "Hello AI"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "reply" in data
    assert data["original_message"] == "Hello AI"
