import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.progress import (
    ProgressResponseSchema,
    ProgressSummaryResponseSchema,
    StreakResponseSchema,
)
from app.services.progress_service import ProgressService

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_user_id(current_user: Dict[str, Any]) -> str:
    return str(current_user.get("id") or current_user.get("_id"))


@router.get("/test", status_code=status.HTTP_200_OK)
async def progress_test():
    """Placeholder test endpoint for progress router."""
    return {"status": "success", "module": "progress"}



@router.get("", response_model=ProgressResponseSchema)
async def get_progress(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch complete progress metrics for the authenticated user."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    return await service.get_progress(user_id)


@router.get("/summary", response_model=ProgressSummaryResponseSchema)
async def get_progress_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch high-level progress summary."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    return await service.get_summary(user_id)


@router.get("/daily")
async def get_daily_progress(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch daily completion metrics."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    p = await service.get_progress(user_id)
    return p.get("daily_completion", [])


@router.get("/weekly")
async def get_weekly_progress(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch weekly completion breakdown."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    p = await service.get_progress(user_id)
    return p.get("weekly_completion", [])


@router.get("/skills")
async def get_skills_progress(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch skill-wise completion progress map."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    p = await service.get_progress(user_id)
    return p.get("skill_progress", {})


@router.get("/streak", response_model=StreakResponseSchema)
async def get_streak(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch current activity streak and active status."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    return await service.get_streak(user_id)


@router.get("/history")
async def get_progress_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch historical progress snapshots."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    p = await service.get_progress(user_id)
    return {
        "daily_completion": p.get("daily_completion", []),
        "skill_progress": p.get("skill_progress", {}),
        "completed_milestones": p.get("completed_milestones", [])
    }
