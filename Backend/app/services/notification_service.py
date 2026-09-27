import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.notification_repository import NotificationRepository
from app.core.redis import redis_manager

logger = logging.getLogger(__name__)


class NotificationService:
    """Service handling notification logic, preference filtering, and deduplication."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.notification_repo = NotificationRepository(db)

    async def create_notification(
        self,
        user_id: str,
        notif_type: str,
        title: str,
        message: str,
        priority: str = "normal",
        action_type: Optional[str] = None,
        action_id: Optional[str] = None,
        action_route: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a notification after checking user preferences and deduplication."""
        # 1. Check user preferences
        prefs = await self.notification_repo.get_preferences(user_id)
        if notif_type == "task" and not prefs.get("task_reminders", True):
            return None
        if notif_type == "achievement" and not prefs.get("achievement_notifications", True):
            return None
        if notif_type == "roadmap" and not prefs.get("roadmap_notifications", True):
            return None
        if notif_type in ["interview", "communication"] and not prefs.get("interview_notifications", True):
            return None
        if notif_type == "general" and not prefs.get("general_notifications", True):
            return None

        # 2. Deduplication check via Redis if available
        dedup_key = f"notif_dedup:{user_id}:{notif_type}:{action_id or title[:20]}"
        if redis_manager.is_healthy():
            already_sent = await redis_manager.get(dedup_key)
            if already_sent:
                logger.info("Notification deduplicated via Redis key: %s", dedup_key)
                return None
            await redis_manager.set(dedup_key, "1", expire=3600)  # 1 hour deduplication window

        # 3. Build notification document
        notif_id = f"notif_{user_id}_{int(datetime.now(timezone.utc).timestamp())}_{uuid.uuid4().hex[:4]}"
        notif_data = {
            "notification_id": notif_id,
            "user_id": user_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "priority": priority,
            "read": False,
            "action_type": action_type,
            "action_id": action_id,
            "action_route": action_route or "/dashboard",
            "metadata": metadata or {},
        }

        return await self.notification_repo.create_notification(notif_data)

    async def get_user_notifications(self, user_id: str, limit: int = 50, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Fetch notification history for user."""
        return await self.notification_repo.get_user_notifications(user_id, limit=limit, unread_only=unread_only)

    async def get_unread_count(self, user_id: str) -> Dict[str, int]:
        """Fetch unread notifications count."""
        count = await self.notification_repo.get_unread_count(user_id)
        return {"unread_count": count}

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark single notification as read."""
        return await self.notification_repo.mark_as_read(notification_id, user_id=user_id)

    async def mark_all_as_read(self, user_id: str) -> Dict[str, Any]:
        """Mark all unread notifications as read."""
        modified = await self.notification_repo.mark_all_as_read(user_id)
        return {"status": "success", "modified_count": modified}

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete notification by ID."""
        return await self.notification_repo.delete_notification(notification_id, user_id=user_id)

    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user notification settings."""
        return await self.notification_repo.get_preferences(user_id)

    async def update_preferences(self, user_id: str, pref_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user notification settings."""
        return await self.notification_repo.update_preferences(user_id, pref_data)
