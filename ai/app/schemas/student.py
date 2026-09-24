from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class SelfReportedSkill(BaseModel):
    """A skill self-reported by the student with an optional claimed proficiency."""
    name: str = Field(..., description="Name of the skill (e.g., 'Python', 'React')")
    level: str = Field(
        default="Intermediate",
        description="Claimed level: 'Beginner', 'Intermediate', 'Advanced', 'Expert'"
    )


class StudentProfile(BaseModel):
    """Self-reported or registered student profile data."""
    name: Optional[str] = Field(None, description="Full name of the student")
    email: Optional[str] = Field(None, description="Email address")
    target_role: Optional[str] = Field(
        None,
        description="Target job profile (e.g., 'Backend Engineer', 'Full Stack Developer', 'SDE 1', 'Data Scientist')"
    )
    target_companies: List[str] = Field(
        default_factory=list,
        description="Target dream companies (e.g. ['Google', 'Microsoft', 'Amazon'])"
    )
    graduation_year: Optional[int] = Field(None, description="Expected or actual year of graduation")
    degree: Optional[str] = Field(None, description="Degree name (e.g., 'B.Tech', 'B.E.', 'MCA', 'BS')")
    branch: Optional[str] = Field(None, description="Department or branch (e.g., 'Computer Science', 'IT', 'ECE')")
    institution: Optional[str] = Field(None, description="College or university name")
    current_semester: Optional[int] = Field(None, description="Current semester (1-8)")
    cgpa: Optional[float] = Field(None, description="Current CGPA or GPA (e.g. 8.5, 3.8)")
    experience_level: Optional[str] = Field(
        None,
        description="Level of experience (e.g., 'Fresher', 'Internship Experience', '1-2 Years Experience')"
    )
    primary_interests: List[str] = Field(
        default_factory=list,
        description="Areas of interest (e.g. ['Machine Learning', 'Cloud Architecture'])"
    )
    self_reported_skills: List[SelfReportedSkill] = Field(
        default_factory=list,
        description="Skills self-reported by the student with claimed proficiency levels"
    )

    @field_validator("self_reported_skills", mode="before")
    @classmethod
    def normalize_self_reported_skills(cls, v: Any) -> List[SelfReportedSkill]:
        """Allow strings, dicts, or lists of strings/dicts to be passed seamlessly."""
        if not v:
            return []
        if isinstance(v, list):
            normalized = []
            for item in v:
                if isinstance(item, str):
                    normalized.append(SelfReportedSkill(name=item.strip(), level="Intermediate"))
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("skill") or ""
                    level = item.get("level") or item.get("current_level") or "Intermediate"
                    if name:
                        normalized.append(SelfReportedSkill(name=name.strip(), level=level))
                elif isinstance(item, SelfReportedSkill):
                    normalized.append(item)
            return normalized
        elif isinstance(v, dict):
            # Format: {"Python": "Advanced", "React": "Beginner"}
            return [
                SelfReportedSkill(name=k.strip(), level=str(val))
                for k, val in v.items()
                if k.strip()
            ]
        return []
