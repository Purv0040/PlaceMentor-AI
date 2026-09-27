from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CommunicationAnalyzeRequestSchema(BaseModel):
    question: str = Field(..., description="Prompt or interview question being answered")
    answer: str = Field(..., min_length=1, description="Student answer text to analyze")


class CommunicationResponseSchema(BaseModel):
    id: str
    analysis_id: str
    user_id: str
    question: str
    answer: str
    clarity: int
    structure: int
    conciseness: int
    technical_explanation: int
    confidence_indicators: int
    filler_words_count: int
    speaking_pace_wpm: int
    overall_score: int
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    improved_answer_structure: str = ""
    actionable_suggestions: List[str] = Field(default_factory=list)
    coaching_feedback: str = ""
    created_at: datetime


class CommunicationSummaryResponseSchema(BaseModel):
    user_id: str
    total_analyses: int = 0
    average_overall_score: float = 0.0
    average_clarity: float = 0.0
    average_structure: float = 0.0
    average_conciseness: float = 0.0
    average_speaking_pace: float = 145.0
    recurring_improvements: List[str] = Field(default_factory=list)
    top_strengths: List[str] = Field(default_factory=list)


# Backward compatibility
CommunicationAssessmentResponse = CommunicationResponseSchema
