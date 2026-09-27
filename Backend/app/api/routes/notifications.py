from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.notification import (
    NotificationResponseSchema,
    NotificationUnreadCountSchema,
    NotificationPreferencesSchema,
)
from app.services.notification_service import NotificationService

router = APIRouter()


def _extract_user_id(current_user: dict) -> str:
    return str(current_user.get("id") or current_user.get("_id") or current_user.get("user_id"))


def get_notification_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("", response_model=List[NotificationResponseSchema])
async def get_notifications(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Fetch notifications list for the authenticated student."""
    user_id = _extract_user_id(current_user)
    return await service.get_user_notifications(user_id=user_id, limit=limit)


@router.get("/unread", response_model=List[NotificationResponseSchema])
async def get_unread_notifications(
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Fetch unread notifications for the authenticated student."""
    user_id = _extract_user_id(current_user)
    return await service.get_user_notifications(user_id=user_id, limit=limit, unread_only=True)


@router.get("/count", response_model=NotificationUnreadCountSchema)
async def get_unread_notification_count(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Fetch total unread notifications count."""
    user_id = _extract_user_id(current_user)
    return await service.get_unread_count(user_id=user_id)


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark a single notification as read."""
    user_id = _extract_user_id(current_user)
    success = await service.mark_as_read(notification_id=notification_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"status": "success", "message": "Notification marked as read."}


@router.post("/read-all")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Mark all unread notifications as read."""
    user_id = _extract_user_id(current_user)
    return await service.mark_all_as_read(user_id=user_id)


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Delete a notification."""
    user_id = _extract_user_id(current_user)
    success = await service.delete_notification(notification_id=notification_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"status": "success", "message": "Notification deleted."}


@router.get("/preferences", response_model=NotificationPreferencesSchema)
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Retrieve user notification preferences."""
    user_id = _extract_user_id(current_user)
    return await service.get_preferences(user_id=user_id)


@router.put("/preferences", response_model=NotificationPreferencesSchema)
async def update_notification_preferences(
    payload: NotificationPreferencesSchema,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Update user notification preferences."""
    user_id = _extract_user_id(current_user)
    return await service.update_preferences(user_id=user_id, pref_data=payload.model_dump())


@router.get("/test")
async def test_notifications_route() -> dict:
    """Placeholder health endpoint for test suite compatibility."""
    return {
        "status": "success",
        "module": "notifications",
        "message": "Notifications router operational",
    }
