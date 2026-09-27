from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.achievement import (
    AchievementsResponseSchema,
    AchievementItemSchema,
    AchievementStatsSchema,
    AchievementCheckResponseSchema,
)
from app.services.achievement_service import AchievementService

router = APIRouter()


def _extract_user_id(current_user: dict) -> str:
    return str(current_user.get("id") or current_user.get("_id") or current_user.get("user_id"))


def get_achievement_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> AchievementService:
    return AchievementService(db)


@router.get("", response_model=AchievementsResponseSchema)
async def get_achievements(
    current_user: dict = Depends(get_current_user),
    service: AchievementService = Depends(get_achievement_service),
):
    """Fetch all achievements with user progress and calculated summary stats."""
    user_id = _extract_user_id(current_user)
    return await service.get_user_achievements_with_progress(user_id)


@router.get("/unlocked", response_model=List[AchievementItemSchema])
async def get_unlocked_achievements(
    current_user: dict = Depends(get_current_user),
    service: AchievementService = Depends(get_achievement_service),
):
    """Fetch only unlocked achievements for the authenticated user."""
    user_id = _extract_user_id(current_user)
    return await service.get_unlocked_achievements(user_id)


@router.get("/progress", response_model=AchievementStatsSchema)
async def get_achievement_progress(
    current_user: dict = Depends(get_current_user),
    service: AchievementService = Depends(get_achievement_service),
):
    """Fetch achievement progress summary statistics."""
    user_id = _extract_user_id(current_user)
    data = await service.get_user_achievements_with_progress(user_id)
    return data["stats"]


@router.post("/check", response_model=AchievementCheckResponseSchema)
async def check_achievements(
    current_user: dict = Depends(get_current_user),
    service: AchievementService = Depends(get_achievement_service),
):
    """Manually evaluate user achievements and return newly unlocked items."""
    user_id = _extract_user_id(current_user)
    newly_unlocked = await service.evaluate_and_unlock(user_id)
    unlocked_list = await service.get_unlocked_achievements(user_id)
    return {
        "newly_unlocked": newly_unlocked,
        "total_unlocked": len(unlocked_list),
    }


@router.get("/test")
async def test_achievements_route() -> dict:
    """Placeholder health endpoint for test suite compatibility."""
    return {
        "status": "success",
        "module": "achievements",
        "message": "Achievements router operational",
    }


@router.get("/{achievement_id}", response_model=AchievementItemSchema)
async def get_achievement_by_id(
    achievement_id: str,
    current_user: dict = Depends(get_current_user),
    service: AchievementService = Depends(get_achievement_service),
):
    """Fetch single achievement details by ID or code."""
    user_id = _extract_user_id(current_user)
    ach = await service.get_achievement_by_id(achievement_id, user_id=user_id)
    if not ach:
        raise HTTPException(status_code=404, detail="Achievement not found.")
    return ach
