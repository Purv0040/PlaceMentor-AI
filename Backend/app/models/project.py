from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ProjectDurationModel(BaseModel):
    """Start and end date representation for project timeline."""
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM or free text)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM, Present, or free text)")


class ProjectLinksModel(BaseModel):
    """Project external URLs."""
    github: Optional[str] = Field(None, description="GitHub repository URL")
    live: Optional[str] = Field(None, description="Live production URL")
    demo: Optional[str] = Field(None, description="Video/Demo URL")


class ProjectGitHubInfoModel(BaseModel):
    """Optional GitHub repository reference."""
    repository_id: Optional[str] = Field(None, description="MongoDB ID of connected GitHub repository")
    repository_url: Optional[str] = Field(None, description="GitHub repository URL")
    connected: bool = Field(False, description="True if project is linked to student's GitHub repo")


class ProjectModel(BaseModel):
    """Pydantic model representing a student portfolio project stored in MongoDB Atlas."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="ID of authenticated user owning the project")

    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Detailed project description")
    category: str = Field("Full Stack / AI", description="Domain category e.g. Full Stack, Backend / Systems, AI / ML")
    role: Optional[str] = Field(None, description="Student's role e.g. Lead Developer, Full Stack Engineer")

    duration: Optional[ProjectDurationModel] = Field(default_factory=ProjectDurationModel)
    technologies: List[str] = Field(default_factory=list, description="Technologies & frameworks used")
    features: List[str] = Field(default_factory=list, description="Key features built")
    achievements: List[str] = Field(default_factory=list, description="Impact or quantifiable achievements")
    architectureTags: List[str] = Field(default_factory=list, description="Architectural tags e.g. Microservices, Pub-Sub")

    links: Optional[ProjectLinksModel] = Field(default_factory=ProjectLinksModel)
    githubUrl: Optional[str] = Field(None, description="GitHub URL shorthand for frontend rendering")
    liveUrl: Optional[str] = Field(None, description="Live demo URL shorthand for frontend rendering")
    github: Optional[ProjectGitHubInfoModel] = Field(default_factory=ProjectGitHubInfoModel)

    status: str = Field("active", description="Project status: active or archived")
    is_featured: bool = Field(False, description="True if highlighted as featured project")

    score: int = Field(85, description="AST System Complexity score (0-100)")
    scoreBadge: str = Field("Production Grade", description="Score badge label")
    complexityScore: int = Field(85, description="Technical depth complexity score")
    evidenceBullets: List[str] = Field(default_factory=list, description="Generated STAR resume evidence bullets")

    analysis: Optional[Dict[str, Any]] = Field(None, description="AI Project Intelligence analysis payload")
    analysis_status: str = Field("not_analyzed", description="Status: not_analyzed, analyzing, completed, failed, stale")
    analysis_version: Optional[str] = Field("1.0", description="Version of AI analysis schema")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
