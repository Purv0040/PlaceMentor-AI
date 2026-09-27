from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class InterviewQuestionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    question_id: str
    interview_id: str
    user_id: str
    question_number: int
    question: str
    category: str
    skill: str
    difficulty: str
    expected_focus: str
    hint: Optional[str] = None
    answer: Optional[str] = None
    answer_submitted_at: Optional[datetime] = None
    evaluation: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True


class InterviewSessionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    interview_id: str
    user_id: str
    target_role: str
    interview_type: str = "technical"  # hr, technical, behavioral, project, dsa, system_design
    difficulty: str = "medium"  # easy, medium, hard
    status: str = "created"  # created, active, completed, abandoned
    total_questions: int = 5
    current_question: int = 1
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    overall_score: Optional[int] = None
    category_scores: Dict[str, int] = Field(default_factory=dict)
    evaluation: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
