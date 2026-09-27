import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.skill_gap import (
    SkillGapAnalyzeRequest,
    SkillGapResponse,
    SkillGapSummaryResponse,
    SkillGapHistoryResponse,
)
from app.services.skill_gap_service import SkillGapService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def analyze_skill_gaps(
    request_data: Optional[SkillGapAnalyzeRequest] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Synthesize multi-module student telemetry and compute deterministic skill gaps with AI recommendations.
    """
    user_id = str(current_user["id"])
    target_role = request_data.target_role if request_data else None
    service = SkillGapService(db)
    analysis = await service.analyze_skill_gaps(user_id, target_role_override=target_role)
    return {
        "status": "success",
        "message": "Skill gap analysis completed successfully.",
        "data": analysis
    }


@router.get("", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_latest_skill_gaps(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve the most recent computed skill gap analysis for the authenticated user.
    """
    user_id = str(current_user["id"])
    service = SkillGapService(db)
    analysis = await service.get_latest_skill_gaps(user_id)
    return {
        "status": "success",
        "data": analysis
    }


@router.get("/summary", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_skill_gap_summary(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve a lightweight summary of skill gaps suitable for the main dashboard.
    """
    user_id = str(current_user["id"])
    service = SkillGapService(db)
    summary_data = await service.get_skill_gap_summary(user_id)
    return {
        "status": "success",
        "data": summary_data
    }


@router.get("/history", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_skill_gap_history(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve historical skill gap snapshots for the authenticated user.
    """
    user_id = str(current_user["id"])
    service = SkillGapService(db)
    history_items = await service.get_skill_gap_history(user_id, limit=limit)
    return {
        "status": "success",
        "data": {
            "items": history_items,
            "total": len(history_items)
        }
    }


@router.get("/test")
async def test_skill_gaps_route() -> dict:
    """Placeholder test endpoint for backward compatibility."""
    return {
        "status": "success",
        "module": "skill_gaps",
        "message": "Skill Gaps router operational",
    }


@router.get("/{analysis_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def get_skill_gap_by_id(
    analysis_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve a specific historical skill gap analysis snapshot by ID.
    """
    user_id = str(current_user["id"])
    service = SkillGapService(db)
    analysis = await service.get_analysis_by_id(analysis_id, user_id=user_id)
    return {
        "status": "success",
        "data": analysis
    }
