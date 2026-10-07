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
        "status": "scored",
        "evidence": ["ATS Quality Score: 78/100", "Detected 12 verified technical skills."],
        "missing_data": [],
        "recommendations": ["Quantify project impacts with concrete performance metrics on your resume."]
    },
    "DSA": {
        "category": "DSA",
        "key": "dsa",
        "score": 82,
        "weight": 0.20,
        "weighted_score": 16.4,
        "confidence": 0.90,
        "status": "scored",
        "evidence": ["Total Solved: 150 problems", "Breakdown: Easy 50, Medium 80, Hard 20"],
        "missing_data": [],
        "recommendations": ["Target Medium & Hard Dynamic Programming and Graph problems."]
    },
    "Projects": {
        "category": "Projects",
        "key": "projects",
        "score": 85,
        "weight": 0.20,
        "weighted_score": 17.0,
        "confidence": 0.88,
        "status": "scored",
        "evidence": ["2 active portfolio projects audited.", "Average AST complexity score: 85/100"],
        "missing_data": [],
        "recommendations": ["Add live deployment URLs and comprehensive README documentation."]
    },
    "GitHub": {
        "category": "GitHub",
        "key": "github",
        "score": 70,
        "weight": 0.10,
        "weighted_score": 7.0,
        "confidence": 0.85,
        "status": "scored",
        "evidence": ["GitHub Handle: @student_dev", "Repositories: 5, Total Stars: 12"],
        "missing_data": [],
        "recommendations": ["Maintain a continuous commit streak and document public repository READMEs."]
    },
    "CS Fundamentals": {
        "category": "CS Fundamentals",
        "key": "cs_fundamentals",
        "score": 75,
        "weight": 0.15,
        "weighted_score": 11.25,
        "confidence": 0.80,
        "status": "scored",
        "evidence": ["Verified CS Fundamentals assessment score: 75/100 across DBMS, OS, Networks, OOP."],
        "missing_data": [],
        "recommendations": ["Review OS process scheduling, DBMS indexing, and TCP/IP networking."]
    },
    "Communication": {
        "category": "Communication",
        "key": "communication",
        "score": 68,
        "weight": 0.10,
        "weighted_score": 6.8,
        "confidence": 0.75,
        "status": "insufficient_data",
        "evidence": [],
        "missing_data": ["No full-length spoken communication assessment available."],
        "recommendations": ["Complete a spoken technical explanation drill to assess communication skills."]
    },
    "Interview": {
        "category": "Interview",
        "key": "interview",
        "score": 65,
        "weight": 0.10,
        "weighted_score": 6.5,
        "confidence": 0.70,
        "status": "insufficient_data",
        "evidence": [],
        "missing_data": ["No mock interview sessions completed."],
        "recommendations": ["Schedule AI mock interview session."]
    }
}

EXAMPLE_WEIGHTS_USED = {
    "Resume": 0.15,
    "DSA": 0.20,
    "Projects": 0.20,
    "GitHub": 0.10,
    "CS Fundamentals": 0.15,
    "Communication": 0.10,
    "Interview": 0.10
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
    "Resume": {"score": 78, "status": "scored"},
    "DSA": {"score": 82, "status": "scored"},
    "Projects": {"score": 85, "status": "scored"},
    "GitHub": {"score": 70, "status": "scored"},
    "CS Fundamentals": {"score": 75, "status": "scored"},
    "Communication": {"score": 68, "status": "insufficient_data"},
    "Interview": {"score": 65, "status": "insufficient_data"}
}


class CategoryScoreSchema(BaseModel):
    category: str = Field(..., example="Resume")
    key: Optional[str] = Field(None, example="resume")
    score: Optional[int] = Field(None, ge=0, le=100, example=78)
    weight: float = Field(..., example=0.15)
    weighted_score: float = Field(..., example=11.7)
    confidence: float = Field(..., example=0.85)
    status: str = Field(..., example="scored")
    evidence: List[str] = Field(default_factory=list, example=["ATS score 84/100"])
    missing_data: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class CategorySummaryItemSchema(BaseModel):
    score: Optional[int] = Field(None, ge=0, le=100, example=78)
    status: str = Field(..., example="scored")


class RoleAlignmentSchema(BaseModel):
    role: str = Field(..., example="Backend Developer")
    aligned_skills: List[str] = Field(default_factory=list, example=["Python", "FastAPI"])
    missing_skills: List[str] = Field(default_factory=list, example=["Docker", "Kubernetes"])
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

    calculation_version: str = Field("1.0", example="1.0")
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "650c1f2e8f1b2c3d4e5f6a7b",
                "user_id": "user_123",
                "target_role": "Backend Developer",
                "overall_score": 76,
                "overall_confidence": 0.82,
                "readiness_label": "Advanced",
                "categories": EXAMPLE_CATEGORIES,
                "weights_used": EXAMPLE_WEIGHTS_USED,
                "scored_categories_count": 5,
                "insufficient_categories_count": 2,
                "strengths": [
                    "DSA is a strength (82/100) with verified evidence.",
                    "Projects is a strength (85/100) with verified evidence."
                ],
                "key_gaps": [
                    "Communication score is currently below target threshold (68/100).",
                    "Missing evidence for Interview."
                ],
                "recommendations": [
                    "Target Medium & Hard Dynamic Programming and Graph problems.",
                    "Add live deployment URLs and comprehensive README documentation."
                ],
                "role_alignment": {
                    "role": "Backend Developer",
                    "aligned_skills": ["Python", "FastAPI"],
                    "missing_skills": ["Docker", "Kubernetes"],
                    "role_alignment_score": 75,
                    "status": "scored",
                    "message": "Evaluated alignment against Backend Developer competencies."
                },
                "data_completeness": {
                    "profile": True,
                    "resume": True,
                    "github": True,
                    "leetcode": True,
                    "projects": True,
                    "communication": False,
                    "interviews": False
                },
                "stale_data": [],
                "provenance": EXAMPLE_PROVENANCE,
                "calculation_version": "1.0",
                "created_at": "2026-10-07T12:00:00Z",
                "updated_at": "2026-10-07T12:00:00Z"
            }
        }


class ReadinessSingleResponse(BaseModel):
    success: bool = True
    message: str = "Placement readiness retrieved successfully"
    data: ReadinessResponse

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Placement readiness analysis calculated successfully.",
                "data": {
                    "id": "650c1f2e8f1b2c3d4e5f6a7b",
                    "user_id": "user_123",
                    "target_role": "Backend Developer",
                    "overall_score": 76,
                    "overall_confidence": 0.82,
                    "readiness_label": "Advanced",
                    "categories": EXAMPLE_CATEGORIES,
                    "weights_used": EXAMPLE_WEIGHTS_USED,
                    "scored_categories_count": 5,
                    "insufficient_categories_count": 2,
                    "strengths": [
                        "DSA is a strength (82/100) with verified evidence.",
                        "Projects is a strength (85/100) with verified evidence."
                    ],
                    "key_gaps": [
                        "Communication score is currently below target threshold (68/100).",
                        "Missing evidence for Interview."
                    ],
                    "recommendations": [
                        "Target Medium & Hard Dynamic Programming and Graph problems.",
                        "Add live deployment URLs and comprehensive README documentation."
                    ],
                    "role_alignment": {
                        "role": "Backend Developer",
                        "aligned_skills": ["Python", "FastAPI"],
                        "missing_skills": ["Docker", "Kubernetes"],
                        "role_alignment_score": 75,
                        "status": "scored",
                        "message": "Evaluated alignment against Backend Developer competencies."
                    },
                    "data_completeness": {
                        "profile": True,
                        "resume": True,
                        "github": True,
                        "leetcode": True,
                        "projects": True,
                        "communication": False,
                        "interviews": False
                    },
                    "stale_data": [],
                    "provenance": EXAMPLE_PROVENANCE,
                    "calculation_version": "1.0",
                    "created_at": "2026-10-07T12:00:00Z",
                    "updated_at": "2026-10-07T12:00:00Z"
                }
            }
        }


class ReadinessSummaryDataSchema(BaseModel):
    user_id: str = Field(..., example="user_123")
    overall_score: Optional[int] = Field(None, example=76)
    readiness_label: str = Field(..., example="Advanced")
    overall_confidence: float = Field(..., example=0.82)
    target_role: str = Field(..., example="Backend Developer")
    scored_categories_count: int = Field(5, example=5)
    categories: Dict[str, CategorySummaryItemSchema] = Field(
        default_factory=dict,
        json_schema_extra={"example": EXAMPLE_SUMMARY_CATEGORIES}
    )
    updated_at: Optional[Any] = Field(None, example="2026-10-07T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "overall_score": 76,
                "readiness_label": "Advanced",
                "overall_confidence": 0.82,
                "target_role": "Backend Developer",
                "scored_categories_count": 5,
                "categories": EXAMPLE_SUMMARY_CATEGORIES,
                "updated_at": "2026-10-07T12:00:00Z"
            }
        }


class ReadinessSummaryResponse(BaseModel):
    success: bool = True
    message: str = "Placement readiness summary retrieved"
    data: ReadinessSummaryDataSchema

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Placement readiness summary retrieved.",
                "data": {
                    "user_id": "user_123",
                    "overall_score": 76,
                    "readiness_label": "Advanced",
                    "overall_confidence": 0.82,
                    "target_role": "Backend Developer",
                    "scored_categories_count": 5,
                    "categories": EXAMPLE_SUMMARY_CATEGORIES,
                    "updated_at": "2026-10-07T12:00:00Z"
                }
            }
        }


class ReadinessHistoryResponse(BaseModel):
    success: bool = True
    total: int = Field(..., example=1)
    data: List[ReadinessResponse] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total": 1,
                "data": [
                    {
                        "id": "650c1f2e8f1b2c3d4e5f6a7b",
                        "user_id": "user_123",
                        "target_role": "Backend Developer",
                        "overall_score": 76,
                        "overall_confidence": 0.82,
                        "readiness_label": "Advanced",
                        "categories": EXAMPLE_CATEGORIES,
                        "weights_used": EXAMPLE_WEIGHTS_USED,
                        "scored_categories_count": 5,
                        "insufficient_categories_count": 2,
                        "strengths": [
                            "DSA is a strength (82/100) with verified evidence.",
                            "Projects is a strength (85/100) with verified evidence."
                        ],
                        "key_gaps": [
                            "Communication score is currently below target threshold (68/100).",
                            "Missing evidence for Interview."
                        ],
                        "recommendations": [
                            "Target Medium & Hard Dynamic Programming and Graph problems.",
                            "Add live deployment URLs and comprehensive README documentation."
                        ],
                        "role_alignment": {
                            "role": "Backend Developer",
                            "aligned_skills": ["Python", "FastAPI"],
                            "missing_skills": ["Docker", "Kubernetes"],
                            "role_alignment_score": 75,
                            "status": "scored",
                            "message": "Evaluated alignment against Backend Developer competencies."
                        },
                        "data_completeness": {
                            "profile": True,
                            "resume": True,
                            "github": True,
                            "leetcode": True,
                            "projects": True,
                            "communication": False,
                            "interviews": False
                        },
                        "stale_data": [],
                        "provenance": EXAMPLE_PROVENANCE,
                        "calculation_version": "1.0",
                        "created_at": "2026-10-07T12:00:00Z",
                        "updated_at": "2026-10-07T12:00:00Z"
                    }
                ]
            }
        }
