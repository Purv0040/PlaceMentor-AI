from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SkillGapAnalyzeRequest(BaseModel):
    """Request payload for POST /api/v1/skill-gaps/analyze."""
    target_role: Optional[str] = Field(
        None,
        description="Optional target role override (e.g. 'AI/ML Engineer', 'Backend Developer', 'Full Stack Developer')"
    )


class SkillItemSchema(BaseModel):
    skill: str
    category: str = "Programming"
    required: bool = True
    importance: str = "medium"
    required_level: str = "Intermediate"
    required_level_num: int = 2
    current_level: str = "Untested"
    current_level_num: int = 0
    gap_type: str = "missing"
    gap_severity: str = "None"
    priority: str = "Low"
    evidence_level: str = "none"
    evidence: List[str] = Field(default_factory=list)
    reason: Optional[str] = None
    recommended_action: Optional[str] = None
    action_label: Optional[str] = "Add to Roadmap"
    action_route: Optional[str] = "/roadmap"


class PriorityGapSchema(BaseModel):
    id: str
    skill: str
    category: str = "Backend"
    gap_type: str = "missing"
    priority: str = "High"
    importance: str = "high"
    current_level: str = "Untested"
    current_level_text: Optional[str] = None
    required_level: str = "Intermediate"
    required_level_text: Optional[str] = None
    reason: str
    suggested_action: str
    action_label: str = "Add to Roadmap"
    action_route: str = "/roadmap"


class SkillGapSummarySchema(BaseModel):
    total_required_skills: int = 0
    skills_aligned: int = 0
    skills_developing: int = 0
    skills_weak: int = 0
    skills_missing: int = 0


class CategoryCoverageSchema(BaseModel):
    category: str
    coverage: int
    color: str = "#8083ff"


class Matrix2x2ItemSchema(BaseModel):
    skill: str
    category: str


class Matrix2x2Schema(BaseModel):
    quick_wins: List[Matrix2x2ItemSchema] = Field(default_factory=list)
    major_projects: List[Matrix2x2ItemSchema] = Field(default_factory=list)
    fill_ins: List[Matrix2x2ItemSchema] = Field(default_factory=list)
    hard_long_term: List[Matrix2x2ItemSchema] = Field(default_factory=list)


class RecommendationItemSchema(BaseModel):
    title: str
    description: str
    action_label: str = "View 90-Day Roadmap"
    action_route: str = "/roadmap"


class StaleDataQualitySchema(BaseModel):
    source: str
    last_updated: Optional[str] = None
    message: str


class SkillGapResponse(BaseModel):
    """Full skill gap analysis response."""
    id: str
    user_id: str
    target_role: str
    overall_coverage: int
    confidence_index: str = "95.0%"
    total_audited: int
    summary: SkillGapSummarySchema
    category_coverage: List[CategoryCoverageSchema] = Field(default_factory=list)
    skills: List[SkillItemSchema] = Field(default_factory=list)
    priority_gaps: List[PriorityGapSchema] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    recommendations: List[RecommendationItemSchema] = Field(default_factory=list)
    matrix2x2: Matrix2x2Schema = Field(default_factory=Matrix2x2Schema)
    data_quality: Dict[str, bool] = Field(default_factory=dict)
    stale_data: List[StaleDataQualitySchema] = Field(default_factory=list)
    ai_summary: Optional[str] = None
    analysis_version: str = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class SkillGapSummaryResponse(BaseModel):
    """Dashboard-friendly lightweight summary response."""
    user_id: str
    target_role: str
    overall_coverage: int
    confidence_index: str = "95.0%"
    total_audited: int
    gaps_identified_count: int
    summary: SkillGapSummarySchema
    top_priority_gaps: List[PriorityGapSchema] = Field(default_factory=list)
    updated_at: Optional[datetime] = None


class SkillGapHistoryResponse(BaseModel):
    """Historical calculation list response."""
    items: List[SkillGapResponse]
    total: int
