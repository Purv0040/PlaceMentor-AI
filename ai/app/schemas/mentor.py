"""
Pydantic schemas for the Personal AI Placement Mentor.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StudentContext(BaseModel):
    """Encapsulates the student's actual placement context."""
    target_role: Optional[str] = Field(None, description="Target placement role")
    profile: Optional[Dict[str, Any]] = Field(None, description="StudentIntelligenceProfile data")
    resume_analysis: Optional[Dict[str, Any]] = Field(None, description="ResumeAnalysis data")
    github_analysis: Optional[Dict[str, Any]] = Field(None, description="GitHubAnalysis data")
    leetcode_analysis: Optional[Dict[str, Any]] = Field(None, description="LeetCodeAnalysis data")
    projects: Optional[List[Dict[str, Any]]] = Field(None, description="Extracted projects data")
    skill_gaps: Optional[Dict[str, Any]] = Field(None, description="SkillGapAnalysis data")
    readiness: Optional[Dict[str, Any]] = Field(None, description="PlacementReadinessAnalysis data")
    roadmap: Optional[Dict[str, Any]] = Field(None, description="PersonalizedRoadmap data")
    today_tasks: Optional[Dict[str, Any]] = Field(None, description="TodayTasksResponse data")
    progress: Optional[Dict[str, Any]] = Field(None, description="StudentProgressPayload data")
    interview_results: Optional[List[Dict[str, Any]]] = Field(None, description="Mock interview results")
    communication_results: Optional[List[Dict[str, Any]]] = Field(None, description="Communication skill results")


class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")


class MentorChatRequest(BaseModel):
    """Input payload for POST /api/ai/mentor/chat."""
    message: str = Field(..., description="The student's new question or message")
    student_context: StudentContext = Field(..., description="The student's actual placement context")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list, 
        description="Previous conversation turns for context (optional)"
    )


class MentorChatResponse(BaseModel):
    """Validated, structured response from the Mentor."""
    answer: str = Field(..., description="The mentor's direct answer to the student")
    evidence: List[str] = Field(
        default_factory=list, 
        description="Specific facts from the student's context supporting the answer"
    )
    recommended_actions: List[str] = Field(
        default_factory=list, 
        description="Actionable next steps for the student"
    )
    related_skills: List[str] = Field(
        default_factory=list, 
        description="Relevant skills related to the question"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence in the answer (e.g. 0.0 if missing context)"
    )
