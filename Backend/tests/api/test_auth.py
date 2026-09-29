import pytest
from fastapi.testclient import TestClient


def test_auth_register_and_login_flow(client: TestClient) -> None:
    # 1. Register new user
    user_email = "newstudent@example.com"
    user_password = "SecurePassword123!"
    user_name = "New Student"

    reg_payload = {
        "email": user_email,
        "password": user_password,
        "full_name": user_name,
    }
    reg_response = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data["data"]
    assert "refresh_token" in reg_data["data"]
    assert reg_data["data"]["user"]["email"] == user_email
    assert reg_data["data"]["user"]["is_onboarded"] is False

    # 2. Duplicate registration attempt should fail with 409
    dup_response = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_response.status_code == 409

    # 3. Login with correct credentials
    login_payload = {
        "email": user_email,
        "password": user_password,
    }
    login_response = client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    access_token = login_data["data"]["access_token"]
    refresh_token = login_data["data"]["refresh_token"]

    # 4. Login with invalid password
    bad_login_response = client.post("/api/v1/auth/login", json={
        "email": user_email,
        "password": "WrongPassword123",
    })
    assert bad_login_response.status_code == 401

    # 5. Access protected /me route
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["success"] is True
    assert me_data["data"]["email"] == user_email

    # 6. Reject refresh token passed as access token to /me
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
    me_refresh_response = client.get("/api/v1/auth/me", headers=refresh_headers)
    assert me_refresh_response.status_code == 401

    # 7. Refresh access token using refresh token
    ref_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_response.status_code == 200
    ref_data = ref_response.json()
    assert ref_data["success"] is True
    assert "access_token" in ref_data["data"]
    assert "user" in ref_data["data"]

    # 8. Logout
    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
