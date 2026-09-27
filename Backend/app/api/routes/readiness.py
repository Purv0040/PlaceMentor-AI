import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.readiness import (
    ReadinessAnalyzeRequest,
    ReadinessResponse,
    ReadinessSingleResponse,
    ReadinessSummaryResponse,
    ReadinessHistoryResponse
)
from app.services.readiness_service import ReadinessService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=ReadinessSingleResponse, status_code=status.HTTP_200_OK)
async def analyze_readiness(
    req: Optional[ReadinessAnalyzeRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Trigger recalculation of student Placement Readiness across all 7 diagnostic vectors."""
    user_id = str(current_user["id"])
    target_role = req.target_role if req else None
    service = ReadinessService(db)
    analysis = await service.analyze_readiness(user_id, target_role_override=target_role)
    return ReadinessSingleResponse(
        success=True,
        message="Placement readiness analysis calculated successfully.",
        data=analysis
    )


@router.get("", response_model=ReadinessSingleResponse)
async def get_latest_readiness(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve the latest Placement Readiness analysis for authenticated student."""
    user_id = str(current_user["id"])
    service = ReadinessService(db)
    analysis = await service.get_latest_readiness(user_id)
    return ReadinessSingleResponse(
        success=True,
        message="Latest placement readiness retrieved successfully.",
        data=analysis
    )


@router.get("/summary", response_model=ReadinessSummaryResponse)
async def get_readiness_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve lightweight readiness score summary for application dashboard."""
    user_id = str(current_user["id"])
    service = ReadinessService(db)
    summary = await service.get_readiness_summary(user_id)
    return ReadinessSummaryResponse(
        success=True,
        message="Placement readiness summary retrieved.",
        data=summary
    )


@router.get("/history", response_model=ReadinessHistoryResponse)
async def get_readiness_history(
    limit: int = Query(10, ge=1, le=50, description="Number of historical snapshots to retrieve"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve historical calculation snapshots for progress tracking."""
    user_id = str(current_user["id"])
    service = ReadinessService(db)
    history = await service.get_readiness_history(user_id, limit=limit)
    return ReadinessHistoryResponse(
        success=True,
        total=len(history),
        data=history
    )


@router.get("/{analysis_id}", response_model=ReadinessSingleResponse)
async def get_readiness_by_id(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch specific historical readiness analysis by ID with ownership verification."""
    user_id = str(current_user["id"])
    service = ReadinessService(db)
    analysis = await service.get_analysis_by_id(analysis_id, user_id)
    return ReadinessSingleResponse(
        success=True,
        message="Readiness analysis details retrieved.",
        data=analysis
    )
