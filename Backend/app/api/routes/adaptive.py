import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.adaptive import (
    AdaptiveRecalculateRequestSchema,
    AdaptiveApplyRequestSchema,
    AdaptationEventResponseSchema,
    AdaptiveSummaryResponseSchema,
)
from app.services.adaptive_service import AdaptiveService

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_user_id(current_user: Dict[str, Any]) -> str:
    return str(current_user.get("id") or current_user.get("_id"))


@router.get("/summary", response_model=AdaptiveSummaryResponseSchema)
async def get_adaptive_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch adaptive planner summary and current recommendation status."""
    user_id = _get_user_id(current_user)
    service = AdaptiveService(db)
    return await service.get_summary(user_id)


@router.post("/recalculate", response_model=AdaptationEventResponseSchema)
async def recalculate_adaptation(
    payload: Optional[AdaptiveRecalculateRequestSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Recalculate and analyze student task velocity to determine adaptations."""
    user_id = _get_user_id(current_user)
    service = AdaptiveService(db)
    roadmap_id = payload.roadmap_id if payload else None
    return await service.recalculate_adaptation(user_id, roadmap_id=roadmap_id)


@router.get("/recommendations", response_model=List[AdaptationEventResponseSchema])
async def get_adaptive_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch list of historical and pending adaptation recommendations."""
    user_id = _get_user_id(current_user)
    service = AdaptiveService(db)
    return await service.get_recommendations(user_id)


@router.post("/apply")
async def apply_adaptation(
    payload: Optional[AdaptiveApplyRequestSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Apply an adaptation recommendation to the active roadmap."""
    user_id = _get_user_id(current_user)
    service = AdaptiveService(db)
    adaptation_id = payload.adaptation_id if payload else None
    roadmap_id = payload.roadmap_id if payload else None
    return await service.apply_adaptation(
        user_id=user_id,
        adaptation_id=adaptation_id,
        roadmap_id=roadmap_id,
    )
