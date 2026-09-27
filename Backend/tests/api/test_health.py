from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Placement Copilot API"
    assert data["status"] == "running"


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AI Placement Copilot API"


def test_api_v1_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data


def test_health_database_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "MongoDB"


def test_health_redis_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health/redis")
    assert response.status_code == 200
    data = response.json()
    assert data["component"] == "Redis"
