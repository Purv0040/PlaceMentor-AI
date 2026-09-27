import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoints(client: TestClient):
    """Verify basic and detailed health check endpoints."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    response_v1 = client.get("/api/v1/health")
    assert response_v1.status_code == 200
    v1_data = response_v1.json()
    assert "status" in v1_data
    assert "components" in v1_data


def test_unauthenticated_access_protection(client: TestClient):
    """Verify unauthenticated requests to protected endpoints return 401."""
    response = client.get("/api/v1/achievements")
    assert response.status_code == 401

    response_notif = client.get("/api/v1/notifications")
    assert response_notif.status_code == 401


def test_invalid_jwt_token_handling(client: TestClient):
    """Verify malformed or invalid JWT tokens return 401."""
    headers = {"Authorization": "Bearer invalid_malformed_token_12345"}
    response = client.get("/api/v1/achievements", headers=headers)
    assert response.status_code == 401


def test_invalid_objectid_validation_error(client: TestClient, auth_headers: dict):
    """Verify passing an invalid ObjectId string returns a clean error status code."""
    response = client.get("/api/v1/achievements/invalid-hex-id-xyz", headers=auth_headers)
    assert response.status_code in [400, 404, 422]


def test_cors_preflight_handling(client: TestClient):
    """Verify OPTIONS preflight request handling."""
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    }
    response = client.options("/api/v1/health", headers=headers)
    assert response.status_code == 200
