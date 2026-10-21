from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class InterviewCreateSchema(BaseModel):
    interview_type: str = Field(default="technical", description="hr, technical, behavioral, project, dsa, system_design")
    difficulty: str = Field(default="medium", description="easy, medium, hard")
    question_count: int = Field(default=5, ge=1, le=10)
    target_role: Optional[str] = Field(default=None, description="Optional target role override")


class InterviewAnswerSchema(BaseModel):
    answer: str = Field(..., min_length=1, description="Candidate response text")


class InterviewQuestionResponseSchema(BaseModel):
    id: str
    question_id: str
    interview_id: str
    question_number: int
    total_questions: int = 5
    question: str
    category: str
    skill: str
    difficulty: str
    expected_focus: str
    hint: Optional[str] = None
    answer: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    created_at: datetime


class InterviewSessionResponseSchema(BaseModel):
    id: str
    interview_id: str
    user_id: str
    target_role: str
    interview_type: str
    difficulty: str
    status: str  # created, active, completed, abandoned
    total_questions: int
    current_question: int
    current_question_data: Optional[InterviewQuestionResponseSchema] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[int] = None
    category_scores: Dict[str, int] = Field(default_factory=dict)
    evaluation: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class InterviewResultResponseSchema(BaseModel):
    interview_id: str
    target_role: str
    interview_type: str
    overall_score: int
    category_scores: Dict[str, int] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    technical_gaps: List[str] = Field(default_factory=list)
    communication_feedback: Dict[str, Any] = Field(default_factory=dict)
    completed_at: datetime


# Aliases for backward compatibility
MockInterviewSession = InterviewSessionResponseSchema
InterviewFeedbackResponse = InterviewResultResponseSchema
