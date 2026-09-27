from typing import Dict
from fastapi.testclient import TestClient


def test_get_onboarding_unauthenticated(client: TestClient) -> None:
    response = client.get("/api/v1/onboarding")
    assert response.status_code == 401


def test_get_onboarding_authenticated(client: TestClient, auth_headers: Dict[str, str]) -> None:
    response = client.get("/api/v1/onboarding", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "personal" in data["data"]


def test_save_onboarding_step(client: TestClient, auth_headers: Dict[str, str]) -> None:
    step_data = {
        "step_number": 1,
        "profile": {
            "name": "Alex Patel",
            "college": "CSPIT",
            "degree": "B.Tech IT",
            "graduationYear": "2027"
        }
    }
    response = client.patch("/api/v1/onboarding/step", json=step_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["personal"]["name"] == "Alex Patel"


def test_save_onboarding_step_validation(client: TestClient, auth_headers: Dict[str, str]) -> None:
    invalid_step = {
        "step_number": 1,
        "profile": {
            "name": "Alex Patel",
            "college": "CSPIT",
            "degree": "B.Tech IT",
            "graduationYear": "1990"  # Invalid year
        }
    }
    response = client.patch("/api/v1/onboarding/step", json=invalid_step, headers=auth_headers)
    assert response.status_code == 422


def test_complete_onboarding(client: TestClient, auth_headers: Dict[str, str]) -> None:
    # First save valid step data
    step1 = {
        "step_number": 1,
        "profile": {
            "name": "Alex Patel",
            "college": "CSPIT",
            "degree": "B.Tech IT",
            "graduationYear": "2027"
        },
        "career": {
            "targetRole": "Backend Developer",
            "secondaryRole": "AI/ML Engineer",
            "companyTier": "Tier-1 Product (MAANG / Unicorns)"
        }
    }
    client.patch("/api/v1/onboarding/step", json=step1, headers=auth_headers)

    response = client.post("/api/v1/onboarding/complete", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["onboarding_completed"] is True
