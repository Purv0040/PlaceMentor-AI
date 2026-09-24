"""
Pydantic schemas for the Placement Readiness Engine.
Defines category weights, individual category readiness scores, historical snapshots, and overall readiness analysis.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator

from app.schemas.student import StudentProfile
from app.schemas.resume import ResumeAnalysis
from app.schemas.github import GitHubAnalysis
from app.schemas.leetcode import LeetCodeAnalysis
from app.schemas.skills import StudentIntelligenceProfile
from app.schemas.skill_gap import SkillGapAnalysis


class ReadinessWeights(BaseModel):
    """
    Configurable category weightings for placement readiness scoring.
    Default weights sum to 1.0.
    """
    resume: float = Field(0.15, ge=0.0, le=1.0, description="Weight for Resume ATS & quality score")
    dsa: float = Field(0.20, ge=0.0, le=1.0, description="Weight for Data Structures & Algorithms score")
    projects: float = Field(0.20, ge=0.0, le=1.0, description="Weight for Portfolio Projects score")
    github: float = Field(0.10, ge=0.0, le=1.0, description="Weight for GitHub repository depth & activity")
    cs_fundamentals: float = Field(0.15, ge=0.0, le=1.0, description="Weight for CS Fundamentals (OS, DBMS, Networks, OOP)")
    communication: float = Field(0.10, ge=0.0, le=1.0, description="Weight for Technical Communication & Documentation")
    interview: float = Field(0.10, ge=0.0, le=1.0, description="Weight for Mock Interview performance")

    def get_raw_weights_map(self) -> Dict[str, float]:
        return {
            "Resume": self.resume,
            "DSA": self.dsa,
            "Projects": self.projects,
            "GitHub": self.github,
            "CS Fundamentals": self.cs_fundamentals,
            "Communication": self.communication,
            "Interview": self.interview,
        }


class CategoryReadinessScore(BaseModel):
    """
    Evaluation result for a single readiness category.
    Strictly separates score, confidence, status, and evidence.
    """
    category: str = Field(..., description="Category name (e.g., 'Resume', 'DSA', 'GitHub')")
    score: Optional[int] = Field(None, ge=0, le=100, description="Calculated category score (0-100) if evidence exists")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence rating based on evidence depth")
    status: str = Field(..., description="'scored' if sufficient data exists, else 'insufficient_data'")
    evidence: List[str] = Field(default_factory=list, description="Concrete evidence strings driving this category's evaluation")


class ReadinessScoreSnapshot(BaseModel):
    """
    Historical snapshot model for storing readiness scores over time.
    """
    timestamp: str = Field(..., description="ISO 8601 timestamp of score calculation")
    overall_score: Optional[int] = Field(None, description="Overall weighted readiness score (0-100)")
    overall_confidence: float = Field(0.0, description="Overall confidence (0.0-1.0)")
    readiness_label: str = Field("Insufficient Evidence", description="Readiness label")
    category_scores: Dict[str, CategoryReadinessScore] = Field(default_factory=dict, description="Snapshotted category scores")


class PlacementReadinessAnalysis(BaseModel):
    """
    Complete Placement Readiness Analysis output.
    """
    target_role: str = Field(..., description="Target placement role name")
    overall_score: Optional[int] = Field(None, description="Normalized weighted overall readiness score out of 100")
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Weighted average confidence across scored categories")
    readiness_label: str = Field(..., description="'Placement Ready', 'Advanced', 'Developing', 'Needs Work', 'Insufficient Evidence'")
    categories: Dict[str, CategoryReadinessScore] = Field(default_factory=dict, description="Category scores mapped by category name")
    weights_used: Dict[str, float] = Field(default_factory=dict, description="Normalized weights applied for each category")
    scored_categories_count: int = Field(0, description="Number of categories with sufficient evidence ('scored')")
    insufficient_categories_count: int = Field(0, description="Number of categories with 'insufficient_data'")
    strengths: List[str] = Field(default_factory=list, description="Top evidence-backed readiness strengths")
    key_gaps: List[str] = Field(default_factory=list, description="Top readiness gaps to address")
    historical_snapshot: ReadinessScoreSnapshot = Field(..., description="Historical snapshot payload for progress tracking")
    scoring_formula_explanation: str = Field(..., description="Transparent explanation of the weighted score normalization formula")


class ReadinessCalculateRequest(BaseModel):
    """
    Input payload for POST /api/ai/readiness/calculate.
    """
    target_role: str = Field("Backend Developer", description="Target role name")
    weights: Optional[ReadinessWeights] = Field(default_factory=ReadinessWeights, description="Custom category weights configuration")
    resume_analysis: Optional[ResumeAnalysis] = None
    github_analysis: Optional[GitHubAnalysis] = None
    leetcode_analysis: Optional[LeetCodeAnalysis] = None
    student_profile: Optional[StudentProfile] = None
    profile: Optional[Any] = Field(None, description="Pre-computed StudentIntelligenceProfile or dict")
    skill_gap_analysis: Optional[Any] = Field(None, description="Pre-computed SkillGapAnalysis or dict")
    interview_data: Optional[Dict[str, Any]] = Field(None, description="Optional mock/live interview assessment data")
