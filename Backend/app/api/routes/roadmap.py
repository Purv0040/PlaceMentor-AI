import logging
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
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
    """
    Extract authenticated user ID safely.
    """
    user_id = current_user.get("id") or current_user.get("_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user ID not found.",
        )

    return str(user_id)


@router.get(
    "/test",
    status_code=status.HTTP_200_OK,
)
async def roadmap_test():
    """
    Test endpoint for roadmap router.
    """
    return {
        "status": "success",
        "module": "roadmap",
    }


@router.post(
    "/generate",
    response_model=RoadmapResponseSchema,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Roadmap generation failed."
        },
        401: {
            "description": "Authentication required."
        },
        500: {
            "description": "Internal roadmap generation error."
        },
    },
)
async def generate_roadmap(
    payload: Optional[RoadmapGenerateRequestSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Generate a personalized 90-day preparation roadmap.
    """

    user_id = _get_user_id(current_user)

    target_role = payload.target_role if payload else None
    daily_minutes = (
        payload.available_minutes_per_day
        if payload
        else 120
    )
    force_regenerate = (
        payload.force_regenerate
        if payload
        else False
    )

    service = RoadmapService(db)

    try:
        roadmap = await service.generate_roadmap(
            user_id=user_id,
            target_role=target_role,
            available_minutes_per_day=daily_minutes,
            force_regenerate=force_regenerate,
        )

        return roadmap

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Roadmap generation failed for user %s",
            user_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap generation failed: {str(exc)}",
        )


@router.post(
    "/regenerate",
    response_model=RoadmapResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def regenerate_roadmap(
    payload: Optional[RoadmapGenerateRequestSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Force regenerate a new 90-day roadmap.
    """

    user_id = _get_user_id(current_user)

    target_role = payload.target_role if payload else None

    daily_minutes = (
        payload.available_minutes_per_day
        if payload
        else 120
    )

    service = RoadmapService(db)

    try:
        roadmap = await service.generate_roadmap(
            user_id=user_id,
            target_role=target_role,
            available_minutes_per_day=daily_minutes,
            force_regenerate=True,
        )

        return roadmap

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Roadmap regeneration failed for user %s",
            user_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap regeneration failed: {str(exc)}",
        )


@router.get(
    "",
    response_model=RoadmapResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_active_roadmap(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Fetch active roadmap for authenticated user.

    If no active roadmap exists, generate one dynamically.
    """

    user_id = _get_user_id(current_user)

    service = RoadmapService(db)

    roadmap = await service.get_active_roadmap(user_id)

    if not roadmap:
        roadmap = await service.generate_roadmap(
            user_id=user_id
        )

    return roadmap


@router.get(
    "/summary",
    response_model=RoadmapSummaryResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_roadmap_summary(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Fetch high-level 90-day roadmap progress summary.
    """

    user_id = _get_user_id(current_user)

    service = RoadmapService(db)

    return await service.get_summary(user_id)


@router.get(
    "/{roadmap_id}",
    response_model=RoadmapResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_roadmap_by_id(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Fetch a specific roadmap belonging to the authenticated user.
    """

    user_id = _get_user_id(current_user)

    service = RoadmapService(db)

    roadmap = await service.get_roadmap_by_id(
        roadmap_id,
        user_id,
    )

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found.",
        )

    return roadmap


@router.patch(
    "/{roadmap_id}",
    response_model=RoadmapResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_roadmap(
    roadmap_id: str,
    payload: RoadmapUpdateSchema,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Update roadmap fields.
    """

    user_id = _get_user_id(current_user)

    update_data = payload.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    service = RoadmapService(db)

    updated = await service.update_roadmap(
        roadmap_id,
        user_id,
        update_data,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found.",
        )

    return updated


@router.delete(
    "/{roadmap_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_roadmap(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Delete a roadmap belonging to the authenticated user.
    """

    user_id = _get_user_id(current_user)

    service = RoadmapService(db)

    deleted = await service.delete_roadmap(
        roadmap_id,
        user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found.",
        )

    return {
        "status": "success",
        "message": "Roadmap deleted successfully.",
    }


@router.get(
    "/{roadmap_id}/weeks",
    status_code=status.HTTP_200_OK,
)
async def get_roadmap_weeks(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Fetch weekly goals for a roadmap.
    """

    user_id = _get_user_id(current_user)

    service = RoadmapService(db)

    roadmap = await service.get_roadmap_by_id(
        roadmap_id,
        user_id,
    )

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found.",
        )

    return await service.get_roadmap_weeks(
        roadmap_id,
        user_id,
    )


@router.get(
    "/{roadmap_id}/phases",
    status_code=status.HTTP_200_OK,
)
async def get_roadmap_phases(
    roadmap_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Fetch three-phase roadmap structure.
    """

    user_id = _get_user_id(current_user)

    service = RoadmapService(db)

    roadmap = await service.get_roadmap_by_id(
        roadmap_id,
        user_id,
    )

    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found.",
        )

    return await service.get_roadmap_phases(
        roadmap_id,
        user_id,
    )