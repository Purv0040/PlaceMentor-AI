import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.roadmap import (
    RoadmapGenerateRequestSchema,
    RoadmapUpdateSchema,
    RoadmapResponseSchema,
    RoadmapSummaryResponseSchema,
)
from app.services.roadmap_service import RoadmapService

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_user_id(current_user: Dict[str, Any]) -> str:
    return str(current_user.get("id") or current_user.get("_id"))


@router.get("/test", status_code=status.HTTP_200_OK)
async def roadmap_test():
    """Placeholder test endpoint for roadmap router."""
    return {"status": "success", "module": "roadmap"}



@router.post("/generate", response_model=RoadmapResponseSchema)
async def generate_roadmap(
    payload: Optional[RoadmapGenerateRequestSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Generate a personalized 90-day preparation roadmap based on student intelligence."""
    user_id = _get_user_id(current_user)
    target_role = payload.target_role if payload else None
    daily_mins = payload.available_minutes_per_day if payload else 120
    force = payload.force_regenerate if payload else False

    service = RoadmapService(db)
    roadmap = await service.generate_roadmap(
        user_id=user_id,
        target_role=target_role,
        available_minutes_per_day=daily_mins,
        force_regenerate=force,
    )
    return roadmap


@router.post("/regenerate", response_model=RoadmapResponseSchema)
async def regenerate_roadmap(
    payload: Optional[RoadmapGenerateRequestSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Force regenerate a new 90-day roadmap."""
    user_id = _get_user_id(current_user)
    target_role = payload.target_role if payload else None
    daily_mins = payload.available_minutes_per_day if payload else 120

    service = RoadmapService(db)
    roadmap = await service.generate_roadmap(
        user_id=user_id,
        target_role=target_role,
        available_minutes_per_day=daily_mins,
        force_regenerate=True,
    )
    return roadmap


@router.get("", response_model=RoadmapResponseSchema)
async def get_active_roadmap(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch active roadmap for the authenticated user."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    roadmap = await service.get_active_roadmap(user_id)
    if not roadmap:
        roadmap = await service.generate_roadmap(user_id=user_id)
    return roadmap


@router.get("/summary", response_model=RoadmapSummaryResponseSchema)
async def get_roadmap_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch high-level 90-day roadmap progress summary."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    return await service.get_summary(user_id)


@router.get("/{roadmap_id}", response_model=RoadmapResponseSchema)
async def get_roadmap_by_id(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch specific roadmap by ID."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    roadmap = await service.get_roadmap_by_id(roadmap_id, user_id)
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
    return roadmap


@router.patch("/{roadmap_id}", response_model=RoadmapResponseSchema)
async def update_roadmap(
    roadmap_id: str,
    payload: RoadmapUpdateSchema,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update roadmap fields (title, description, status)."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = await service.update_roadmap(roadmap_id, user_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
    return updated


@router.delete("/{roadmap_id}")
async def delete_roadmap(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Delete a roadmap record."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    deleted = await service.delete_roadmap(roadmap_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found.")
    return {"status": "success", "message": "Roadmap deleted successfully."}


@router.get("/{roadmap_id}/weeks")
async def get_roadmap_weeks(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch weekly goals breakdown for a roadmap."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    return await service.get_roadmap_weeks(roadmap_id, user_id)


@router.get("/{roadmap_id}/phases")
async def get_roadmap_phases(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch 3-phase structure for a roadmap."""
    user_id = _get_user_id(current_user)
    service = RoadmapService(db)
    return await service.get_roadmap_phases(roadmap_id, user_id)
