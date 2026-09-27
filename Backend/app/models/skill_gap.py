from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SkillEvidenceItemModel(BaseModel):
    """Source evidence point for a skill."""
    source: str = Field(..., description="Source of evidence: 'resume', 'projects', 'github', 'leetcode', 'profile'")
    detail: str = Field(..., description="Concrete factual evidence string")
    timestamp: Optional[str] = Field(default=None)


class SkillItemModel(BaseModel):
    """Evaluated skill item with evidence and gap calculation."""
    skill: str = Field(..., description="Canonical skill name")
    category: str = Field(default="Programming", description="Technical engineering category")
    required: bool = Field(default=True, description="Whether skill is required for target role")
    importance: str = Field(default="medium", description="'critical', 'high', 'medium', 'low'")
    required_level: str = Field(default="Intermediate", description="'Beginner', 'Intermediate', 'Advanced', 'Expert'")
    required_level_num: int = Field(default=2, description="1-4 numeric representation")
    current_level: str = Field(default="Untested", description="'Untested', 'Beginner', 'Intermediate', 'Advanced', 'Expert'")
    current_level_num: int = Field(default=0, description="0-4 numeric representation")
    gap_type: str = Field(default="missing", description="'missing', 'weak', 'developing', 'aligned'")
    gap_severity: str = Field(default="None", description="'None', 'Low', 'Medium', 'High', 'Critical'")
    priority: str = Field(default="Low", description="'High', 'Medium', 'Low'")
    evidence_level: str = Field(default="none", description="'none', 'mentioned', 'demonstrated', 'strong_evidence'")
    evidence: List[str] = Field(default_factory=list, description="List of evidence strings")
    reason: Optional[str] = Field(default=None, description="Tier-1 rationale for gap importance")
    recommended_action: Optional[str] = Field(default=None, description="Actionable suggestion to bridge gap")
    action_label: Optional[str] = Field(default="Add to Roadmap", description="UI button action label")
    action_route: Optional[str] = Field(default="/roadmap", description="Internal navigation route")


class PriorityGapModel(BaseModel):
    """Actionable priority gap for high-leverage remediation."""
    id: str = Field(..., description="Unique gap identifier (e.g. 'gap-1')")
    skill: str = Field(..., description="Canonical skill name")
    category: str = Field(default="Backend", description="Skill category")
    gap_type: str = Field(default="missing", description="'missing', 'weak', 'developing'")
    priority: str = Field(default="High", description="'Critical', 'High', 'Medium', 'Low'")
    importance: str = Field(default="high", description="'critical', 'high', 'medium'")
    current_level: str = Field(default="Untested")
    current_level_text: Optional[str] = Field(default=None)
    required_level: str = Field(default="Intermediate")
    required_level_text: Optional[str] = Field(default=None)
    reason: str = Field(..., description="Why this gap matters for candidate placement")
    suggested_action: str = Field(..., description="Specific recommended task or milestone")
    action_label: str = Field(default="Add to Roadmap")
    action_route: str = Field(default="/roadmap")


class SkillGapSummaryModel(BaseModel):
    """Aggregate statistics for skill gap analysis."""
    total_required_skills: int = Field(default=0)
    skills_aligned: int = Field(default=0)
    skills_developing: int = Field(default=0)
    skills_weak: int = Field(default=0)
    skills_missing: int = Field(default=0)


class CategoryCoverageModel(BaseModel):
    """Coverage percentage across an engineering domain."""
    category: str = Field(...)
    coverage: int = Field(..., description="0-100 percentage")
    color: str = Field(default="#8083ff")


class Matrix2x2ItemModel(BaseModel):
    skill: str
    category: str


class Matrix2x2Model(BaseModel):
    quick_wins: List[Matrix2x2ItemModel] = Field(default_factory=list)
    major_projects: List[Matrix2x2ItemModel] = Field(default_factory=list)
    fill_ins: List[Matrix2x2ItemModel] = Field(default_factory=list)
    hard_long_term: List[Matrix2x2ItemModel] = Field(default_factory=list)


class RecommendationItemModel(BaseModel):
    title: str
    description: str
    action_label: str = "View 90-Day Roadmap"
    action_route: str = "/roadmap"


class StaleDataQualityModel(BaseModel):
    source: str
    last_updated: Optional[str] = None
    message: str


class SkillGapAnalysisModel(BaseModel):
    """Full MongoDB Atlas document model for skill_gap_analyses collection."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str = Field(..., index=True)
    target_role: str = Field(default="Backend Developer")
    overall_coverage: int = Field(default=0, description="0-100 coverage percentage")
    confidence_index: str = Field(default="95.0%")
    total_audited: int = Field(default=0)
    summary: SkillGapSummaryModel = Field(default_factory=SkillGapSummaryModel)
    category_coverage: List[CategoryCoverageModel] = Field(default_factory=list)
    skills: List[SkillItemModel] = Field(default_factory=list)
    priority_gaps: List[PriorityGapModel] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    recommendations: List[RecommendationItemModel] = Field(default_factory=list)
    matrix2x2: Matrix2x2Model = Field(default_factory=Matrix2x2Model)
    data_quality: Dict[str, bool] = Field(default_factory=dict)
    stale_data: List[StaleDataQualityModel] = Field(default_factory=list)
    ai_summary: Optional[str] = Field(default=None)
    analysis_version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
