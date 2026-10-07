from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ProjectAnalyzeRequest(BaseModel):
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    category: Optional[str] = Field(None, description="Project domain category")
    role: Optional[str] = Field(None, description="Student's role in the project")
    duration: Optional[Dict[str, Any]] = Field(None, description="Project duration")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    features: List[str] = Field(default_factory=list, description="Project features")
    achievements: List[str] = Field(default_factory=list, description="Project achievements")
    architectureTags: List[str] = Field(default_factory=list, description="Architecture tags")
    github_url: Optional[str] = Field(None, description="GitHub repository URL")
    githubUrl: Optional[str] = Field(None, description="GitHub repository URL alias")
    live_url: Optional[str] = Field(None, description="Live deployment URL")
    liveUrl: Optional[str] = Field(None, description="Live deployment URL alias")
    demo_url: Optional[str] = Field(None, description="Demo video URL")
    code_audit: Optional[Dict[str, Any]] = Field(None, description="Optional existing AST audit metadata")


class ProjectAIAnalysis(BaseModel):
    score: int = Field(88, ge=0, le=100, description="Overall project AST & architectural score")
    score_badge: str = Field("Production Grade", description="Visual badge label e.g. Production Grade")
    complexity_score: int = Field(85, ge=0, le=100, description="Technical complexity depth score")
    architecture_tags: List[str] = Field(default_factory=list, description="Recommended architectural tags")
    evidence_bullets: List[str] = Field(default_factory=list, description="Generated STAR resume evidence bullets")
    strengths: List[str] = Field(default_factory=list, description="Key technical strengths")
    weaknesses: List[str] = Field(default_factory=list, description="System design or documentation gaps")
    recommendations: List[str] = Field(default_factory=list, description="Actionable improvement steps")
    project_type: Optional[str] = Field(None, description="Inferred project classification type")
    code_audit: Optional[Dict[str, Any]] = Field(None, description="AST code audit inspection results")
