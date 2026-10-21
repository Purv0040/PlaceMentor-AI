from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AIInterviewQuestionRequest(BaseModel):
    target_role: str = Field(..., description="Target role e.g. Backend Developer")
    interview_type: str = Field(..., description="hr, technical, behavioral, project, dsa, system_design")
    difficulty: str = Field("medium", description="easy, medium, hard")
    question_number: int = Field(1, ge=1)
    total_questions: int = Field(5, ge=1, le=20)
    previous_qa: List[Dict[str, Any]] = Field(default_factory=list, description="History of previous Q&A in this session")
    student_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Profile, resume, projects, github, leetcode evidence")


class AIInterviewQuestionResponse(BaseModel):
    question_id: str
    question_number: int
    question: str
    category: str
    skill: str
    difficulty: str
    expected_focus: str
    hint: Optional[str] = None


class AIInterviewAnswerEvaluateRequest(BaseModel):
    question: str
    category: str
    skill: str
    difficulty: str
    expected_focus: str
    answer: str
    previous_qa: List[Dict[str, Any]] = Field(default_factory=list)
    student_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    question_number: int = Field(1)
    total_questions: int = Field(5)


class AIInterviewAnswerEvaluation(BaseModel):
    score: int = Field(..., ge=0, le=100)
    correctness: int = Field(..., ge=0, le=100)
    relevance: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    depth: int = Field(..., ge=0, le=100)
    technical_accuracy: int = Field(..., ge=0, le=100)
    communication_quality: int = Field(..., ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    ai_feedback: str = ""
    follow_up_needed: bool = False
    suggested_next_topic: Optional[str] = None


class AIInterviewCompleteRequest(BaseModel):
    target_role: str
    interview_type: str
    qna_history: List[Dict[str, Any]] = Field(default_factory=list)
    student_context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AIInterviewSummaryEvaluation(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    category_scores: Dict[str, int] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    technical_gaps: List[str] = Field(default_factory=list)
    communication_feedback: Dict[str, Any] = Field(default_factory=dict)
    overall_feedback: str = ""
