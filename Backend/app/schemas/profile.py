from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.roles import ALLOWED_TARGET_ROLES


# ============================================================
# PERSONAL INFORMATION
# ============================================================

class PersonalInfoSchema(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        description="Student full name",
    )

    college: str = Field(
        ...,
        min_length=1,
        description="College / University name",
    )

    degree: str = Field(
        ...,
        min_length=1,
        description="Degree & Branch",
    )

    graduationYear: str = Field(
        ...,
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
            v = v.strip()

            if not v:
                raise ValueError(
                    "Field cannot be empty string."
                )

        return v

    @field_validator("graduationYear")
    @classmethod
    def validate_graduation_year(cls, v):
        if isinstance(v, str):
            v = v.strip()

            if v.isdigit():
                year = int(v)

                if year < 2020 or year > 2035:
                    raise ValueError(
                        "Graduation year must be between 2020 and 2035."
                    )

        return v


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

    @field_validator("targetRole")
    @classmethod
    def validate_target_role(cls, v):
        if isinstance(v, str):
            v = v.strip()

            if not v:
                raise ValueError(
                    "Target role cannot be empty."
                )

            # Allowed roles are validated when present.
            # Custom non-empty roles are also accepted.
            if v not in ALLOWED_TARGET_ROLES:
                return v

        return v


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

    mentorTone: str = (
        "Socratic Coach (Probing Questions)"
    )

    studyCadence: str = (
        "Daily Evening Sprint"
    )

    preferred_language: str = "English"

    @field_validator("dailyGoalMinutes")
    @classmethod
    def validate_daily_minutes(cls, v):
        if isinstance(v, str):
            v = v.strip()

            if v.isdigit():
                minutes = int(v)

                if minutes < 0 or minutes > 1440:
                    raise ValueError(
                        "Daily goal minutes must be between 0 and 1440."
                    )

        return v


# ============================================================
# GOALS
# ============================================================

class GoalsInfoSchema(BaseModel):
    targetDrive: str = (
        "August 2026 (Campus Phase 1)"
    )

    targetCtc: str = (
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

    overallReadinessScore: Optional[int] = None


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
