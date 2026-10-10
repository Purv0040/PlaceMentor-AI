from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AchievementItemSchema(BaseModel):
    id: str = Field(..., example="ach-1")
    code: str = Field(..., example="WEEK_WARRIOR")
    title: str = Field(..., example="14-Day Consistency Master")
    description: str = Field(..., example="Maintained an active daily preparation sprint.")
    category: str = Field(..., example="Consistency")
    icon: str = Field(..., example="local_fire_department")
    color: Optional[str] = Field(None, example="text-amber-400 bg-amber-500/10 border-amber-500/20")
    xp: int = Field(250, example=250)
    requiredCount: int = Field(..., example=14)
    currentCount: int = Field(..., example=14)
    unlocked: bool = Field(False, example=True)
    unlockedAt: Optional[str] = Field(None, example="Yesterday")
    route: Optional[str] = Field(None, example="/tasks")
    actionLabel: Optional[str] = Field(None, example="View Today's Tasks")


class AchievementStatsSchema(BaseModel):
    unlockedCount: int = Field(..., example=8)
    totalCount: int = Field(..., example=12)
    earnedXp: int = Field(..., example=1850)
    totalXp: int = Field(..., example=3000)
    level: int = Field(..., example=7)
    levelTitle: str = Field(..., example="Active Competitor")
    xpInCurrentLevel: int = Field(..., example=50)
    xpRemaining: int = Field(..., example=250)
    completionPercentage: int = Field(..., example=67)
    isDailyClaimed: bool = Field(False, example=False)


class AchievementsResponseSchema(BaseModel):
    achievements: List[AchievementItemSchema]
    stats: AchievementStatsSchema


class AchievementCheckResponseSchema(BaseModel):
    newly_unlocked: List[AchievementItemSchema]
    total_unlocked: int
