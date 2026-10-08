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


# --- POSITIVE FLOW TESTS (A - G) ---

def test_create_and_manage_conversation_flow(client: TestClient, auth_headers: dict):
    """A. Create conversation, B. List own, C. Get own, F. Archive own, G. Confirm archived status."""
    # A. Create conversation
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

    # B. Get list of user conversations
    res_list = client.get("/api/v1/mentor/conversations", headers=auth_headers)
    assert res_list.status_code == 200
    conv_list = res_list.json()
    assert len(conv_list) >= 1
    assert any(c["conversation_id"] == conv_id for c in conv_list)

    # C. Get single conversation detail
    res_detail = client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["conversation_id"] == conv_id
    assert detail["status"] == "active"
    assert "messages" in detail
    assert isinstance(detail["messages"], list)

    # F. Archive conversation
    res_del = client.delete(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "success"

    # G. Get archived conversation and confirm status="archived"
    res_archived = client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_archived.status_code == 200
    assert res_archived.json()["status"] == "archived"


def test_send_message_to_active_conversation(client: TestClient, auth_headers: dict):
    """D. Send message to own active conversation."""
    res_create = client.post("/api/v1/mentor/conversations", json={"title": "Daily Plan Q&A"}, headers=auth_headers)
    conv_id = res_create.json()["conversation_id"]

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

    # Retrieve conversation detail to verify both messages were stored
    res_detail = client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    messages = res_detail.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What should I study today?"
    assert messages[1]["role"] == "assistant"


def test_ask_mentor_on_active_conversation(client: TestClient, auth_headers: dict):
    """E. /mentor/ask on own active conversation and without conversation."""
    # Without conversation ID
    res_ask1 = client.post(
        "/api/v1/mentor/ask",
        json={"message": "Why is my readiness score low?"},
        headers=auth_headers,
    )
    assert res_ask1.status_code == 200
    ask_data1 = res_ask1.json()
    assert "answer" in ask_data1
    assert "intent" in ask_data1
    assert "context_sources" in ask_data1
    assert "conversation_id" in ask_data1
    conv_id = ask_data1["conversation_id"]

    # With existing active conversation ID
    res_ask2 = client.post(
        "/api/v1/mentor/ask",
        json={"message": "How can I improve my DSA skills?", "conversation_id": conv_id},
        headers=auth_headers,
    )
    assert res_ask2.status_code == 200
    ask_data2 = res_ask2.json()
    assert ask_data2["conversation_id"] == conv_id


# --- NEGATIVE & VALIDATION TESTS (H - R) ---

def test_nonexistent_conversation_operations(client: TestClient, auth_headers: dict):
    """H, I, J, K: Nonexistent conversation operations return 404."""
    fake_id = "conv_nonexistent_99999"
    # H. GET nonexistent
    assert client.get(f"/api/v1/mentor/conversations/{fake_id}", headers=auth_headers).status_code == 404

    # I. DELETE nonexistent
    assert client.delete(f"/api/v1/mentor/conversations/{fake_id}", headers=auth_headers).status_code == 404

    # J. Send message to nonexistent
    assert client.post(
        f"/api/v1/mentor/conversations/{fake_id}/messages",
        json={"message": "Hello?"},
        headers=auth_headers,
    ).status_code == 404

    # K. /ask with nonexistent conversation_id
    assert client.post(
        "/api/v1/mentor/ask",
        json={"message": "Hello?", "conversation_id": fake_id},
        headers=auth_headers,
    ).status_code == 404


def test_empty_and_whitespace_messages(client: TestClient, auth_headers: dict):
    """L, M: Empty and whitespace-only message validation."""
    res_create = client.post("/api/v1/mentor/conversations", json={"title": "Empty Test"}, headers=auth_headers)
    conv_id = res_create.json()["conversation_id"]

    # L. Empty string
    assert client.post(f"/api/v1/mentor/conversations/{conv_id}/messages", json={"message": ""}, headers=auth_headers).status_code == 422
    assert client.post("/api/v1/mentor/ask", json={"message": ""}, headers=auth_headers).status_code == 422

    # M. Whitespace only
    assert client.post(f"/api/v1/mentor/conversations/{conv_id}/messages", json={"message": "   \n\t  "}, headers=auth_headers).status_code == 422
    assert client.post("/api/v1/mentor/ask", json={"message": "   "}, headers=auth_headers).status_code == 422


def test_archived_conversation_message_rejection(client: TestClient, auth_headers: dict):
    """N, O: Archived conversation rejects new messages with 409 Conflict."""
    # Create conversation and archive it
    res_create = client.post("/api/v1/mentor/conversations", json={"title": "Archived Test"}, headers=auth_headers)
    conv_id = res_create.json()["conversation_id"]
    client.delete(f"/api/v1/mentor/conversations/{conv_id}", headers=auth_headers)

    # N. POST /messages on archived conversation -> 409 Conflict
    res_msg = client.post(
        f"/api/v1/mentor/conversations/{conv_id}/messages",
        json={"message": "Should fail because archived"},
        headers=auth_headers,
    )
    assert res_msg.status_code == 409

    # O. POST /ask with archived conversation_id -> 409 Conflict
    res_ask = client.post(
        "/api/v1/mentor/ask",
        json={"message": "Should fail because archived", "conversation_id": conv_id},
        headers=auth_headers,
    )
    assert res_ask.status_code == 409


def test_cross_user_isolation(client: TestClient, auth_headers: dict, mock_db):
    """P, Q, R: Cross-user isolation - user 2 cannot access, message, or archive user 1's conversation."""
    mock_db["users"].docs["other_user_mentor_999"] = {
        "_id": "other_user_mentor_999",
        "email": "other_mentor@example.com",
        "hashed_password": "hashed_secret",
        "full_name": "Other Student",
        "is_active": True,
    }

    # Create conversation as User 1
    res_create = client.post("/api/v1/mentor/conversations", json={"title": "User1 Private Session"}, headers=auth_headers)
    conv_id = res_create.json()["conversation_id"]

    # Headers for User 2
    user2_token = create_access_token(subject="other_user_mentor_999", extra_claims={"email": "other_mentor@example.com"})
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # P. User 2 attempts to get User 1's conversation -> 404
    assert client.get(f"/api/v1/mentor/conversations/{conv_id}", headers=user2_headers).status_code == 404

    # Q. User 2 attempts to send message to User 1's conversation -> 404
    assert client.post(
        f"/api/v1/mentor/conversations/{conv_id}/messages",
        json={"message": "Unauthorized message"},
        headers=user2_headers,
    ).status_code == 404

    # R. User 2 attempts to archive User 1's conversation -> 404
    assert client.delete(f"/api/v1/mentor/conversations/{conv_id}", headers=user2_headers).status_code == 404


# --- DYNAMIC CONTEXT & ENGINE TESTS (S - W) ---

def test_dynamic_mentor_uses_actual_student_data(client: TestClient, auth_headers: dict, mock_db):
    """S, T, U, V, W: Test mentor dynamically uses actual target role, skills, readiness, and produces real context sources/evidence."""
    from app.engines.mentor_engine import AIMentorEngine

    context = {
        "target_role": "AI/ML Engineer",
        "profile": {
            "name": "Alice ML Specialist",
            "target_role": "AI/ML Engineer",
            "skills": ["PyTorch", "FastAPI", "Transformers"],
        },
        "readiness": {
            "overall_score": 88,
            "readiness_label": "Tier-1 Ready",
        },
        "skill_gaps": {
            "top_gaps": ["Dynamic Programming", "Distributed Training"],
        },
        "leetcode_analysis": {"solved": 150},
        "leetcode_weak_topics": ["Dynamic Programming"],
    }

    engine = AIMentorEngine()

    # S, T: Query about DSA
    res_dsa = engine.chat({
        "message": "What DSA topics should I practice on LeetCode?",
        "student_context": context,
    })
    assert "AI/ML Engineer" in res_dsa["answer"] or "Dynamic Programming" in res_dsa["answer"]
    assert res_dsa["intent"] in ["leetcode", "dsa"]
    # U: context_sources contains real sources
    assert "profile" in res_dsa["context_sources"]
    assert "leetcode" in res_dsa["context_sources"]
    # V: evidence matches actual student data
    assert any("AI/ML Engineer" in ev for ev in res_dsa["evidence"])
    assert any("Dynamic Programming" in ev for ev in res_dsa["evidence"])
    # Confidence is between 0.70 and 0.95
    assert 0.70 <= res_dsa["confidence"] <= 0.95

    # W: Query about readiness
    res_ready = engine.chat({
        "message": "Can you assess my readiness score?",
        "student_context": context,
    })
    assert res_ready["intent"] == "readiness"
    assert "88/100" in res_ready["answer"]
    assert "readiness" in res_ready["context_sources"]
    assert any("88/100" in ev for ev in res_ready["evidence"])


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
