from typing import List, Optional
from pydantic import BaseModel, Field

class ScoreDetail(BaseModel):
    score: int = Field(..., description="A numerical score out of 100")
    reason: str = Field(..., description="Explanation based strictly on evidence for why this score was given")

class ExtractedSkills(BaseModel):
    languages: List[str] = Field(default_factory=list, description="Programming languages extracted from the resume")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries extracted from the resume")
    tools: List[str] = Field(default_factory=list, description="Tools and platforms extracted from the resume")
    other: List[str] = Field(default_factory=list, description="Other skills extracted from the resume")

class Education(BaseModel):
    institution: str = Field(..., description="Name of the institution")
    degree: str = Field(..., description="Degree obtained or pursued")
    graduation_date: Optional[str] = Field(None, description="Graduation date if stated")
    gpa: Optional[str] = Field(None, description="GPA if stated")

class Experience(BaseModel):
    company: str = Field(..., description="Company name")
    role: str = Field(..., description="Job title or role")
    duration: Optional[str] = Field(None, description="Duration of employment")
    bullets: List[str] = Field(default_factory=list, description="Raw bullet points under this experience")

class Project(BaseModel):
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Short description of the project")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in this project")
    bullets: List[str] = Field(default_factory=list, description="Raw bullet points for this project")
    has_metrics: bool = Field(..., description="True if the project description contains quantifiable metrics (e.g., numbers, percentages)")

class WeakBullet(BaseModel):
    original_bullet: str = Field(..., description="The exact bullet point from the text")
    issues: List[str] = Field(..., description="List of issues with this bullet (e.g., 'vague', 'missing metrics', 'generic')")
    suggestion: str = Field(..., description="A suggested rewrite based ONLY on evidence present in the resume. DO NOT invent metrics or technologies.")
    evidence_used: List[str] = Field(..., description="List of facts from the resume used to formulate the suggestion")

# Model used by the LLM to return raw structural findings
class LLMResumeExtraction(BaseModel):
    skills: ExtractedSkills = Field(..., description="Skills categorized by type")
    education: List[Education] = Field(default_factory=list, description="List of educational background")
    experience: List[Experience] = Field(default_factory=list, description="List of work experience")
    projects: List[Project] = Field(default_factory=list, description="List of projects")
    certifications: List[str] = Field(default_factory=list, description="List of certifications")
    achievements: List[str] = Field(default_factory=list, description="List of achievements or awards")
    missing_sections: List[str] = Field(default_factory=list, description="Standard resume sections that are completely missing (e.g., 'Projects', 'Education')")
    weak_bullets: List[WeakBullet] = Field(default_factory=list, description="Analysis of weak or poorly constructed bullet points found in the resume")
    repeated_words: List[str] = Field(default_factory=list, description="Overused words or phrases")
    generic_phrases: List[str] = Field(default_factory=list, description="Cliches or generic phrases found (e.g., 'Team player', 'Hard worker')")
    keyword_gaps: List[str] = Field(default_factory=list, description="Important tech keywords that might be expected based on the profile but are missing")

# Final combined model returned by the API
class ResumeAnalysis(BaseModel):
    ats_score: ScoreDetail
    skills_score: ScoreDetail
    projects_score: ScoreDetail
    experience_score: ScoreDetail
    formatting_score: ScoreDetail
    impact_score: ScoreDetail
    
    overall_score: int = Field(..., description="The final calculated score out of 100")
    suggestions: List[str] = Field(default_factory=list, description="High-level suggestions for improving the resume")
    
    extracted_skills: ExtractedSkills
    education: List[Education]
    experience: List[Experience]
    projects: List[Project]
    certifications: List[str]
    achievements: List[str]
    
    missing_sections: List[str]
    weak_bullets: List[WeakBullet]
    repeated_words: List[str]
    generic_phrases: List[str]
    keyword_gaps: List[str]
