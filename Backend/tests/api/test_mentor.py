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


# ===========================================================================
# Unit & Integration Tests for AI Mentor Intent Handling & Technical Responses
# ===========================================================================

def test_mentor_engine_python_error_missing_code():
    """Verify that vague Python error query asks user to provide code and error traceback."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "My Python code is giving an error",
        "student_context": {"target_role": "Backend Developer"},
    })
    assert res["intent"] == "python_error_missing"
    assert "share your python code" in res["answer"].lower()
    assert "traceback" in res["answer"].lower()


def test_mentor_engine_python_error_diagnosis():
    """Verify that specific Python error with traceback diagnoses root cause and provides defensive fix."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Why do I get TypeError: 'NoneType' object is not subscriptable in Python?",
        "student_context": {"target_role": "Backend Developer"},
    })
    assert res["intent"] == "python_error"
    assert "TypeError: 'NoneType' object is not subscriptable" in res["answer"]
    assert "Root Cause" in res["answer"]
    assert "```python" in res["answer"]


def test_mentor_engine_oop_four_pillars():
    """Verify that OOP query returns concise explanation of the 4 pillars and code."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Explain OOP concepts and the 4 pillars",
        "student_context": {"target_role": "Software Engineer"},
    })
    assert res["intent"] == "oop"
    ans = res["answer"]
    assert "Encapsulation" in ans
    assert "Abstraction" in ans
    assert "Inheritance" in ans
    assert "Polymorphism" in ans
    assert "```python" in ans


def test_mentor_engine_leetcode_missing_problem():
    """Verify that vague LeetCode query asks user for problem name or number."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Help me solve this LeetCode problem",
        "student_context": {"target_role": "Software Engineer"},
    })
    assert res["intent"] == "leetcode_missing"
    assert "Which LeetCode problem are you working on?" in res["answer"]


def test_mentor_engine_leetcode_two_sum():
    """Verify that LeetCode Two Sum query returns optimal O(N) hash map solution."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "How do I solve LeetCode 1 Two Sum?",
        "student_context": {"target_role": "Software Engineer"},
    })
    assert res["intent"] == "leetcode"
    ans = res["answer"]
    assert "Two Sum" in ans
    assert "Hash Map" in ans or "complement" in ans
    assert "O(N)" in ans
    assert "def twoSum" in ans


def test_mentor_engine_followup_conversation_history():
    """Verify that follow-up asking for code example uses conversation history."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    history = [
        {"role": "user", "content": "What is encapsulation in OOP?"},
        {"role": "assistant", "content": "Encapsulation bundles data and methods and hides internal state with private attributes."},
    ]
    res = engine.chat({
        "message": "Can you give me a code example in Python?",
        "student_context": {"target_role": "Software Engineer"},
        "conversation_history": history,
    })
    assert res["intent"] == "followup_code"
    ans = res["answer"]
    assert "BankAccount" in ans or "balance" in ans.lower()
    assert "```python" in ans


def test_mentor_engine_roadmap_task_progress_real_data():
    """Verify real application data is used for remaining days and pending count without hallucination."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    context = {
        "target_role": "Cloud / DevOps Engineer",
        "roadmap": {
            "current_day": 7,
            "total_days": 90,
            "remaining_days": 83,
            "total_tasks_count": 180,
        },
        "all_pending_tasks": {
            "total_pending": 84,
            "tasks": [{"title": "Docker Multi-stage Builds", "day": 7, "category": "DevOps", "estimated_minutes": 45}],
        },
        "today_tasks": {
            "pending_tasks": [{"title": "Docker Multi-stage Builds", "day": 7, "category": "DevOps", "estimated_minutes": 45}],
            "completed_tasks": [],
        },
        "progress": {"completed_tasks": 96},
    }

    # Remaining days query
    res_days = engine.chat({
        "message": "How many days are remaining?",
        "student_context": context,
    })
    assert res_days["intent"] == "remaining_days"
    assert "83 days remaining" in res_days["answer"]
    assert "Day 7" in res_days["answer"]
    assert "90-day" in res_days["answer"]

    # Why 84 tasks pending query
    res_why = engine.chat({
        "message": "Why are 84 tasks pending?",
        "student_context": context,
    })
    assert res_why["intent"] == "why_pending"
    assert "84" in res_why["answer"]
    assert "180" in res_why["answer"]
    assert "96" in res_why["answer"]


def test_mentor_engine_coding_binary_search():
    """Verify coding question for binary search returns time complexity and code."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Explain binary search and implement it in Python",
        "student_context": {"target_role": "Software Engineer"},
    })
    assert res["intent"] in ["coding", "leetcode"]
    ans = res["answer"]
    assert "Binary Search" in ans
    assert "O(\\log N)" in ans or "O(log N)" in ans
    assert "def binary_search" in ans


# ===========================================================================
# Backend Engine Regression Tests (8 Required Problem Archetypes)
# ===========================================================================

def test_mentor_engine_regression_ask_5_python_interview_questions():
    """Regression Test 1: Ask me 5 Python interview questions returns 5 questions with interactive prompt."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Ask me 5 Python interview questions",
        "student_context": {"target_role": "Data Engineer", "roadmap": {"total_days": 60}},
    })
    assert res["intent"] in ["interview_questions", "interview_practice"]
    ans = res["answer"]
    assert "5 Python" in ans
    assert "Mutability" in ans or "GIL" in ans or "Generators" in ans
    assert "Interactive Practice" in ans


def test_mentor_engine_regression_what_about_day_13():
    """Regression Test 2: What about Day 13? retrieves scheduled tasks for Day 13 dynamically from context."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "What about Day 13?",
        "student_context": {
            "target_role": "Full Stack Engineer",
            "roadmap": {"current_day": 10, "total_days": 60},
            "tasks_by_day": {
                "13": [
                    {
                        "title": "PostgreSQL Query Optimization & Indexing",
                        "category": "Databases",
                        "estimated_minutes": 90,
                        "difficulty": "Hard",
                        "status": "pending"
                    }
                ]
            }
        },
    })
    assert res["intent"] == "day_specific"
    ans = res["answer"]
    assert "Day 13" in ans
    assert "PostgreSQL Query Optimization & Indexing" in ans
    assert "Databases" in ans


def test_mentor_engine_regression_what_should_i_learn_next():
    """Regression Test 3: What should I learn next? dynamically recommends the next appropriate incomplete task."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "What should I learn next?",
        "student_context": {
            "target_role": "Site Reliability Engineer",
            "roadmap": {"current_day": 5, "total_days": 45},
            "next_recommended_task": {
                "title": "Prometheus & Grafana Alerting Setup",
                "day": 5,
                "category": "Monitoring",
                "difficulty": "Medium",
                "estimated_minutes": 60
            }
        },
    })
    assert res["intent"] == "learn_next"
    ans = res["answer"]
    assert "Prometheus & Grafana Alerting Setup" in ans
    assert "Day 5" in ans
    assert "Monitoring" in ans


def test_mentor_engine_regression_what_is_my_target_role():
    """Regression Test 4: What is my target role? returns actual saved role without hardcoding."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "What is my target role?",
        "student_context": {
            "target_role": "AI / Machine Learning Engineer",
            "roadmap": {"total_days": 120, "start_date": "2026-09-01"},
            "profile": {"skills": ["PyTorch", "Transformers", "CUDA"]}
        },
    })
    assert res["intent"] == "target_role"
    ans = res["answer"]
    assert "AI / Machine Learning Engineer" in ans
    assert "120-day" in ans
    assert "PyTorch" in ans
    assert "AWS / DevOps" not in ans


def test_mentor_engine_regression_which_tasks_are_overdue():
    """Regression Test 5: Which tasks are overdue? finds and reports incomplete tasks past due date."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Which tasks are overdue?",
        "student_context": {
            "target_role": "Backend Developer",
            "roadmap": {"current_day": 12, "total_days": 60},
            "overdue_tasks": {
                "total_overdue": 2,
                "tasks": [
                    {"title": "Redis Pub/Sub Setup", "day": 8, "category": "Backend", "estimated_minutes": 45},
                    {"title": "Celery Distributed Workers", "day": 10, "category": "Backend", "estimated_minutes": 60}
                ]
            }
        },
    })
    assert res["intent"] == "overdue_tasks"
    ans = res["answer"]
    assert "2" in ans
    assert "overdue" in ans.lower()
    assert "Redis Pub/Sub Setup" in ans
    assert "Celery Distributed Workers" in ans


def test_mentor_engine_regression_explain_numpy_broadcasting():
    """Regression Test 6: Explain NumPy broadcasting provides compatibility rules, code example, and memory model."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Explain NumPy broadcasting",
        "student_context": {"target_role": "Data Scientist"},
    })
    assert res["intent"] == "numpy"
    ans = res["answer"]
    assert "NumPy Broadcasting" in ans
    assert "Broadcasting Rules" in ans or "Dimension Compatibility" in ans
    assert "Trailing dimensions" in ans or "dimensions are compatible" in ans or "Rule 1" in ans
    assert "```python" in ans
    assert "np.array" in ans


def test_mentor_engine_regression_explain_oop_concepts_for_interviews():
    """Regression Test 7: Explain OOP concepts for interviews provides 4 pillars, top interview questions, and payment gateway code."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Explain OOP concepts for interviews",
        "student_context": {"target_role": "Backend Engineer"},
    })
    assert res["intent"] == "oop_interview"
    ans = res["answer"]
    assert "OOP Concepts for Technical Interviews" in ans
    assert "Encapsulation" in ans
    assert "Abstraction" in ans
    assert "Inheritance" in ans
    assert "Polymorphism" in ans
    assert "Composition vs" in ans or "Abstract Class" in ans
    assert "PaymentGateway" in ans or "abstractmethod" in ans
    assert "```python" in ans


def test_mentor_engine_regression_explain_binary_search_step_by_step():
    """Regression Test 8: Explain binary search step by step provides walkthrough, formula, trace example, and Python code."""
    from app.engines.mentor_engine import AIMentorEngine
    engine = AIMentorEngine()
    res = engine.chat({
        "message": "Explain binary search step by step",
        "student_context": {"target_role": "Software Development Engineer"},
    })
    assert res["intent"] == "binary_search_step"
    ans = res["answer"]
    assert "Step-by-Step" in ans
    assert "mid = low + (high - low) // 2" in ans
    assert "Step-by-Step Walkthrough" in ans or "Pass 1" in ans
    assert "def binary_search" in ans


def test_ask_mentor_with_client_session_id(client: TestClient, auth_headers: dict):
    """Client sessions starting with session- or local_ are auto-created gracefully without 404."""
    client_sess_id = "session-1729341234567"
    res = client.post(
        "/api/v1/mentor/ask",
        json={"message": "What should I focus on today?", "conversation_id": client_sess_id},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert data["conversation_id"] == client_sess_id



