from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

EXAMPLE_CATEGORIES = {
    "Resume": {
        "category": "Resume",
        "key": "resume",
        "score": 78,
        "weight": 0.15,
        "weighted_score": 11.7,
        "confidence": 0.85,
        "status": "assessed",
        "evidence": ["ATS Quality Score: 78/100", "Detected 12 verified technical skills."],
        "missing_data": [],
        "reason": "Verified ATS analysis from uploaded resume document.",
        "rubric_detail": "ATS score (40%) + STAR formatting (30%) + role skill density (30%)",
        "is_fresh": True,
        "recommendations": ["Quantify project impacts with concrete performance metrics on your resume."]
    },
    "DSA": {
        "category": "DSA",
        "key": "dsa",
        "score": 82,
        "weight": 0.20,
        "weighted_score": 16.4,
        "confidence": 0.90,
        "status": "assessed",
        "evidence": ["Total Solved: 150 problems", "Breakdown: Easy 50, Medium 80, Hard 20"],
        "missing_data": [],
        "reason": "Verified LeetCode problem solve statistics and difficulty distribution.",
        "rubric_detail": "Easy (0.15 pts) + Medium (0.40 pts) + Hard (0.70 pts) + Contest bonus",
        "is_fresh": True,
        "recommendations": ["Target Medium & Hard Dynamic Programming and Graph problems."]
    },
    "Projects": {
        "category": "Projects",
        "key": "projects",
        "score": 85,
        "weight": 0.20,
        "weighted_score": 17.0,
        "confidence": 0.88,
        "status": "assessed",
        "evidence": ["2 active portfolio projects audited.", "Average AST complexity score: 85/100"],
        "missing_data": [],
        "reason": "Audited active portfolio projects with connected GitHub and deployment links.",
        "rubric_detail": "AST code complexity + GitHub repository link + Live URL + Tech depth",
        "is_fresh": True,
        "recommendations": ["Add live deployment URLs and comprehensive README documentation."]
    },
    "GitHub": {
        "category": "GitHub",
        "key": "github",
        "score": 70,
        "weight": 0.10,
        "weighted_score": 7.0,
        "confidence": 0.85,
        "status": "assessed",
        "evidence": ["GitHub Handle: @student_dev", "Repositories: 5, Total Stars: 12"],
        "missing_data": [],
        "reason": "Verified public repositories, commit footprint, and language diversity.",
        "rubric_detail": "Repository depth (40%) + Stars & Engagement (30%) + Language diversity (30%)",
        "is_fresh": True,
        "recommendations": ["Maintain a continuous commit streak and document public repository READMEs."]
    },
    "CS Fundamentals": {
        "category": "CS Fundamentals",
        "key": "cs_fundamentals",
        "score": 75,
        "weight": 0.15,
        "weighted_score": 11.25,
        "confidence": 0.80,
        "status": "assessed",
        "evidence": ["Verified CS Fundamentals assessment score: 75/100 across DBMS, OS, Networks, OOP."],
        "missing_data": [],
        "reason": "Verified assessment score across core computer science subjects.",
        "rubric_detail": "Normalized test scores in DBMS, Operating Systems, Computer Networks, and OOP",
        "is_fresh": True,
        "recommendations": ["Review OS process scheduling, DBMS indexing, and TCP/IP networking."]
    },
    "Communication": {
        "category": "Communication",
        "key": "communication",
        "score": 68,
        "weight": 0.10,
        "weighted_score": 6.8,
        "confidence": 0.50,
        "status": "provisional",
        "evidence": ["Limited proxy signal: Resume STAR bullet point formatting compliance: 68/100."],
        "missing_data": ["No full-length spoken communication or oral interview assessment available."],
        "reason": "Provisional evaluation based on written resume formatting; spoken drill needed.",
        "rubric_detail": "STAR structure compliance (proxy) / Oral technical explanation drill",
        "is_fresh": True,
        "recommendations": ["Complete a spoken technical explanation drill to assess communication skills."]
    },
    "Interview": {
        "category": "Interview",
        "key": "interview",
        "score": None,
        "weight": 0.10,
        "weighted_score": 0.0,
        "confidence": 0.0,
        "status": "not_assessed",
        "evidence": [],
        "missing_data": ["No mock interview sessions completed."],
        "reason": "No completed mock interview sessions found.",
        "rubric_detail": "Live coding correctness + Problem breakdown + Behavioral communication",
        "is_fresh": False,
        "recommendations": ["Schedule and complete an AI mock interview session."]
    }
}

EXAMPLE_WEIGHTS_USED = {
    "Resume": 0.1667,
    "DSA": 0.2222,
    "Projects": 0.2222,
    "GitHub": 0.1111,
    "CS Fundamentals": 0.1667,
    "Communication": 0.1111,
    "Interview": 0.0
}

EXAMPLE_PROVENANCE = {
    "resume_analysis_id": "650c1f2e8f1b2c3d4e5f6a70",
    "leetcode_analysis_id": "650c1f2e8f1b2c3d4e5f6a71",
    "project_analysis_ids": ["650c1f2e8f1b2c3d4e5f6a72", "650c1f2e8f1b2c3d4e5f6a73"],
    "github_analysis_id": "650c1f2e8f1b2c3d4e5f6a74",
    "communication_analysis_id": None,
    "interview_session_id": None
}

EXAMPLE_SUMMARY_CATEGORIES = {
    "Resume": {"score": 78, "status": "assessed"},
    "DSA": {"score": 82, "status": "assessed"},
    "Projects": {"score": 85, "status": "assessed"},
    "GitHub": {"score": 70, "status": "assessed"},
    "CS Fundamentals": {"score": 75, "status": "assessed"},
    "Communication": {"score": 68, "status": "provisional"},
    "Interview": {"score": None, "status": "not_assessed"}
}


class CategoryScoreSchema(BaseModel):
    category: str = Field(..., example="Resume")
    key: Optional[str] = Field(None, example="resume")
    score: Optional[int] = Field(None, ge=0, le=100, example=78)
    weight: float = Field(..., example=0.15)
    weighted_score: float = Field(..., example=11.7)
    confidence: float = Field(..., example=0.85)
    status: str = Field(..., example="assessed")  # assessed, provisional, stale, not_assessed, scored, insufficient_data
    evidence: List[str] = Field(default_factory=list, example=["ATS score 84/100"])
    missing_data: List[str] = Field(default_factory=list)
    reason: Optional[str] = Field(None, example="Verified ATS analysis from uploaded resume document.")
    rubric_detail: Optional[str] = Field(None, example="ATS score (40%) + STAR formatting (30%) + role skill density (30%)")
    assessment_timestamp: Optional[datetime] = None
    is_fresh: bool = Field(True, example=True)
    recommendations: List[str] = Field(default_factory=list)


class CategorySummaryItemSchema(BaseModel):
    score: Optional[int] = Field(None, ge=0, le=100, example=78)
    status: str = Field(..., example="assessed")


class RoleSpecificGapSchema(BaseModel):
    area: str = Field(..., example="Deep Learning & Neural Networks")
    description: str = Field(..., example="PyTorch / TensorFlow neural pipeline construction required for AI/ML Engineer.")
    severity: str = Field("High", example="High")


class RoleAlignmentSchema(BaseModel):
    role: str = Field(..., example="Backend Developer")
    aligned_skills: List[str] = Field(default_factory=list, example=["Python", "FastAPI"])
    missing_skills: List[str] = Field(default_factory=list, example=["Docker", "Kubernetes"])
    role_specific_gaps: List[RoleSpecificGapSchema] = Field(default_factory=list)
    role_alignment_score: Optional[int] = Field(None, example=75)
    status: Optional[str] = Field("scored", example="scored")
    message: Optional[str] = Field(None, example="Target role alignment evaluated.")


class DataCompletenessSchema(BaseModel):
    profile: bool = True
    resume: bool = True
    github: bool = True
    leetcode: bool = True
    projects: bool = True
    communication: bool = False
    interviews: bool = False


class StaleDataItemSchema(BaseModel):
    source: str = Field(..., example="github")
    last_updated: Optional[str] = Field(None, example="2026-09-01T00:00:00Z")
    message: str = Field(..., example="GitHub data has not been synchronized in 14 days.")


class ReadinessWeightsSchema(BaseModel):
    resume: float = Field(0.15, ge=0.0, le=1.0)
    dsa: float = Field(0.20, ge=0.0, le=1.0)
    projects: float = Field(0.20, ge=0.0, le=1.0)
    github: float = Field(0.10, ge=0.0, le=1.0)
    cs_fundamentals: float = Field(0.15, ge=0.0, le=1.0)
    communication: float = Field(0.10, ge=0.0, le=1.0)
    interview: float = Field(0.10, ge=0.0, le=1.0)


class ReadinessAnalyzeRequest(BaseModel):
    target_role: Optional[str] = Field(None, example="Backend Developer")
    weights: Optional[ReadinessWeightsSchema] = None


class ReadinessResponse(BaseModel):
    id: str = Field(..., example="650c1f2e8f1b2c3d4e5f6a7b")
    user_id: str = Field(..., example="user_123")

    target_role: str = Field(..., example="Backend Developer")
    overall_score: Optional[int] = Field(None, example=76)
    overall_confidence: float = Field(..., example=0.82)
    readiness_label: str = Field(..., example="Advanced")
    readiness_status: str = Field("assessed", example="assessed")  # assessed, provisional, stale, insufficient_evidence
    coverage_percentage: float = Field(80.0, example=80.0)

    previous_score: Optional[int] = Field(None, example=72)
    score_delta: Optional[int] = Field(None, example=4)

    categories: Dict[str, CategoryScoreSchema] = Field(
        default_factory=dict,
        json_schema_extra={"example": EXAMPLE_CATEGORIES}
    )
    weights_used: Dict[str, float] = Field(
        default_factory=dict,
        json_schema_extra={"example": EXAMPLE_WEIGHTS_USED}
    )

    scored_categories_count: int = Field(5, example=5)
    insufficient_categories_count: int = Field(2, example=2)

    strengths: List[str] = Field(
        default_factory=list,
        example=["DSA is a strength (82/100) with verified evidence.", "Projects is a strength (85/100) with verified evidence."]
    )
    key_gaps: List[str] = Field(
        default_factory=list,
        example=["Communication score is currently below target threshold (68/100).", "Missing evidence for Interview."]
    )
    recommendations: List[str] = Field(
        default_factory=list,
        example=["Target Medium & Hard Dynamic Programming and Graph problems.", "Add live deployment URLs."]
    )

    role_alignment: Optional[RoleAlignmentSchema] = None
    data_completeness: Optional[DataCompletenessSchema] = None
    stale_data: List[StaleDataItemSchema] = Field(default_factory=list)
    provenance: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        json_schema_extra={"example": EXAMPLE_PROVENANCE}
    )

    calculation_version: str = Field("2.0", example="2.0")
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReadinessSingleResponse(BaseModel):
    success: bool = True
    message: str = "Placement readiness retrieved successfully"
    data: ReadinessResponse


class ReadinessSummaryDataSchema(BaseModel):
    user_id: str = Field(..., example="user_123")
    overall_score: Optional[int] = Field(None, example=76)
    readiness_label: str = Field(..., example="Advanced")
    readiness_status: str = Field("assessed", example="assessed")
    coverage_percentage: float = Field(80.0, example=80.0)
    previous_score: Optional[int] = Field(None, example=72)
    score_delta: Optional[int] = Field(None, example=4)
    overall_confidence: float = Field(..., example=0.82)
    target_role: str = Field(..., example="Backend Developer")
    scored_categories_count: int = Field(5, example=5)
    categories: Dict[str, CategorySummaryItemSchema] = Field(
        default_factory=dict,
        json_schema_extra={"example": EXAMPLE_SUMMARY_CATEGORIES}
    )
    updated_at: Optional[Any] = Field(None, example="2026-10-07T12:00:00Z")


class ReadinessSummaryResponse(BaseModel):
    success: bool = True
    message: str = "Placement readiness summary retrieved"
    data: ReadinessSummaryDataSchema


class ReadinessHistoryResponse(BaseModel):
    success: bool = True
    total: int = Field(..., example=1)
    data: List[ReadinessResponse] = Field(default_factory=list)
