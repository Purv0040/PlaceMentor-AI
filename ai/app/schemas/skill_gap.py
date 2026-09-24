"""
Pydantic schemas for the Skill Gap Engine.
Defines role requirements, individual skill gaps, and the complete SkillGapAnalysis result.
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from app.schemas.skills import StudentIntelligenceProfile, ProfileBuildRequest


class RoleSkillRequirement(BaseModel):
    """A single skill requirement for a target role."""
    skill: str = Field(..., description="Canonical name of the required skill (e.g. 'Python', 'Docker')")
    required_level: str = Field(
        ...,
        description="Required level: 'Beginner', 'Intermediate', 'Advanced', 'Expert'"
    )
    importance: str = Field(
        ...,
        description="Importance for the role: 'critical', 'high', 'medium', 'low'"
    )
    category: str = Field(
        ...,
        description="Category (e.g., 'Programming', 'DSA', 'Backend', 'DevOps')"
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisite skills that should ideally be mastered first"
    )


class SkillGapItem(BaseModel):
    """Individual skill gap calculation result."""
    skill: str = Field(..., description="Canonical skill name")
    current_level: str = Field(..., description="Assessed level: 'Untested', 'Beginner', 'Intermediate', 'Advanced', 'Expert'")
    required_level: str = Field(..., description="Required level for target role")
    gap: str = Field(..., description="Gap severity: 'None', 'Low', 'Medium', 'High', 'Critical'")
    priority: str = Field(..., description="Calculated priority: 'High', 'Medium', 'Low'")
    importance: str = Field(..., description="Role importance: 'critical', 'high', 'medium', 'low'")
    category: str = Field(..., description="Skill category")
    evidence: List[str] = Field(default_factory=list, description="Evidence points supporting current level and gap assessment")
    explanation: Optional[str] = Field(None, description="Concise rationale explaining why this gap matters for the target role")
    recommended_action: Optional[str] = Field(None, description="Actionable recommendation to bridge this skill gap")


class SkillGapAnalysis(BaseModel):
    """Complete Skill Gap Analysis output for a target role."""
    target_role: str = Field(..., description="Canonical target role name")
    skills: List[SkillGapItem] = Field(default_factory=list, description="All evaluated skill gaps for the target role")
    high_priority: List[str] = Field(default_factory=list, description="Skill names categorized as High priority")
    medium_priority: List[str] = Field(default_factory=list, description="Skill names categorized as Medium priority")
    low_priority: List[str] = Field(default_factory=list, description="Skill names categorized as Low priority")
    summary: str = Field(..., description="Executive summary of the skill gap analysis")
    evidence: List[str] = Field(default_factory=list, description="Overall evidence highlights driving the analysis")


class SkillGapRequest(BaseModel):
    """Input payload for POST /api/ai/skills/analyze."""
    target_role: str = Field(..., description="Target role name (e.g., 'AI/ML Engineer', 'Backend Developer')")
    profile: Optional[Any] = Field(
        None,
        description="Pre-computed StudentIntelligenceProfile or dict payload"
    )
    profile_request: Optional[ProfileBuildRequest] = Field(
        None,
        description="Optional raw payload to build profile on the fly if profile is not supplied"
    )
