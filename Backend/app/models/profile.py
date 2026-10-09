from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PersonalInfoModel(BaseModel):
    name: str = ""
    college: str = ""
    degree: str = ""
    graduationYear: str = "2026"
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    profile_image: Optional[str] = None


class CareerInfoModel(BaseModel):
    targetRole: str = "Full Stack Engineer"
    secondaryRole: Optional[str] = "Cybersecurity Analyst & Engineer"
    companyTier: Optional[str] = "Tier-1 Product (MAANG / Unicorns)"
    career_goal: Optional[str] = None
    preferred_domain: Optional[str] = None
    preferred_work_mode: Optional[str] = None


class SkillsInfoModel(BaseModel):
    dsaLevel: str = "Intermediate"
    sysDesignLevel: str = "Beginner"
    databaseLevel: str = "Intermediate"
    frameworkLevel: str = "Advanced"
    selectedSkills: List[str] = Field(
        default_factory=lambda: ["Java", "Spring Boot", "Data Structures", "SQL", "Git"]
    )


class IntegrationsInfoModel(BaseModel):
    githubConnected: bool = False
    githubHandle: Optional[str] = None
    leetcodeConnected: bool = False
    leetcodeHandle: Optional[str] = None
    resumeUploaded: bool = False
    resumeFileName: Optional[str] = None


class PreferencesInfoModel(BaseModel):
    dailyGoalMinutes: str = "90"
    mentorTone: str = "Socratic Coach (Probing Questions)"
    studyCadence: str = "Daily Evening Sprint"
    preferred_language: str = "English"


class GoalsInfoModel(BaseModel):
    targetDrive: str = "August 2026 (Campus Phase 1)"
    targetCtc: str = "14 - 24 LPA (Product Tier)"
    primaryGoal: Optional[str] = "Master Graph Algorithms & System Microservices"


class OnboardingStateModel(BaseModel):
    completed: bool = False
    completed_at: Optional[datetime] = None
    current_step: int = 1
    completed_steps: List[int] = Field(default_factory=lambda: [1])


class StudentProfileModel(BaseModel):
    """MongoDB StudentProfile document model stored in student_profiles collection."""

    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    personal: PersonalInfoModel = Field(default_factory=PersonalInfoModel)
    career: CareerInfoModel = Field(default_factory=CareerInfoModel)
    skills: SkillsInfoModel = Field(default_factory=SkillsInfoModel)
    integrations: IntegrationsInfoModel = Field(default_factory=IntegrationsInfoModel)
    preferences: PreferencesInfoModel = Field(default_factory=PreferencesInfoModel)
    goals: GoalsInfoModel = Field(default_factory=GoalsInfoModel)
    onboarding: OnboardingStateModel = Field(default_factory=OnboardingStateModel)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
