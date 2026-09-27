from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.mentor import (
    MentorConversationCreateSchema,
    MentorConversationResponseSchema,
    MentorConversationDetailResponseSchema,
    MentorMessageCreateSchema,
    MentorMessageResponseSchema,
    MentorAskSchema,
    MentorResponseSchema,
)
from app.services.mentor_service import MentorService

router = APIRouter()


def _extract_user_id(current_user: dict) -> str:
    return str(current_user.get("id") or current_user.get("_id") or current_user.get("user_id"))


def get_mentor_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> MentorService:
    return MentorService(db)


@router.post("/conversations", response_model=MentorConversationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: MentorConversationCreateSchema,
    current_user: dict = Depends(get_current_user),
    service: MentorService = Depends(get_mentor_service),
):
    """Create a new AI Mentor conversation session."""
    try:
        user_id = _extract_user_id(current_user)
        return await service.create_conversation(user_id=user_id, title=payload.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@router.get("/conversations", response_model=List[MentorConversationResponseSchema])
async def get_conversations(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: MentorService = Depends(get_mentor_service),
):
    """Fetch all mentor conversations for the authenticated student."""
    user_id = _extract_user_id(current_user)
    return await service.get_user_conversations(user_id=user_id, limit=limit)


@router.get("/conversations/{conversation_id}", response_model=MentorConversationDetailResponseSchema)
async def get_conversation_detail(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    service: MentorService = Depends(get_mentor_service),
):
    """Fetch single conversation metadata and message history."""
    user_id = _extract_user_id(current_user)
    conv = await service.get_conversation_detail(conversation_id=conversation_id, user_id=user_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Mentor conversation not found.")
    return conv


@router.post("/conversations/{conversation_id}/messages", response_model=MentorMessageResponseSchema)
async def send_message(
    conversation_id: str,
    payload: MentorMessageCreateSchema,
    current_user: dict = Depends(get_current_user),
    service: MentorService = Depends(get_mentor_service),
):
    """Send a query to the AI Mentor within an existing conversation."""
    user_id = _extract_user_id(current_user)
    conv = await service.get_conversation_detail(conversation_id=conversation_id, user_id=user_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Mentor conversation not found.")

    try:
        return await service.send_message(
            user_id=user_id,
            conversation_id=conversation_id,
            message_text=payload.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send mentor message: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def archive_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    service: MentorService = Depends(get_mentor_service),
):
    """Archive a mentor conversation session."""
    user_id = _extract_user_id(current_user)
    success = await service.archive_conversation(conversation_id=conversation_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mentor conversation not found.")
    return {"status": "success", "message": "Conversation archived."}


@router.post("/ask", response_model=MentorResponseSchema)
async def ask_mentor(
    payload: MentorAskSchema,
    current_user: dict = Depends(get_current_user),
    service: MentorService = Depends(get_mentor_service),
):
    """Quick single-query AI Mentor endpoint."""
    try:
        user_id = _extract_user_id(current_user)
        return await service.ask_mentor(
            user_id=user_id,
            message_text=payload.message,
            conversation_id=payload.conversation_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process mentor query: {str(e)}")


@router.get("/test")
async def test_mentor_route():
    """Placeholder health endpoint for test suite compatibility."""
    return {"status": "success", "module": "mentor", "message": "Mentor module is active."}

