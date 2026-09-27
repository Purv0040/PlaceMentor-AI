from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CommunicationAnalysisModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    analysis_id: str
    user_id: str
    question: str
    answer: str
    clarity: int = 75
    structure: int = 75
    conciseness: int = 75
    technical_explanation: int = 75
    confidence_indicators: int = 75
    filler_words_count: int = 0
    speaking_pace_wpm: int = 145
    overall_score: int = 75
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    improved_answer_structure: str = ""
    actionable_suggestions: List[str] = Field(default_factory=list)
    coaching_feedback: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
