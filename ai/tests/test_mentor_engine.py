"""
Unit and integration tests for the Personal AI Placement Mentor.
Tests ContextBuilder routing, PersonalMentorEngine prompt building, and the API endpoint.
"""
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.engines.mentor_engine import ContextBuilder, PersonalMentorEngine
from app.schemas.mentor import MentorChatRequest, MentorChatResponse, StudentContext, ChatMessage


@pytest.fixture
def mock_llm_service():
    """Mock LLMService for deterministic execution without external API calls."""
    mock = MagicMock()
    mock.generate_structured.return_value = MentorChatResponse(
        answer="This is a mock answer based on the context.",
        evidence=["Fact 1"],
        recommended_actions=["Action 1"],
        related_skills=["Python"],
        confidence=0.9
    )
    return mock


@pytest.fixture
def sample_context():
    """Sample StudentContext for testing."""
    return StudentContext(
        target_role="Backend Developer",
        profile={"skill": "Python", "level": "Intermediate"},
        resume_analysis={"score": 85, "weak_bullets": []},
        leetcode_analysis={"total_solved": 150},
        projects=[{"name": "API Service"}],
        skill_gaps={"Docker": "High"},
        readiness={"overall_score": 70},
        roadmap={"phases": []},
        today_tasks={"tasks": [{"title": "Do DSA"}]},
        progress={"completion_rate": 80.0}
    )


def test_context_builder_resume_question(sample_context):
    """Test ContextBuilder routing for a resume-related question."""
    builder = ContextBuilder()
    context_dict = builder.build_context("How can I improve my resume?", sample_context)
    
    # Should include resume_analysis, profile, target_role
    assert "resume_analysis" in context_dict
    assert "profile" in context_dict
    assert "target_role" in context_dict
    # Should not include unrelated context
    assert "leetcode_analysis" not in context_dict


def test_context_builder_dsa_question(sample_context):
    """Test ContextBuilder routing for a DSA-related question."""
    builder = ContextBuilder()
    context_dict = builder.build_context("Which leetcode problems should I practice?", sample_context)
    
    assert "leetcode_analysis" in context_dict
    assert "roadmap" in context_dict
    assert "progress" in context_dict
    assert "skill_gaps" in context_dict
    assert "resume_analysis" not in context_dict


def test_context_builder_today_question(sample_context):
    """Test ContextBuilder routing for a today's tasks question."""
    builder = ContextBuilder()
    context_dict = builder.build_context("What should I focus on today?", sample_context)
    
    assert "today_tasks" in context_dict
    assert "roadmap" in context_dict
    assert "skill_gaps" in context_dict
    assert "progress" in context_dict


def test_context_builder_unmatched_question(sample_context):
    """Test ContextBuilder routing for an unmatched question (general balanced context)."""
    builder = ContextBuilder()
    context_dict = builder.build_context("Tell me about myself.", sample_context)
    
    # Should fallback to balanced context
    assert "profile" in context_dict
    assert "skill_gaps" in context_dict
    assert "progress" in context_dict
    assert "today_tasks" in context_dict
    assert "target_role" in context_dict


def test_personal_mentor_engine_chat(sample_context, mock_llm_service):
    """Test the PersonalMentorEngine chat flow constructs correct prompts."""
    engine = PersonalMentorEngine(llm_service=mock_llm_service)
    
    request = MentorChatRequest(
        message="What is my resume score?",
        student_context=sample_context,
        conversation_history=[
            ChatMessage(role="user", content="Hi mentor!"),
            ChatMessage(role="assistant", content="Hello! How can I help?")
        ]
    )
    
    response = engine.chat(request)
    
    # Check that LLM was called
    mock_llm_service.generate_structured.assert_called_once()
    
    # Verify the prompt string sent to LLM
    call_args = mock_llm_service.generate_structured.call_args
    prompt = call_args.kwargs['prompt']
    
    assert "You are a Personal AI Placement Mentor" in prompt
    assert "CRITICAL RULES" in prompt
    assert "resume_analysis" in prompt # Context builder included resume
    assert "Hi mentor!" in prompt # Conversation history included
    assert "What is my resume score?" in prompt # Current question included
    
    assert response.answer == "This is a mock answer based on the context."
    assert response.confidence == 0.9


def test_personal_mentor_engine_missing_data(sample_context, mock_llm_service):
    """Test mentor chat gracefully handles missing data in context."""
    # Remove resume analysis from context
    sample_context.resume_analysis = None
    
    engine = PersonalMentorEngine(llm_service=mock_llm_service)
    request = MentorChatRequest(
        message="What is my resume score?",
        student_context=sample_context
    )
    
    engine.chat(request)
    
    call_args = mock_llm_service.generate_structured.call_args
    prompt = call_args.kwargs['prompt']
    
    # Verify that resume_analysis is NOT in the prompt (filtered out)
    assert "resume_analysis" not in prompt


def test_api_mentor_chat_endpoint():
    """Integration test for POST /api/ai/mentor/chat."""
    client = TestClient(app)
    
    # Patch the engine so we don't need a real LLM key for endpoint test
    with patch("app.main.mentor_engine.chat") as mock_chat:
        mock_chat.return_value = MentorChatResponse(
            answer="API Mock Answer",
            evidence=["Evidence 1"],
            recommended_actions=["Action 1"],
            related_skills=["Backend"],
            confidence=0.85
        )
        
        payload = {
            "message": "How am I progressing?",
            "student_context": {
                "target_role": "Backend Developer",
                "progress": {"completion_rate": 75.0}
            },
            "conversation_history": [
                {"role": "user", "content": "Hi"}
            ]
        }
        
        response = client.post("/api/ai/mentor/chat", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["answer"] == "API Mock Answer"
        assert data["confidence"] == 0.85
        assert len(data["evidence"]) == 1


# ===========================================================================
# Comprehensive Tests for Intent Handling, Technical Q&A, and Follow-ups
# ===========================================================================

def test_grounded_greeting_response():
    """Test greeting returns natural, brief message using dynamic target role."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Cloud / DevOps Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: hi"
    )
    res = _build_grounded_mentor_response(prompt)
    assert "Cloud / DevOps Engineer" in res["answer"]
    assert len(res["answer"]) < 120
    assert "Hey there!" in res["answer"]


def test_grounded_python_error_missing_details():
    """Test vague Python error query asks user to provide code and traceback."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Backend Developer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: My Python code is giving an error"
    )
    res = _build_grounded_mentor_response(prompt)
    assert "share your Python code snippet" in res["answer"]
    assert "error message or traceback" in res["answer"]


def test_grounded_python_error_with_traceback():
    """Test specific Python error diagnoses root cause and provides defensive code fix."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Backend Developer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Why do I get TypeError: 'NoneType' object is not subscriptable in Python?"
    )
    res = _build_grounded_mentor_response(prompt)
    assert "TypeError: 'NoneType' object is not subscriptable" in res["answer"]
    assert "Root Cause" in res["answer"]
    assert "Corrected Code" in res["answer"]
    assert "```python" in res["answer"]


def test_grounded_oop_explanations():
    """Test OOP query explains the 4 pillars with code demonstration."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Explain OOP concepts and the 4 pillars"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Encapsulation" in ans
    assert "Abstraction" in ans
    assert "Inheritance" in ans
    assert "Polymorphism" in ans
    assert "```python" in ans


def test_grounded_oop_specific_encapsulation():
    """Test specific OOP pillar query focuses on encapsulation with class example."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: What is encapsulation in Python?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Encapsulation" in ans
    assert "BankAccount" in ans or "private" in ans.lower()
    assert "```python" in ans


def test_grounded_leetcode_missing_problem():
    """Test vague LeetCode query asks user for problem name or number."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Help me solve this LeetCode problem"
    )
    res = _build_grounded_mentor_response(prompt)
    assert "Which LeetCode problem are you working on?" in res["answer"]
    assert "problem number, title, or the problem statement" in res["answer"]


def test_grounded_leetcode_two_sum():
    """Test LeetCode Two Sum query gives optimal O(N) hash map solution."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: How do I solve LeetCode 1 Two Sum?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Two Sum" in ans
    assert "Hash Map" in ans or "complement" in ans
    assert "O(N)" in ans
    assert "def twoSum" in ans


def test_grounded_coding_binary_search():
    """Test coding question for binary search returns time complexity and code."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Explain binary search and implement it"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Binary Search" in ans
    assert "O(\\log N)" in ans or "O(log N)" in ans
    assert "def binary_search" in ans


def test_grounded_followup_code_example():
    """Test conversational follow-up for a code example after discussing OOP encapsulation."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Engineer"}\n\n'
        "=== CONVERSATION HISTORY ===\n"
        "USER: What is encapsulation?\n"
        "ASSISTANT: Encapsulation is the practice of bundling data and methods inside a class.\n===\n\n"
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Can you give me a code example in Python?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "BankAccount" in ans or "Encapsulation" in ans
    assert "```python" in ans
    assert "balance" in ans.lower()


def test_grounded_system_design_query():
    """Test general technical system design query returns concrete architecture advice without generic deflection."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Backend Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: How should I design a caching and microservices architecture?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "System Design & Technical Architecture" in ans
    assert "Redis" in ans or "Cache" in ans
    assert "Load Balancer" in ans or "API Gateway" in ans
    # Should not be generic deflection
    assert "Would you like an algorithmic code example, an architectural breakdown" not in ans


def test_grounded_career_guidance():
    """Test career and placement guidance returns structured strategy without generic deflection."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Backend Developer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: How can I prepare to get placed in Tier-1 product companies and negotiate salary?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "placement advice" in ans.lower() or "tier-1" in ans.lower()
    assert "portfolio" in ans.lower() or "dsa" in ans.lower()
    assert "Would you like an algorithmic code example" not in ans


# ===========================================================================
# Dynamic AI Mentor Regression Tests (8 Required Problem Archetypes)
# ===========================================================================

def test_regression_ask_5_python_interview_questions():
    """Regression Test 1: Ask me 5 Python interview questions returns 5 structured Python questions with interactive prompt."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Data Engineer", "roadmap": {"total_days": 60}}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Ask me 5 Python interview questions"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "5 Python" in ans
    assert "Mutability" in ans or "GIL" in ans or "Generators" in ans
    assert "Interactive Practice" in ans
    assert len(res["evidence"]) >= 2
    assert "Topic: Python Interview Questions" in res["evidence"]


def test_regression_what_about_day_13():
    """Regression Test 2: What about Day 13? retrieves actual scheduled tasks for Day 13 dynamically from context."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
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
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: What about Day 13?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Day 13" in ans
    assert "PostgreSQL Query Optimization & Indexing" in ans
    assert "Databases" in ans
    assert "90 mins" in ans


def test_regression_what_should_i_learn_next():
    """Regression Test 3: What should I learn next? dynamically recommends the next appropriate incomplete task."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "Site Reliability Engineer",
        "roadmap": {"current_day": 5, "total_days": 45},
        "next_recommended_task": {
            "title": "Prometheus & Grafana Alerting Setup",
            "day": 5,
            "category": "Monitoring",
            "difficulty": "Medium",
            "estimated_minutes": 60
        }
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: What should I learn next?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Prometheus & Grafana Alerting Setup" in ans
    assert "Day 5" in ans
    assert "Monitoring" in ans
    assert "60 mins" in ans


def test_regression_what_is_my_target_role():
    """Regression Test 4: What is my target role? returns actual saved role without hardcoding."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "AI / Machine Learning Engineer",
        "roadmap": {"total_days": 120, "start_date": "2026-09-01"},
        "profile": {"skills": ["PyTorch", "Transformers", "CUDA"]}
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: What is my target role?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "AI / Machine Learning Engineer" in ans
    assert "120-day" in ans
    assert "PyTorch" in ans
    assert "AWS / DevOps" not in ans


def test_regression_which_tasks_are_overdue():
    """Regression Test 5: Which tasks are overdue? finds and reports incomplete tasks past due date."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "Backend Developer",
        "roadmap": {"current_day": 12, "total_days": 60},
        "overdue_tasks": {
            "total_overdue": 2,
            "tasks": [
                {"title": "Redis Pub/Sub Setup", "day": 8, "category": "Backend", "estimated_minutes": 45},
                {"title": "Celery Distributed Workers", "day": 10, "category": "Backend", "estimated_minutes": 60}
            ]
        }
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: Which tasks are overdue?"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "2" in ans
    assert "overdue" in ans.lower()
    assert "Redis Pub/Sub Setup" in ans
    assert "Celery Distributed Workers" in ans
    assert "Day 8" in ans
    assert "Day 10" in ans


def test_regression_explain_numpy_broadcasting():
    """Regression Test 6: Explain NumPy broadcasting provides compatibility rules, code example, and memory model."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Data Scientist"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Explain NumPy broadcasting"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "NumPy Broadcasting" in ans
    assert "Broadcasting Rules" in ans or "Dimension Compatibility" in ans
    assert "Trailing dimensions" in ans or "dimensions are compatible" in ans or "Rule 1" in ans
    assert "```python" in ans
    assert "np.array" in ans
    assert "O(1)" in ans or "memory" in ans.lower()


def test_regression_explain_oop_concepts_for_interviews():
    """Regression Test 7: Explain OOP concepts for interviews provides 4 pillars, top interview questions, and payment gateway code."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Backend Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Explain OOP concepts for interviews"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "OOP Concepts for Technical Interviews" in ans
    assert "Encapsulation" in ans
    assert "Abstraction" in ans
    assert "Inheritance" in ans
    assert "Polymorphism" in ans
    assert "Composition vs" in ans or "Abstract Class" in ans
    assert "PaymentGateway" in ans or "abstractmethod" in ans
    assert "```python" in ans


def test_regression_explain_binary_search_step_by_step():
    """Regression Test 8: Explain binary search step by step provides walkthrough, formula, trace example, and Python code."""
    from app.services.llm_service import _build_grounded_mentor_response
    prompt = (
        "=== STUDENT CONTEXT ===\n"
        '{"target_role": "Software Development Engineer"}\n\n'
        "=== CURRENT QUESTION ===\n"
        "STUDENT: Explain binary search step by step"
    )
    res = _build_grounded_mentor_response(prompt)
    ans = res["answer"]
    assert "Step-by-Step" in ans
    assert "mid = low + (high - low) // 2" in ans
    assert "Step-by-Step Walkthrough" in ans or "Pass 1" in ans
    assert "def binary_search" in ans
    assert "O(\\log N)" in ans or "O(log N)" in ans


# ===========================================================================
# Robustness & Context Data-Contract Regression Tests
# ===========================================================================

def test_regression_integer_counts_context():
    """Verify mentor handles standard integer-count semantics without type errors."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "Backend Engineer",
        "roadmap": {"current_day": 5, "total_days": 90, "total_tasks_count": 180},
        "all_pending_tasks": {
            "total_pending": 75,
            "tasks": [{"title": "API Design", "day": 5, "category": "Backend"}]
        },
        "progress": {
            "completed_tasks": 105,
            "completion_rate": 58.3
        }
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: How many tasks are incomplete?"
    )
    res = _build_grounded_mentor_response(prompt)
    assert "75" in res["answer"]
    assert "Total Pending Tasks: 75" in res["evidence"]


def test_regression_task_lists_as_counts_context():
    """Verify mentor handles task collections passed as lists for completed_tasks or total_pending."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "AI/ML Engineer",
        "roadmap": {"current_day": 2, "total_days": 60},
        "all_pending_tasks": {
            "total_pending": ["task_1", "task_2", "task_3"],
            "tasks": [{"title": "PyTorch Tensors"}, {"title": "CNNs"}]
        },
        "progress": {
            "completed_tasks": ["task_comp_1", "task_comp_2"],
            "completion_rate": 40.0
        }
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: What are my pending tasks?"
    )
    res = _build_grounded_mentor_response(prompt)
    assert res["answer"] is not None
    assert "3" in res["answer"]


def test_regression_missing_and_null_context():
    """Verify mentor handles completely missing or explicitly null context objects gracefully."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "DevOps Engineer",
        "roadmap": None,
        "today_tasks": None,
        "all_pending_tasks": None,
        "progress": None,
        "overdue_tasks": None,
        "yesterday_completed_tasks": None
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: What can I do today?"
    )
    res = _build_grounded_mentor_response(prompt)
    assert res["answer"] is not None
    assert isinstance(res["evidence"], list)


def test_regression_malformed_context_types():
    """Verify mentor handles malformed context data types (strings, unexpected types) without raising unhandled TypeErrors."""
    from app.services.llm_service import _build_grounded_mentor_response
    import json
    ctx = {
        "target_role": "Data Analyst",
        "roadmap": "invalid_roadmap_string",
        "all_pending_tasks": "not_a_dict",
        "progress": "not_a_dict",
        "today_tasks": 12345,
        "overdue_tasks": False
    }
    prompt = (
        f"=== STUDENT CONTEXT ===\n"
        f"{json.dumps(ctx)}\n\n"
        f"=== CURRENT QUESTION ===\n"
        f"STUDENT: Why are 84 tasks pending?"
    )
    res = _build_grounded_mentor_response(prompt)
    assert res["answer"] is not None
    assert "84" in res["answer"]

