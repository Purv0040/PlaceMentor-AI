from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.roles import ALLOWED_TARGET_ROLES


# ============================================================
# PERSONAL INFORMATION
# ============================================================

class PersonalInfoSchema(BaseModel):
    name: Optional[str] = Field(
        default="Student Candidate",
        description="Student full name",
    )

    college: Optional[str] = Field(
        default="",
        description="College / University name",
    )

    degree: Optional[str] = Field(
        default="",
        description="Degree & Branch",
    )

    graduationYear: Optional[str] = Field(
        default="2026",
        description="Graduation year, e.g. 2027",
    )

    branch: Optional[str] = "Computer Science / IT"
    cgpa: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    linkedinUrl: Optional[str] = None
    portfolioUrl: Optional[str] = None
    profile_image: Optional[str] = None

    @field_validator(
        "name",
        "college",
        "degree",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v or ""

    @field_validator("graduationYear", mode="before")
    @classmethod
    def validate_graduation_year(cls, v):
        if v is None:
            return "2026"
        if isinstance(v, int):
            v = str(v)
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return "2026"
            if v.isdigit():
                year = int(v)
                if year < 2020 or year > 2035:
                    raise ValueError(
                        "Graduation year must be between 2020 and 2035."
                    )
                return str(year)
            raise ValueError("Graduation year must be a valid year.")
        return "2026"


# ============================================================
# CAREER INFORMATION
# ============================================================

class CareerInfoSchema(BaseModel):
    targetRole: str = Field(
        "Backend Developer",
        description="Primary target role",
    )

    secondaryRole: Optional[str] = Field(
        "AI/ML Engineer",
        description="Secondary target role",
    )

    companyTier: Optional[str] = Field(
        "Tier-1 Product (MAANG / Unicorns)",
        description="Target company tier",
    )

    career_goal: Optional[str] = None
    preferred_domain: Optional[str] = None
    preferred_work_mode: Optional[str] = None

    @field_validator("targetRole", mode="before")
    @classmethod
    def validate_target_role(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return "Full Stack Engineer"
            return v
        return v or "Full Stack Engineer"


# ============================================================
# SKILLS
# ============================================================

class SkillsInfoSchema(BaseModel):
    dsaLevel: str = "Intermediate"

    sysDesignLevel: str = "Beginner"

    databaseLevel: str = "Intermediate"

    frameworkLevel: str = "Advanced"

    selectedSkills: List[str] = Field(
        default_factory=list
    )

    @field_validator(
        "selectedSkills",
        mode="before",
    )
    @classmethod
    def clean_skills_list(cls, v):
        if v is None:
            return []

        if isinstance(v, list):
            cleaned = []

            for item in v:
                if isinstance(item, str):
                    item = item.strip()

                    if item and item not in cleaned:
                        cleaned.append(item)

            return cleaned

        return []


# ============================================================
# INTEGRATIONS
# ============================================================

class IntegrationsInfoSchema(BaseModel):
    """
    Integration information.

    IMPORTANT:
    All optional handles/file names default to None.

    This prevents old mock/demo values from automatically
    appearing in a new profile.
    """

    githubConnected: bool = False

    githubHandle: Optional[str] = None

    leetcodeConnected: bool = False

    leetcodeHandle: Optional[str] = None

    resumeUploaded: bool = False

    resumeFileName: Optional[str] = None


# ============================================================
# PREFERENCES
# ============================================================

class PreferencesInfoSchema(BaseModel):
    dailyGoalMinutes: str = "90"

    studyDurationDays: Optional[str] = "90"

    mentorTone: str = (
        "Socratic Coach (Probing Questions)"
    )

    studyCadence: str = (
        "Daily Evening Sprint"
    )

    preferred_language: str = "English"

<<<<<<< HEAD
    @field_validator("studyDurationDays")
    @classmethod
    def validate_study_duration(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.isdigit():
                days = int(v)
                if days < 1 or days > 365:
                    raise ValueError(
                        "Study duration days must be between 1 and 365."
                    )
        return v

    @field_validator("dailyGoalMinutes")
=======
    @field_validator("dailyGoalMinutes", mode="before")
>>>>>>> 43b07ddd632a814987d6db1c57622e9835d6bc89
    @classmethod
    def validate_daily_minutes(cls, v):
        if v is None:
            return "90"
        if isinstance(v, (int, float)):
            return str(int(v))
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return "90"
            if v.isdigit():
                minutes = int(v)
                if 0 <= minutes <= 1440:
                    return str(minutes)
                return "90"
            return v
        return "90"


# ============================================================
# GOALS
# ============================================================

class GoalsInfoSchema(BaseModel):
    targetDrive: Optional[str] = (
        "August 2026 (Campus Phase 1)"
    )

    targetCtc: Optional[str] = (
        "14 - 24 LPA (Product Tier)"
    )

    primaryGoal: Optional[str] = (
        "Master Graph Algorithms & System Microservices"
    )


# ============================================================
# ONBOARDING
# ============================================================

class OnboardingStatusSchema(BaseModel):
    completed: bool = False

    completed_at: Optional[datetime] = None

    current_step: int = 1

    completed_steps: List[int] = Field(
        default_factory=lambda: [1]
    )


# ============================================================
# PROFILE CREATE
# ============================================================

class ProfileCreate(BaseModel):
    """
    Used when creating a new student profile.

    Sections are optional so the profile can be initialized
    gradually during onboarding.
    """

    personal: Optional[PersonalInfoSchema] = None

    career: Optional[CareerInfoSchema] = None

    skills: Optional[SkillsInfoSchema] = None

    integrations: Optional[IntegrationsInfoSchema] = None

    preferences: Optional[PreferencesInfoSchema] = None

    goals: Optional[GoalsInfoSchema] = None

    onboarding: Optional[OnboardingStatusSchema] = None


# ============================================================
# PROFILE UPDATE
# ============================================================

class ProfileUpdate(BaseModel):
    """
    Used for PUT/PATCH profile updates.

    IMPORTANT:
    None is allowed intentionally.

    Example:

        {
            "integrations": {
                "githubConnected": false,
                "githubHandle": null
            }
        }

    This allows the existing GitHub handle to be cleared.
    """

    personal: Optional[PersonalInfoSchema] = None

    career: Optional[CareerInfoSchema] = None

    skills: Optional[SkillsInfoSchema] = None

    integrations: Optional[IntegrationsInfoSchema] = None

    preferences: Optional[PreferencesInfoSchema] = None

    goals: Optional[GoalsInfoSchema] = None

    onboarding: Optional[OnboardingStatusSchema] = None

    overallReadinessScore: Optional[float] = None

    baseline_score: Optional[float] = None


# ============================================================
# PROFILE RESPONSE
# ============================================================

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


ProfileUpdateRequest = ProfileUpdate
