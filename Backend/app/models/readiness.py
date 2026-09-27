from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CategoryScoreModel(BaseModel):
    category: str = Field(..., description="Category name (e.g. Resume, DSA, Projects, GitHub, CS Fundamentals, Communication, Interview)")
    score: Optional[int] = Field(None, ge=0, le=100, description="Category score out of 100")
    weight: float = Field(..., ge=0.0, le=1.0, description="Configured weight for this category")
    weighted_score: float = Field(0.0, description="Weighted contribution to overall score")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence based on evidence completeness")
    status: str = Field("insufficient_data", description="'scored' or 'insufficient_data'")
    evidence: List[str] = Field(default_factory=list, description="Evidence driving category score")
    missing_data: List[str] = Field(default_factory=list, description="Missing signals or recommendations")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")


class RoleAlignmentModel(BaseModel):
    role: str = Field(..., description="Target placement role")
    aligned_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


class DataCompletenessModel(BaseModel):
    profile: bool = False
    resume: bool = False
    github: bool = False
    leetcode: bool = False
    projects: bool = False
    communication: bool = False
    interviews: bool = False


class StaleDataItemModel(BaseModel):
    source: str = Field(..., description="Source module e.g. github, leetcode, resume")
    last_updated: Optional[str] = None
    message: str = Field(..., description="Warning message for stale data")


class ReadinessAnalysisModel(BaseModel):
    """Document model representing a student's Placement Readiness Analysis in MongoDB Atlas."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="ID of authenticated user owning the analysis")

    target_role: str = Field("Backend Developer", description="Student's target placement role")
    overall_score: Optional[int] = Field(None, ge=0, le=100, description="Normalized overall readiness score (0-100)")
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall weighted confidence")
    readiness_label: str = Field("Insufficient Evidence", description="Label: Placement Ready, Advanced, Developing, Needs Work, Insufficient Evidence")

    categories: Dict[str, CategoryScoreModel] = Field(default_factory=dict, description="Detailed category score models")
    weights_used: Dict[str, float] = Field(default_factory=dict, description="Normalized category weights map")

    scored_categories_count: int = Field(0)
    insufficient_categories_count: int = Field(0)

    strengths: List[str] = Field(default_factory=list, description="Key preparation strengths")
    key_gaps: List[str] = Field(default_factory=list, description="Priority preparation gaps")
    recommendations: List[str] = Field(default_factory=list, description="Holistic remediation recommendations")

    role_alignment: Optional[RoleAlignmentModel] = None
    data_completeness: Optional[DataCompletenessModel] = Field(default_factory=DataCompletenessModel)
    stale_data: List[StaleDataItemModel] = Field(default_factory=list)

    calculation_version: str = Field("1.0", description="Version of readiness scoring algorithm")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
