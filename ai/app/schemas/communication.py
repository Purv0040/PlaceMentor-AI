from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AICommunicationAnalyzeRequest(BaseModel):
    question: str = Field(..., description="Prompt or interview question")
    answer: str = Field(..., description="Student spoken or written answer text")
    target_role: Optional[str] = Field(None, description="Optional target role context")


class AICommunicationAnalysisResult(BaseModel):
    clarity: int = Field(..., ge=0, le=100)
    structure: int = Field(..., ge=0, le=100)
    conciseness: int = Field(..., ge=0, le=100)
    technical_explanation: int = Field(..., ge=0, le=100)
    confidence_indicators: int = Field(..., ge=0, le=100)
    filler_words_count: int = Field(0, ge=0)
    speaking_pace_wpm: int = Field(145, ge=50, le=250)
    overall_score: int = Field(..., ge=0, le=100)
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    improved_answer_structure: str = ""
    actionable_suggestions: List[str] = Field(default_factory=list)
    coaching_feedback: str = ""
