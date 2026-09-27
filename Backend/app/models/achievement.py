from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AchievementDefinitionModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    code: str  # Unique code e.g. FIRST_STEP, FIRST_RESUME
    title: str
    description: str
    category: str  # onboarding, profile, resume, github, leetcode, projects, roadmap, tasks, streak, interview, communication, readiness
    icon: str
    color: Optional[str] = "text-amber-400 bg-amber-500/10 border-amber-500/20"
    points: int = 100
    rarity: str = "common"  # common, uncommon, rare, milestone
    required_count: int = 1
    route: Optional[str] = "/dashboard"
    action_label: Optional[str] = "View Details"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True


class UserAchievementModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    achievement_id: str
    code: str
    unlocked: bool = True
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_count: int = 1
    required_count: int = 1
    progress_percentage: float = 100.0
    points: int = 100
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True
