"""Pydantic v2 data models for API request/response validation."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class MetadataItem(BaseModel):
    """Extracted metadata field with confidence score."""
    value: Optional[str] = Field(default=None, description="Extracted string value or None.")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score (0.0 - 1.0).")


class ResumeMetadata(BaseModel):
    """Extracted personal metadata from student resume."""
    full_name: Optional[str] = Field(default=None, description="Full Name")
    email: Optional[str] = Field(default=None, description="Email")
    phone_number: Optional[str] = Field(default=None, description="Phone Number")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn URL")
    github_url: Optional[str] = Field(default=None, description="GitHub URL")
    portfolio_website: Optional[str] = Field(default=None, description="Portfolio Website (if available)")


class SectionDetail(BaseModel):
    """Details of a detected resume section."""
    present: bool = Field(..., description="Whether section header was detected.")
    text: str = Field(default="", description="Extracted content text of the section.")
    word_count: int = Field(default=0, description="Word count within section.")


class SkillItem(BaseModel):
    """Extracted technical skill details with confidence."""
    name: str = Field(..., description="Standardized skill name.")
    confidence: float = Field(default=0.99, ge=0.0, le=1.0, description="Extraction confidence score.")
    category: Optional[str] = Field(default="General", description="Skill category (e.g. Programming Languages, DevOps).")
    source_section: Optional[str] = Field(default="General", description="Section where skill was found.")
    skill_name: Optional[str] = Field(default=None, description="Legacy alias for skill name.")


class SkillsSummary(BaseModel):
    """Summary of all extracted skills."""
    detected_skills: List[SkillItem] = Field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = Field(default_factory=dict)
    total_skills_count: int = Field(default=0)
    unique_categories_count: int = Field(default=0)


class ContactInfoBooleans(BaseModel):
    """Boolean flags for extracted contact information."""
    email: bool = False
    phone: bool = False
    linkedin: bool = False
    github: bool = False
    portfolio: bool = False


class ContactInfo(BaseModel):
    """Extracted contact information."""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class ResumeStatistics(BaseModel):
    """Key metric statistics of the analyzed resume."""
    total_pages: int = Field(default=1, ge=1, description="Number of pages in PDF.")
    total_words: int = Field(default=0, ge=0, description="Total word count.")
    total_characters: int = Field(default=0, ge=0, description="Total character count.")
    number_of_skills_found: int = Field(default=0, ge=0, description="Total unique skills extracted.")
    number_of_sections_found: int = Field(default=0, ge=0, description="Number of detected sections.")
    has_contact_info: ContactInfoBooleans = Field(default_factory=ContactInfoBooleans, description="Contact info boolean flags.")


class SectionATSScore(BaseModel):
    """Section-wise ATS score breakdown out of 100."""
    overall: int = Field(..., ge=0, le=100, description="Overall ATS score out of 100.")
    education: int = Field(..., ge=0, le=100, description="Education section score.")
    skills: int = Field(..., ge=0, le=100, description="Technical skills section score.")
    projects: int = Field(..., ge=0, le=100, description="Projects section score.")
    experience: int = Field(..., ge=0, le=100, description="Experience section score.")
    certifications: int = Field(..., ge=0, le=100, description="Certifications section score.")
    contact: int = Field(..., ge=0, le=100, description="Contact information section score.")
    achievements: int = Field(..., ge=0, le=100, description="Achievements section score.")


class ATSMaxScores(BaseModel):
    """Maximum possible weights for legacy ATS scoring components."""
    essential_sections: int = 30
    technical_skills: int = 30
    projects_experience: int = 20
    contact_info: int = 10
    structure: int = 10


class ATSBreakdown(BaseModel):
    """Legacy detailed score breakdown of the ATS evaluation."""
    total_score: int = Field(..., ge=0, le=100, description="Final ATS score out of 100.")
    essential_sections_score: float = Field(..., ge=0, le=30)
    technical_skills_score: float = Field(..., ge=0, le=30)
    projects_experience_score: float = Field(..., ge=0, le=20)
    contact_info_score: float = Field(..., ge=0, le=10)
    structure_score: float = Field(..., ge=0, le=10)
    max_scores: ATSMaxScores = Field(default_factory=ATSMaxScores)


class Suggestion(BaseModel):
    """Actionable improvement recommendation."""
    priority: str = Field(..., description="Priority level: HIGH, MEDIUM, LOW.")
    category: str = Field(..., description="Target category of improvement.")
    message: str = Field(..., description="Actionable recommendation message.")
    estimated_impact: str = Field(..., description="Estimated score gain (e.g. '+10 pts').")


class CategorizedSuggestions(BaseModel):
    """Categorized suggestions response format."""
    critical: List[str] = Field(default_factory=list, description="Critical high-priority issues.")
    recommended: List[str] = Field(default_factory=list, description="Recommended medium-priority improvements.")
    optional: List[str] = Field(default_factory=list, description="Optional low-priority recommendations.")


class ResumeAnalysisResponse(BaseModel):
    """Full analysis result payload returned by the API."""
    success: bool = True
    version: str = Field(default="1.0.0", description="API version.")
    processing_time: str = Field(..., description="Total execution time (e.g. '1.38 sec').")
    resume_metadata: ResumeMetadata = Field(..., description="Extracted student metadata.")
    statistics: ResumeStatistics = Field(..., description="Resume statistics and metrics.")
    ats_score: SectionATSScore = Field(..., description="Section-wise ATS scores.")
    sections: Dict[str, Dict[str, Any]] = Field(..., description="Extracted resume sections.")
    skills: List[Dict[str, Any]] = Field(..., description="Extracted technical skills.")
    missing_sections: List[str] = Field(default_factory=list, description="List of missing resume sections.")
    suggestions: List[Dict[str, Any]] = Field(..., description="Categorized actionable suggestions.")


class HealthCheckResponse(BaseModel):
    """Health check endpoint response model."""
    status: str = "ok"
    app_name: str
    version: str


class ErrorResponse(BaseModel):
    """Standardized API Error payload."""
    success: bool = False
    error: str
    message: str
    status_code: int

