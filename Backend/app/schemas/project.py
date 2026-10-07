from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl


class ProjectDurationSchema(BaseModel):
    start_date: Optional[str] = Field(None, example="2025-01")
    end_date: Optional[str] = Field(None, example="Present")


class ProjectLinksSchema(BaseModel):
    github: Optional[str] = Field(None, example="https://github.com/example/project-repo")
    live: Optional[str] = Field(None, example="https://project.demo.app")
    demo: Optional[str] = Field(None, example="https://youtube.com/watch?v=123")


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, example="Student Portfolio Website")
    description: str = Field(..., min_length=5, max_length=3000, example="Personal portfolio application displaying projects, skills, and resume details.")
    category: Optional[str] = Field("Full Stack", example="Full Stack")
    role: Optional[str] = Field(None, example="Full Stack Developer")

    duration: Optional[ProjectDurationSchema] = None
    technologies: List[str] = Field(default_factory=list, example=["React", "FastAPI", "Python", "MongoDB"])
    features: List[str] = Field(default_factory=list, example=["User Authentication", "Project Dashboard"])
    achievements: List[str] = Field(default_factory=list, example=["Deployed interactive application with responsive UI"])
    architectureTags: List[str] = Field(default_factory=list, example=["REST API", "Modular Architecture"])

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = Field(None, example="https://github.com/example/project-repo")
    liveUrl: Optional[str] = Field(None, example="https://project.demo.app")
    is_featured: bool = Field(False, example=False)


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150, example="Student Portfolio Website")
    description: Optional[str] = Field(None, min_length=5, max_length=3000, example="Updated portfolio application with enhanced features.")
    category: Optional[str] = Field(None, example="Full Stack")
    role: Optional[str] = Field(None, example="Full Stack Developer")

    duration: Optional[ProjectDurationSchema] = None
    technologies: Optional[List[str]] = Field(None, example=["React", "FastAPI", "Python", "MongoDB"])
    features: Optional[List[str]] = Field(None, example=["User Authentication"])
    achievements: Optional[List[str]] = Field(None, example=["Deployed interactive application"])
    architectureTags: Optional[List[str]] = Field(None, example=["REST API"])

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = Field(None, example="https://github.com/example/project-repo")
    liveUrl: Optional[str] = Field(None, example="https://project.demo.app")
    is_featured: Optional[bool] = Field(None, example=True)
    status: Optional[str] = Field(None, example="active")


class ProjectFeaturedRequest(BaseModel):
    is_featured: bool = Field(..., example=True)


class ProjectCodeAudit(BaseModel):
    status: str = Field("not_available", example="not_available", description="Audit execution status e.g. audited, not_available, failed")
    reason: Optional[str] = Field("No accessible source repository was provided.", example="No accessible source repository was provided.", description="Explanation when status is not_available")
    repository: Optional[str] = Field(None, example=None)
    primary_language: Optional[str] = Field(None, example=None)
    stars: Optional[int] = Field(None, example=None)
    default_branch: Optional[str] = Field(None, example=None)
    has_tests: Optional[bool] = Field(None, example=None)
    has_docker: Optional[bool] = Field(None, example=None)
    has_ci_cd: Optional[bool] = Field(None, example=None)
    summary: Optional[str] = Field(None, example=None)


class ProjectAnalysis(BaseModel):
    score: int = Field(82, example=82, ge=0, le=100, description="Overall AST & architectural depth score")
    score_badge: str = Field("Good Evidence", example="Good Evidence", description="Badge classification e.g. Production Grade, System Architect, Good Evidence, Foundational")
    complexity_score: int = Field(76, example=76, ge=0, le=100, description="Technical complexity depth score")
    architecture_tags: List[str] = Field(default_factory=list, example=["Machine Learning", "Data Preprocessing", "Regression"])
    evidence_bullets: List[str] = Field(default_factory=list, example=["Implemented data preprocessing and feature engineering.", "Built and evaluated a regression model."])
    strengths: List[str] = Field(default_factory=list, example=["Clear preprocessing workflow."])
    weaknesses: List[str] = Field(default_factory=list, example=["Cross-validation is not documented."])
    recommendations: List[str] = Field(default_factory=list, example=["Add k-fold cross-validation."])
    project_type: Optional[str] = Field("machine_learning", example="machine_learning", description="Inferred project category type")
    code_audit: Optional[ProjectCodeAudit] = Field(
        default_factory=lambda: ProjectCodeAudit(
            status="not_available",
            reason="No accessible source repository was provided."
        ),
        description="AST repository code audit metrics"
    )


class ProjectResponse(BaseModel):
    id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    user_id: str = Field(..., example="user_123")

    title: str = Field(..., example="Student Portfolio Website")
    description: str = Field(..., example="Personal portfolio application displaying projects.")
    category: str = Field("Full Stack", example="Full Stack")
    role: Optional[str] = Field(None, example="Full Stack Developer")

    duration: Optional[ProjectDurationSchema] = None
    technologies: List[str] = Field(default_factory=list, example=["React", "FastAPI", "Python", "MongoDB"])
    features: List[str] = Field(default_factory=list, example=["User Authentication", "Project Dashboard"])
    achievements: List[str] = Field(default_factory=list, example=["Deployed interactive application"])
    architectureTags: List[str] = Field(default_factory=list, example=["REST API", "Modular Architecture"])

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = Field(None, example="https://github.com/example/project-repo")
    liveUrl: Optional[str] = Field(None, example="https://project.demo.app")

    status: str = Field("active", example="active")
    is_featured: bool = Field(False, example=False)

    score: int = Field(72, example=72)
    scoreBadge: str = Field("Good Evidence", example="Good Evidence")
    complexityScore: int = Field(70, example=70)
    evidenceBullets: List[str] = Field(default_factory=list, example=["Engineered Student Portfolio Website."])

    analysis: Optional[ProjectAnalysis] = Field(None, example=None)
    analysis_status: str = Field("not_analyzed", example="not_analyzed")
    analysis_version: Optional[str] = Field("1.0", example="1.0")

    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectListResponse(BaseModel):
    success: bool = Field(True, example=True)
    total: int = Field(..., example=1)
    data: List[ProjectResponse] = Field(default_factory=list)


class ProjectSingleResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("Project retrieved successfully.", example="Project retrieved successfully.")
    data: ProjectResponse


class ProjectAnalyzeResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("Project analyzed successfully.", example="Project analyzed successfully.")
    data: ProjectResponse


class ProjectAnalysisData(BaseModel):
    project_id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    user_id: str = Field(..., example="user_123")
    analysis_status: str = Field("completed", example="completed")
    analysis_version: str = Field("1.0", example="1.0")
    analyzed_at: Optional[Any] = Field(None, example="2026-10-07T07:07:05Z")
    analysis: ProjectAnalysis


class ProjectAnalysisResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("Project AI analysis report retrieved.", example="Project AI analysis report retrieved.")
    data: ProjectAnalysisData


class ProjectDeleteData(BaseModel):
    project_id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    deleted: bool = Field(True, example=True)


class ProjectDeleteResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("Project removed successfully.", example="Project removed successfully.")
    data: ProjectDeleteData


class ProjectErrorDetail(BaseModel):
    code: str = Field("NOT_FOUND", example="NOT_FOUND")
    message: str = Field("Project not found or access denied.", example="Project not found or access denied.")
    details: Optional[Any] = Field(None, example=None)


class ProjectErrorResponse(BaseModel):
    success: bool = Field(False, example=False)
    error: ProjectErrorDetail
