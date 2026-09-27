import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.daily_task import (
    DailyTaskCreateSchema,
    DailyTaskUpdateSchema,
    DailyTaskStatusUpdateSchema,
    DailyTaskCompleteSchema,
    DailyTaskSkipSchema,
    DailyTaskResponseSchema,
    TodayTasksResponseSchema,
)
from app.services.task_service import TaskService
from app.services.progress_service import ProgressService

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_user_id(current_user: Dict[str, Any]) -> str:
    return str(current_user.get("id") or current_user.get("_id"))


@router.get("/test", status_code=status.HTTP_200_OK)
async def tasks_test():
    """Placeholder test endpoint for tasks router."""
    return {"status": "success", "module": "tasks"}



@router.get("/today", response_model=TodayTasksResponseSchema)
async def get_today_tasks(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch today's scheduled tasks for the authenticated student."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    return await service.get_today_tasks(user_id)


@router.get("/progress")
async def get_tasks_progress(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch user task completion progress summary."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    return await service.get_summary(user_id)


@router.get("/streak")
async def get_tasks_streak(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch current activity streak and active status."""
    user_id = _get_user_id(current_user)
    service = ProgressService(db)
    return await service.get_streak(user_id)


@router.post("/generate")
async def generate_daily_tasks(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Force generate today's tasks from active roadmap."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    return await service.get_today_tasks(user_id)


@router.get("", response_model=List[DailyTaskResponseSchema])
async def get_all_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    category_filter: Optional[str] = Query(None, alias="category"),
    date_filter: Optional[str] = Query(None, alias="date"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """List all daily tasks for the user with optional filters."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    return await service.get_all_tasks(
        user_id=user_id,
        status=status_filter,
        category=category_filter,
        date_str=date_filter,
    )


@router.get("/{task_id}", response_model=DailyTaskResponseSchema)
async def get_task_by_id(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Fetch task by ID."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    task = await service.get_task_by_id(task_id, user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task


@router.post("", response_model=DailyTaskResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: DailyTaskCreateSchema,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Create a new custom daily task."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    return await service.create_task(user_id, payload.model_dump())


@router.patch("/{task_id}", response_model=DailyTaskResponseSchema)
async def update_task(
    task_id: str,
    payload: DailyTaskUpdateSchema,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update task details."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    updated = await service.update_task(task_id, user_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return updated


@router.patch("/{task_id}/status", response_model=DailyTaskResponseSchema)
async def update_task_status(
    task_id: str,
    payload: DailyTaskStatusUpdateSchema,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Update task status ('pending', 'in_progress', 'completed', 'skipped')."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    updated = await service.update_task_status(
        task_id=task_id,
        user_id=user_id,
        status=payload.status,
        actual_minutes=payload.actual_minutes,
        notes=payload.notes,
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return updated


@router.post("/{task_id}/complete", response_model=DailyTaskResponseSchema)
async def complete_task(
    task_id: str,
    payload: Optional[DailyTaskCompleteSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Mark a task as completed."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    actual_mins = payload.actual_minutes if payload else None
    notes = payload.notes if payload else None
    updated = await service.complete_task(
        task_id=task_id, user_id=user_id, actual_minutes=actual_mins, notes=notes
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return updated


@router.post("/{task_id}/skip", response_model=DailyTaskResponseSchema)
async def skip_task(
    task_id: str,
    payload: Optional[DailyTaskSkipSchema] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Mark a task as skipped."""
    user_id = _get_user_id(current_user)
    service = TaskService(db)
    reason = payload.reason if payload else None
    updated = await service.skip_task(task_id=task_id, user_id=user_id, reason=reason)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return updated
