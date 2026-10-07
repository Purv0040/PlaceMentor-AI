from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl


class ProjectDurationSchema(BaseModel):
    start_date: Optional[str] = Field(None, example="2025-01")
    end_date: Optional[str] = Field(None, example="Present")


class ProjectLinksSchema(BaseModel):
    github: Optional[str] = Field(None, example="https://github.com/Purv0040/PlaceMentor-AI")
    live: Optional[str] = Field(None, example="https://placementor-ai.demo.app")
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
    title: Optional[str] = Field(None, min_length=2, max_length=150, example="PlaceMentor AI — SDE Placement Copilot")
    description: Optional[str] = Field(None, min_length=5, max_length=3000, example="Updated description with enhanced features.")
    category: Optional[str] = Field(None, example="Full Stack / AI")
    role: Optional[str] = Field(None, example="Lead Developer")

    duration: Optional[ProjectDurationSchema] = None
    technologies: Optional[List[str]] = Field(None, example=["React", "FastAPI", "Python", "MongoDB"])
    features: Optional[List[str]] = Field(None, example=["ATS Resume Scanner"])
    achievements: Optional[List[str]] = Field(None, example=["Handled 1,000+ API queries"])
    architectureTags: Optional[List[str]] = Field(None, example=["Microservices", "REST API"])

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = Field(None, example="https://github.com/Purv0040/PlaceMentor-AI")
    liveUrl: Optional[str] = Field(None, example="https://placementor-ai.demo.app")
    is_featured: Optional[bool] = Field(None, example=True)
    status: Optional[str] = Field(None, example="active")


class ProjectFeaturedRequest(BaseModel):
    is_featured: bool = Field(..., example=True)


class ProjectCodeAudit(BaseModel):
    status: str = Field("not_available", example="not_available", description="Audit execution status e.g. audited, not_available, failed")
    reason: Optional[str] = Field(None, example="No accessible source repository was provided.", description="Explanation when status is not_available")
    repository: Optional[str] = Field(None, example="Purv0040/PlaceMentor-AI")
    primary_language: Optional[str] = Field(None, example="Python")
    stars: Optional[int] = Field(None, example=42)
    default_branch: Optional[str] = Field(None, example="main")
    has_tests: Optional[bool] = Field(None, example=True)
    has_docker: Optional[bool] = Field(None, example=True)
    has_ci_cd: Optional[bool] = Field(None, example=True)
    summary: Optional[str] = Field(None, example="Audited GitHub repository 'Purv0040/PlaceMentor-AI'. Primary language: Python.")


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
    code_audit: Optional[ProjectCodeAudit] = Field(None, description="AST repository code audit metrics")


class ProjectResponse(BaseModel):
    id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    user_id: str = Field(..., example="user_123")

    title: str = Field(..., example="PlaceMentor AI — SDE Placement Copilot")
    description: str = Field(..., example="Full-stack AI placement mentoring platform.")
    category: str = Field("Full Stack / AI", example="Full Stack / AI")
    role: Optional[str] = Field(None, example="Lead Developer")

    duration: Optional[ProjectDurationSchema] = None
    technologies: List[str] = Field(default_factory=list, example=["React", "FastAPI", "Python", "MongoDB"])
    features: List[str] = Field(default_factory=list, example=["ATS Resume Scanner", "AST Code Auditor"])
    achievements: List[str] = Field(default_factory=list, example=["Handled 1,000+ API queries with sub-200ms response time"])
    architectureTags: List[str] = Field(default_factory=list, example=["Microservices", "REST API", "JWT Auth"])

    links: Optional[ProjectLinksSchema] = None
    githubUrl: Optional[str] = Field(None, example="https://github.com/Purv0040/PlaceMentor-AI")
    liveUrl: Optional[str] = Field(None, example="https://placementor-ai.demo.app")

    status: str = Field("active", example="active")
    is_featured: bool = Field(False, example=False)

    score: int = Field(85, example=85)
    scoreBadge: str = Field("Production Grade", example="Production Grade")
    complexityScore: int = Field(85, example=85)
    evidenceBullets: List[str] = Field(default_factory=list, example=["Engineered PlaceMentor AI platform."])

    analysis: Optional[ProjectAnalysis] = None
    analysis_status: str = Field("not_analyzed", example="completed")
    analysis_version: Optional[str] = Field("1.0", example="1.0")

    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectListResponse(BaseModel):
    success: bool = Field(True, example=True)
    total: int = Field(..., example=4)
    data: List[ProjectResponse] = Field(default_factory=list)


class ProjectSingleResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("Project retrieved successfully.", example="Project retrieved successfully.")
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
