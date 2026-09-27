from typing import Dict
from fastapi.testclient import TestClient


def test_get_my_profile_unauthenticated(client: TestClient) -> None:
    response = client.get("/api/v1/users/me/profile")
    assert response.status_code == 401


def test_get_my_profile_authenticated(client: TestClient, auth_headers: Dict[str, str]) -> None:
    response = client.get("/api/v1/users/me/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user_id" in data["data"]


def test_update_my_profile(client: TestClient, auth_headers: Dict[str, str]) -> None:
    update_payload = {
        "personal": {
            "name": "Alex Patel Updated",
            "college": "CSPIT College",
            "degree": "B.Tech Information Technology",
            "graduationYear": "2027"
        },
        "career": {
            "targetRole": "Backend Developer",
            "companyTier": "Tier-1 Product (MAANG / Unicorns)"
        }
    }
    response = client.put("/api/v1/users/me/profile", json=update_payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["personal"]["name"] == "Alex Patel Updated"
