from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.core.roles import ALLOWED_TARGET_ROLES


class PersonalInfoSchema(BaseModel):
    name: str = Field(..., min_length=1, description="Student full name")
    college: str = Field(..., min_length=1, description="College / University name")
    degree: str = Field(..., min_length=1, description="Degree & Branch")
    graduationYear: str = Field(..., description="Graduation Year e.g. 2027")
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    profile_image: Optional[str] = None

    @field_validator("name", "college", "degree", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Field cannot be empty string.")
        return v

    @field_validator("graduationYear")
    @classmethod
    def validate_graduation_year(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if v.isdigit():
                year = int(v)
                if year < 2020 or year > 2035:
                    raise ValueError("Graduation year must be between 2020 and 2035.")
        return v


class CareerInfoSchema(BaseModel):
    targetRole: str = Field("Backend Developer", description="Primary target role")
    secondaryRole: Optional[str] = Field("AI/ML Engineer", description="Secondary target role")
    companyTier: Optional[str] = Field("Tier-1 Product (MAANG / Unicorns)", description="Target company tier")
    career_goal: Optional[str] = None
    preferred_domain: Optional[str] = None
    preferred_work_mode: Optional[str] = None

    @field_validator("targetRole")
    @classmethod
    def validate_target_role(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if v not in ALLOWED_TARGET_ROLES:
                # Accept custom role if valid string, but validate non-empty
                if not v:
                    raise ValueError("Target role cannot be empty.")
        return v


class SkillsInfoSchema(BaseModel):
    dsaLevel: str = "Intermediate"
    sysDesignLevel: str = "Beginner"
    databaseLevel: str = "Intermediate"
    frameworkLevel: str = "Advanced"
    selectedSkills: List[str] = Field(default_factory=list)

    @field_validator("selectedSkills", mode="before")
    @classmethod
    def clean_skills_list(cls, v: List[str]) -> List[str]:
        if isinstance(v, list):
            cleaned = []
            for item in v:
                if isinstance(item, str) and item.strip():
                    if item.strip() not in cleaned:
                        cleaned.append(item.strip())
            return cleaned
        return []


class IntegrationsInfoSchema(BaseModel):
    githubConnected: bool = True
    githubHandle: Optional[str] = "alexpatel-dev"
    leetcodeConnected: bool = True
    leetcodeHandle: Optional[str] = "alex_patel99"
    resumeUploaded: bool = True
    resumeFileName: Optional[str] = "Alex_Patel_Backend_Resume.pdf"


class PreferencesInfoSchema(BaseModel):
    dailyGoalMinutes: str = "90"
    mentorTone: str = "Socratic Coach (Probing Questions)"
    studyCadence: str = "Daily Evening Sprint"
    preferred_language: str = "English"

    @field_validator("dailyGoalMinutes")
    @classmethod
    def validate_daily_minutes(cls, v: str) -> str:
        if isinstance(v, str) and v.isdigit():
            mins = int(v)
            if mins < 0 or mins > 1440:
                raise ValueError("Daily goal minutes must be between 0 and 1440.")
        return v


class GoalsInfoSchema(BaseModel):
    targetDrive: str = "August 2026 (Campus Phase 1)"
    targetCtc: str = "14 - 24 LPA (Product Tier)"
    primaryGoal: Optional[str] = "Master Graph Algorithms & System Microservices"


class OnboardingStatusSchema(BaseModel):
    completed: bool = False
    completed_at: Optional[datetime] = None
    current_step: int = 1
    completed_steps: List[int] = Field(default_factory=lambda: [1])


class ProfileCreate(BaseModel):
    personal: Optional[PersonalInfoSchema] = None
    career: Optional[CareerInfoSchema] = None
    skills: Optional[SkillsInfoSchema] = None
    integrations: Optional[IntegrationsInfoSchema] = None
    preferences: Optional[PreferencesInfoSchema] = None
    goals: Optional[GoalsInfoSchema] = None


class ProfileUpdate(BaseModel):
    personal: Optional[PersonalInfoSchema] = None
    career: Optional[CareerInfoSchema] = None
    skills: Optional[SkillsInfoSchema] = None
    integrations: Optional[IntegrationsInfoSchema] = None
    preferences: Optional[PreferencesInfoSchema] = None
    goals: Optional[GoalsInfoSchema] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    personal: PersonalInfoSchema
    career: CareerInfoSchema
    skills: SkillsInfoSchema
    integrations: IntegrationsInfoSchema
    preferences: PreferencesInfoSchema
    goals: GoalsInfoSchema
    onboarding: OnboardingStatusSchema
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
