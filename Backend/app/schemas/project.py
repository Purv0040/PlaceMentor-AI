from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator


class ProjectDurationSchema(BaseModel):
    start_date: Optional[str] = Field(None, example="2025-01")
    end_date: Optional[str] = Field(None, example="Present")


class ProjectLinksSchema(BaseModel):
    github: Optional[str] = Field(None, example="https://github.com/user/repo")
    live: Optional[str] = Field(None, example="https://project.demo.app")
    demo: Optional[str] = Field(None, example="https://youtube.com/watch?v=123")


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, example="PlaceMentor AI — SDE Placement Copilot")
    description: str = Field(..., min_length=5, max_length=3000, example="Full-stack AI placement mentoring platform featuring AST code audit.")
    category: Optional[str] = Field("Full Stack / AI", example="Full Stack / AI")
    role: Optional[str] = Field(None, example="Lead Developer")

    duration: Optional[ProjectDurationSchema] = None
    technologies: List[str] = Field(default_factory=list, example=["React", "FastAPI", "Python", "MongoDB"])
    features: List[str] = Field(default_factory=list, example=["ATS Resume Scanner", "AST Code Auditor"])
    achievements: List[str] = Field(default_factory=list, example=["Handled 1,000+ API queries with sub-200ms response time"])
    architectureTags: List[str] = Field(default_factory=list, example=["Microservices", "REST API", "JWT Auth"])

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = Field(None, example="https://github.com/Purv0040/PlaceMentor-AI")
    liveUrl: Optional[str] = Field(None, example="https://placementor-ai.demo.app")
    is_featured: bool = Field(False, example=False)


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, min_length=5, max_length=3000)
    category: Optional[str] = None
    role: Optional[str] = None

    duration: Optional[ProjectDurationSchema] = None
    technologies: Optional[List[str]] = None
    features: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    architectureTags: Optional[List[str]] = None

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = None
    liveUrl: Optional[str] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = Field(None, example="active")


class ProjectFeaturedRequest(BaseModel):
    is_featured: bool = Field(..., example=True)


class ProjectResponse(BaseModel):
    id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    user_id: str = Field(..., example="user_123")

    title: str = Field(..., example="PlaceMentor AI — SDE Placement Copilot")
    description: str = Field(..., example="Full-stack AI placement mentoring platform.")
    category: str = Field("Full Stack / AI", example="Full Stack / AI")
    role: Optional[str] = None

    duration: Optional[ProjectDurationSchema] = None
    technologies: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    architectureTags: List[str] = Field(default_factory=list)

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = None
    liveUrl: Optional[str] = None

    status: str = Field("active")
    is_featured: bool = Field(False)

    score: int = Field(85)
    scoreBadge: str = Field("Production Grade")
    complexityScore: int = Field(85)
    evidenceBullets: List[str] = Field(default_factory=list)

    analysis: Optional[Dict[str, Any]] = None
    analysis_status: str = Field("not_analyzed")
    analysis_version: Optional[str] = Field("1.0")

    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectListResponse(BaseModel):
    success: bool = True
    total: int = Field(..., example=4)
    data: List[ProjectResponse] = Field(default_factory=list)


class ProjectSingleResponse(BaseModel):
    success: bool = True
    message: str = "Project retrieved successfully"
    data: ProjectResponse


class ProjectAnalysisResponse(BaseModel):
    success: bool = True
    message: str = "Project analysis completed successfully"
    data: Dict[str, Any]
