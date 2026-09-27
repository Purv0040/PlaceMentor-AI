from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.interview import (
    InterviewCreateSchema,
    InterviewAnswerSchema,
    InterviewQuestionResponseSchema,
    InterviewSessionResponseSchema,
    InterviewResultResponseSchema,
)
from app.services.interview_service import InterviewService

router = APIRouter()


def _extract_user_id(current_user: dict) -> str:
    return str(current_user.get("id") or current_user.get("_id") or current_user.get("user_id"))


def get_interview_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> InterviewService:
    return InterviewService(db)


@router.get("/test", status_code=status.HTTP_200_OK)
async def interviews_test():
    """Placeholder health endpoint for interviews router."""
    return {"status": "success", "module": "interviews"}



@router.post("", response_model=InterviewSessionResponseSchema, status_code=status.HTTP_201_CREATED)
async def start_interview(
    payload: InterviewCreateSchema,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Start a new mock interview session and generate the first role-grounded question."""
    try:
        user_id = _extract_user_id(current_user)
        return await service.start_mock_interview(
            user_id=user_id,
            interview_type=payload.interview_type,
            difficulty=payload.difficulty,
            question_count=payload.question_count,
            target_role_override=payload.target_role,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start mock interview: {str(e)}")


@router.get("/history", response_model=List[InterviewSessionResponseSchema])
async def get_interview_history_alias(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Fetch past mock interview sessions for current user."""
    user_id = _extract_user_id(current_user)
    return await service.get_interview_history(user_id, limit=limit)


@router.get("", response_model=List[InterviewSessionResponseSchema])
async def get_interview_history(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Fetch past mock interview sessions for current user."""
    user_id = _extract_user_id(current_user)
    return await service.get_interview_history(user_id, limit=limit)


@router.get("/{interview_id}/current")
async def get_current_question(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Fetch active question for interview session."""
    user_id = _extract_user_id(current_user)
    session = await service.get_session_by_id(interview_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    data = await service.get_current_question(interview_id, user_id=user_id)
    if not data or not data.get("session"):
        raise HTTPException(status_code=404, detail="Interview session or current question not found.")
    return data


@router.get("/{interview_id}/questions", response_model=List[InterviewQuestionResponseSchema])
async def get_interview_questions(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Fetch all questions for a specific interview session."""
    user_id = _extract_user_id(current_user)
    session = await service.get_session_by_id(interview_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return await service.get_interview_questions(interview_id, user_id=user_id)


@router.get("/{interview_id}", response_model=InterviewSessionResponseSchema)
async def get_interview_session(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Fetch interview session details by ID."""
    user_id = _extract_user_id(current_user)
    session = await service.get_session_by_id(interview_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session


@router.post("/{interview_id}/answer")
async def submit_answer(
    interview_id: str,
    payload: InterviewAnswerSchema,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Submit candidate answer for current question."""
    user_id = _extract_user_id(current_user)
    session = await service.get_session_by_id(interview_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    try:
        return await service.submit_answer(
            interview_id=interview_id,
            user_id=user_id,
            answer=payload.answer,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")


@router.post("/{interview_id}/complete")
async def complete_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Manually complete an interview session and compute final overall scores."""
    user_id = _extract_user_id(current_user)
    session = await service.get_session_by_id(interview_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    try:
        return await service.complete_interview(interview_id=interview_id, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete interview: {str(e)}")
