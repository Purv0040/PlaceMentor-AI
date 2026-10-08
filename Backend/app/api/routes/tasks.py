import logging
from typing import Optional, List, Dict, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
)

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import (
    get_db,
    get_current_user,
)

from app.schemas.daily_task import (
    TasksTestResponseSchema,
    DailyTaskCreateSchema,
    DailyTaskUpdateSchema,
    DailyTaskStatusUpdateSchema,
    DailyTaskCompleteSchema,
    DailyTaskSkipSchema,
    DailyTaskResponseSchema,
    TodayTasksResponseSchema,
)

from app.schemas.progress import (
    ProgressSummaryResponseSchema,
    StreakResponseSchema,
)

from app.services.task_service import TaskService
from app.services.progress_service import ProgressService


logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# HELPER
# ============================================================

def _get_user_id(
    current_user: Dict[str, Any],
) -> str:
    """
    Extract authenticated user ID from current user.
    """

    user_id = (
        current_user.get("id")
        or current_user.get("_id")
    )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user ID not found.",
        )

    return str(user_id)


# ============================================================
# TEST
# ============================================================

@router.get(
    "/test",
    response_model=TasksTestResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Tasks Test",
    description="Test endpoint for the Tasks router.",
)
async def tasks_test() -> TasksTestResponseSchema:
    """
    Test endpoint for Tasks router.
    """

    return {
        "status": "success",
        "module": "tasks",
    }


# ============================================================
# TODAY
# ============================================================

@router.get(
    "/today",
    response_model=TodayTasksResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get today's tasks",
)
async def get_today_tasks(
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Get today's dynamically generated tasks
    for the authenticated user.
    """

    user_id = _get_user_id(
        current_user
    )

    service = TaskService(db)

    return await service.get_today_tasks(
        user_id
    )


# ============================================================
# PROGRESS
# ============================================================

@router.get(
    "/progress",
    response_model=ProgressSummaryResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get task progress",
)
async def get_tasks_progress(
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Get dynamically calculated task progress.
    """

    user_id = _get_user_id(
        current_user
    )

    service = ProgressService(db)

    return await service.get_summary(
        user_id
    )


# ============================================================
# STREAK
# ============================================================

@router.get(
    "/streak",
    response_model=StreakResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get task streak",
)
async def get_tasks_streak(
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Get dynamically calculated task streak.
    """

    user_id = _get_user_id(
        current_user
    )

    service = ProgressService(db)

    return await service.get_streak(
        user_id
    )


# ============================================================
# GENERATE
# ============================================================

@router.post(
    "/generate",
    response_model=TodayTasksResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Generate today's tasks",
)
async def generate_daily_tasks(
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Generate today's tasks from the user's
    active roadmap.
    """

    user_id = _get_user_id(
        current_user
    )

    service = TaskService(db)

    return await service.generate_today_tasks(
        user_id
    )


# ============================================================
# GET ALL TASKS
# ============================================================

@router.get(
    "",
    response_model=List[DailyTaskResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get all tasks",
)
async def get_all_tasks(
    status_filter: Optional[str] = Query(
        default=None,
        alias="status",
        description="Filter tasks by status.",
    ),
    category_filter: Optional[str] = Query(
        default=None,
        alias="category",
        description="Filter tasks by category.",
    ),
    date_filter: Optional[str] = Query(
        default=None,
        alias="date",
        description="Filter tasks by date.",
    ),
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Get all tasks for the authenticated user.

    Optional filters:
    - status
    - category
    - date
    """

    user_id = _get_user_id(
        current_user
    )

    service = TaskService(db)

    return await service.get_all_tasks(
        user_id=user_id,
        status=status_filter,
        category=category_filter,
        date_str=date_filter,
    )


# ============================================================
# GET TASK BY ID
# ============================================================

@router.get(
    "/{task_id}",
    response_model=DailyTaskResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
)
async def get_task_by_id(
    task_id: str,
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Get a specific task belonging to
    the authenticated user.
    """

    user_id = _get_user_id(
        current_user
    )

    service = TaskService(db)

    task = await service.get_task_by_id(
        task_id,
        user_id,
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return task


# ============================================================
# CREATE TASK
# ============================================================

@router.post(
    "",
    response_model=DailyTaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create task",
)
async def create_task(
    payload: DailyTaskCreateSchema,
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Create a new task for the authenticated user.
    """

    user_id = _get_user_id(
        current_user
    )

    service = TaskService(db)

    return await service.create_task(
        user_id=user_id,
        task_data=payload.model_dump(
            exclude_none=True
        ),
    )


# ============================================================
# UPDATE TASK
# ============================================================

@router.patch(
    "/{task_id}",
    response_model=DailyTaskResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update task",
)
async def update_task(
    task_id: str,
    payload: DailyTaskUpdateSchema,
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Update task fields.

    Supports fields such as:
    - title
    - description
    - category
    - difficulty
    - estimated_minutes
    - actual_minutes
    - status
    - notes
    - resource
    """

    user_id = _get_user_id(
        current_user
    )

    update_data = payload.model_dump(
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    service = TaskService(db)

    updated = await service.update_task(
        task_id=task_id,
        user_id=user_id,
        update_data=update_data,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return updated


# ============================================================
# UPDATE STATUS
# ============================================================

@router.patch(
    "/{task_id}/status",
    response_model=DailyTaskResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update task status",
)
async def update_task_status(
    task_id: str,
    payload: DailyTaskStatusUpdateSchema,
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Update task status.

    Supported statuses:
    - pending
    - in_progress
    - completed
    - skipped
    """

    user_id = _get_user_id(
        current_user
    )

    service = TaskService(db)

    updated = await service.update_task_status(
        task_id=task_id,
        user_id=user_id,
        status=payload.status,
        actual_minutes=payload.actual_minutes,
        notes=payload.notes,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return updated


# ============================================================
# COMPLETE TASK
# ============================================================

@router.post(
    "/{task_id}/complete",
    response_model=DailyTaskResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Complete task",
)
async def complete_task(
    task_id: str,
    payload: Optional[
        DailyTaskCompleteSchema
    ] = None,
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Mark a task as completed.
    """

    user_id = _get_user_id(
        current_user
    )

    actual_minutes = (
        payload.actual_minutes
        if payload
        else None
    )

    notes = (
        payload.notes
        if payload
        else None
    )

    service = TaskService(db)

    updated = await service.complete_task(
        task_id=task_id,
        user_id=user_id,
        actual_minutes=actual_minutes,
        notes=notes,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return updated


# ============================================================
# SKIP TASK
# ============================================================

@router.post(
    "/{task_id}/skip",
    response_model=DailyTaskResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Skip task",
)
async def skip_task(
    task_id: str,
    payload: Optional[
        DailyTaskSkipSchema
    ] = None,
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
    db: AsyncIOMotorDatabase = Depends(
        get_db
    ),
):
    """
    Skip a task.
    """

    user_id = _get_user_id(
        current_user
    )

    reason = (
        payload.reason
        if payload
        else None
    )

    service = TaskService(db)

    updated = await service.skip_task(
        task_id=task_id,
        user_id=user_id,
        reason=reason,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return updated