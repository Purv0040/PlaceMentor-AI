from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.profile import (
    PersonalInfoSchema,
    CareerInfoSchema,
    SkillsInfoSchema,
    IntegrationsInfoSchema,
    PreferencesInfoSchema,
    GoalsInfoSchema,
    OnboardingStatusSchema,
)


class OnboardingStepUpdate(BaseModel):
    step_number: int = Field(..., ge=1, le=7, description="Onboarding step number (1 to 7)")
    profile: Optional[PersonalInfoSchema] = None
    career: Optional[CareerInfoSchema] = None
    skills: Optional[SkillsInfoSchema] = None
    integrations: Optional[IntegrationsInfoSchema] = None
    preferences: Optional[PreferencesInfoSchema] = None
    goals: Optional[GoalsInfoSchema] = None


class OnboardingCompleteResponse(BaseModel):
    user_id: str
    onboarding_completed: bool = True
    completed_at: datetime
    message: str = "Onboarding completed successfully!"


class OnboardingStateResponse(BaseModel):
    user_id: str
    onboarding: OnboardingStatusSchema
    profile: PersonalInfoSchema
    career: CareerInfoSchema
    skills: SkillsInfoSchema
    integrations: IntegrationsInfoSchema
    preferences: PreferencesInfoSchema
    goals: GoalsInfoSchema
