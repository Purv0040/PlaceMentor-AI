from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CategoryScoreSchema(BaseModel):
    category: str = Field(..., example="Resume")
    key: Optional[str] = Field(None, example="resume")
    score: Optional[int] = Field(None, ge=0, le=100, example=78)
    weight: float = Field(..., example=0.15)
    weighted_score: float = Field(..., example=11.7)
    confidence: float = Field(..., example=0.85)
    status: str = Field(..., example="scored")
    evidence: List[str] = Field(default_factory=list, example=["ATS score 84/100"])
    missing_data: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class RoleAlignmentSchema(BaseModel):
    role: str = Field(..., example="Backend Developer")
    aligned_skills: List[str] = Field(default_factory=list, example=["Python", "FastAPI"])
    missing_skills: List[str] = Field(default_factory=list, example=["Docker", "Kubernetes"])
    role_alignment_score: Optional[int] = Field(None, example=75)
    status: Optional[str] = Field("scored", example="scored")
    message: Optional[str] = Field(None, example="Target role alignment evaluated.")


class DataCompletenessSchema(BaseModel):
    profile: bool = True
    resume: bool = True
    github: bool = True
    leetcode: bool = True
    projects: bool = True
    communication: bool = False
    interviews: bool = False


class StaleDataItemSchema(BaseModel):
    source: str = Field(..., example="github")
    last_updated: Optional[str] = Field(None, example="2026-09-01T00:00:00Z")
    message: str = Field(..., example="GitHub data has not been synchronized in 14 days.")


class ReadinessWeightsSchema(BaseModel):
    resume: float = Field(0.15, ge=0.0, le=1.0)
    dsa: float = Field(0.20, ge=0.0, le=1.0)
    projects: float = Field(0.20, ge=0.0, le=1.0)
    github: float = Field(0.10, ge=0.0, le=1.0)
    cs_fundamentals: float = Field(0.15, ge=0.0, le=1.0)
    communication: float = Field(0.10, ge=0.0, le=1.0)
    interview: float = Field(0.10, ge=0.0, le=1.0)


class ReadinessAnalyzeRequest(BaseModel):
    target_role: Optional[str] = Field(None, example="Backend Developer")
    weights: Optional[ReadinessWeightsSchema] = None


class ReadinessResponse(BaseModel):
    id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    user_id: str = Field(..., example="user_123")

    target_role: str = Field(..., example="Backend Developer")
    overall_score: Optional[int] = Field(None, example=76)
    overall_confidence: float = Field(..., example=0.82)
    readiness_label: str = Field(..., example="Advanced")

    categories: Dict[str, CategoryScoreSchema] = Field(default_factory=dict)
    weights_used: Dict[str, float] = Field(default_factory=dict)

    scored_categories_count: int = Field(5)
    insufficient_categories_count: int = Field(2)

    strengths: List[str] = Field(default_factory=list)
    key_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    role_alignment: Optional[RoleAlignmentSchema] = None
    data_completeness: Optional[DataCompletenessSchema] = None
    stale_data: List[StaleDataItemSchema] = Field(default_factory=list)
    provenance: Optional[Dict[str, Any]] = Field(default_factory=dict)

    calculation_version: str = Field("1.0")
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReadinessSingleResponse(BaseModel):
    success: bool = True
    message: str = "Placement readiness retrieved successfully"
    data: ReadinessResponse


class ReadinessSummaryResponse(BaseModel):
    success: bool = True
    message: str = "Placement readiness summary retrieved"
    data: Dict[str, Any]


class ReadinessHistoryResponse(BaseModel):
    success: bool = True
    total: int = Field(..., example=1)
    data: List[ReadinessResponse] = Field(default_factory=list)
