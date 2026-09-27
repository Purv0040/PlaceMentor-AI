from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.communication import (
    CommunicationAnalyzeRequestSchema,
    CommunicationResponseSchema,
    CommunicationSummaryResponseSchema,
)
from app.services.communication_service import CommunicationService

router = APIRouter()


def _extract_user_id(current_user: dict) -> str:
    return str(current_user.get("id") or current_user.get("_id") or current_user.get("user_id"))


def get_communication_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> CommunicationService:
    return CommunicationService(db)


@router.get("/test", status_code=status.HTTP_200_OK)
async def communication_test():
    """Placeholder health endpoint for communication router."""
    return {"status": "success", "module": "communication"}



@router.post("/analyze", response_model=CommunicationResponseSchema, status_code=status.HTTP_201_CREATED)
async def analyze_communication(
    payload: CommunicationAnalyzeRequestSchema,
    current_user: dict = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    """Analyze student answer for verbal clarity, structure, conciseness, and filler words."""
    try:
        user_id = _extract_user_id(current_user)
        return await service.analyze_communication(
            user_id=user_id,
            question=payload.question,
            answer=payload.answer,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze communication: {str(e)}")


@router.get("/summary", response_model=CommunicationSummaryResponseSchema)
async def get_communication_summary(
    current_user: dict = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    """Fetch aggregate communication practice summary & recurring feedback."""
    user_id = _extract_user_id(current_user)
    return await service.get_summary(user_id)


@router.get("/history", response_model=List[CommunicationResponseSchema])
async def get_communication_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    """Fetch practice history of communication analyses."""
    user_id = _extract_user_id(current_user)
    return await service.get_history(user_id, limit=limit)


@router.get("/{analysis_id}", response_model=CommunicationResponseSchema)
async def get_communication_analysis_by_id(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    service: CommunicationService = Depends(get_communication_service),
):
    """Fetch specific communication analysis by ID."""
    user_id = _extract_user_id(current_user)
    doc = await service.get_by_id(analysis_id, user_id=user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Communication analysis not found.")
    return doc
