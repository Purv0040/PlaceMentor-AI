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
