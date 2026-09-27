import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.integrations.ai_client import AIClientError


def test_mentor_unauthenticated(client: TestClient):
    """Test unauthenticated access to mentor endpoints."""
    assert client.post("/api/v1/mentor/conversations", json={}).status_code == 401
    assert client.get("/api/v1/mentor/conversations").status_code == 401
    assert client.get("/api/v1/mentor/conversations/conv_123").status_code == 401
    assert client.post("/api/v1/mentor/conversations/conv_123/messages", json={"message": "hi"}).status_code == 401
    assert client.delete("/api/v1/mentor/conversations/conv_123").status_code == 401
    assert client.post("/api/v1/mentor/ask", json={"message": "hi"}).status_code == 401


def test_create_and_manage_conversation_flow(client: TestClient, auth_headers: dict):
    """Test creating a conversation session, fetching history, and archiving."""
    # 1. Create conversation
    res_create = client.post(
        "/api/v1/mentor/conversations",
        json={"title": "Test Preparation Session"},
        headers=auth_headers,
    )
    assert res_create.status_code == 201
    conv_data = res_create.json()
    assert "conversation_id" in conv_data
    assert conv_data["title"] == "Test Preparation Session"
    assert conv_data["status"] == "active"
    conv_id = conv_data["conversation_id"]

    # 2. Get list of user conversations
    res_list = client.get("/api/v1/mentor/conversations", headers=auth_headers)
    assert res_list.status_code == 200
    conv_list = res_list.json()
    assert len(conv_list) >= 1
    assert any(c["conversation_id"] == conv_id for c in conv_list)

    # 3. Get single conversation detail
    res_detail = client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["conversation_id"] == conv_id
    assert "messages" in detail
    assert isinstance(detail["messages"], list)

    # 4. Archive conversation
    res_del = client.delete(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"


def test_send_mentor_message(client: TestClient, auth_headers: dict):
    """Test sending a query message to mentor within a conversation session."""
    # 1. Create conversation
    res_create = client.post("/api/v1/mentor/conversations", json={"title": "Daily Plan Q&A"}, headers=auth_headers)
    conv_id = res_create.json()["conversation_id"]

    # 2. Send message
    res_msg = client.post(
        f"/api/v1/mentor/conversations/{conv_id}/messages",
        json={"message": "What should I study today?"},
        headers=auth_headers,
    )
    assert res_msg.status_code == 200
    msg_data = res_msg.json()
    assert msg_data["role"] == "assistant"
    assert "content" in msg_data
    assert len(msg_data["content"]) > 0
    assert "intent" in msg_data
    assert "context_sources" in msg_data

    # 3. Retrieve conversation detail to verify messages were stored
    res_detail = client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    messages = res_detail.json()["messages"]
    # Should have user message + assistant message
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What should I study today?"
    assert messages[1]["role"] == "assistant"


def test_quick_ask_mentor(client: TestClient, auth_headers: dict):
    """Test /api/v1/mentor/ask endpoint."""
    res_ask = client.post(
        "/api/v1/mentor/ask",
        json={"message": "Why is my readiness score low?"},
        headers=auth_headers,
    )
    assert res_ask.status_code == 200
    ask_data = res_ask.json()
    assert "answer" in ask_data
    assert "intent" in ask_data
    assert "context_sources" in ask_data
    assert "conversation_id" in ask_data


def test_mentor_ownership_security(client: TestClient, auth_headers: dict, mock_db):
    """Test that student cannot access or message another student's conversation."""
    # Seed user 2 in mock DB
    mock_db["users"].docs["other_user_mentor_999"] = {
        "_id": "other_user_mentor_999",
        "email": "other_mentor@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "Other Student",
        "is_active": True,
    }

    # Create conversation as User 1
    res_create = client.post("/api/v1/mentor/conversations", json={"title": "Private Session"}, headers=auth_headers)
    conv_id = res_create.json()["conversation_id"]

    # Header for User 2
    user2_token = create_access_token(subject="other_user_mentor_999", extra_claims={"email": "other_mentor@example.com"})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User 2 attempts to get User 1's conversation
    assert client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=user2_headers).status_code == 404

    # User 2 attempts to send message to User 1's conversation
    assert client.post(
        f"/api/v1/mentor/conversations/{conv_id}/messages",
        json={"message": "Unauthorized message"},
        headers=user2_headers,
    ).status_code == 404

    # User 2 attempts to archive User 1's conversation
    assert client.delete(f"/api/v1/mentor/conversations/{conv_id}", headers=user2_headers).status_code == 404


def test_ai_failure_fallback_mentor(client: TestClient, auth_headers: dict):
    """Test that if AI microservice fails, local fallback engine generates valid guidance response."""
    with patch("app.integrations.ai_client.AIClient.chat_mentor", new_callable=AsyncMock, side_effect=AIClientError("AI Microservice down")):
        res_ask = client.post(
            "/api/v1/mentor/ask",
            json={"message": "How can I improve my GitHub profile?"},
            headers=auth_headers,
        )
        assert res_ask.status_code == 200
        ask_data = res_ask.json()
        assert "answer" in ask_data
        assert len(ask_data["answer"]) > 0
        assert ask_data["intent"] in ["github", "projects", "general_placement"]
