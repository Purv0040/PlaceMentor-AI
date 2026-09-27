import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class NotificationRepository:
    """Repository handling raw MongoDB queries for notifications and notification_preferences."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.notifications = db["notifications"]
        self.preferences = db["notification_preferences"]

    async def ensure_indexes(self) -> None:
        """Create database indexes."""
        try:
            await self.notifications.create_index([("user_id", 1), ("created_at", -1)])
            await self.notifications.create_index([("user_id", 1), ("read", 1)])
            await self.preferences.create_index("user_id", unique=True)
            logger.info("NotificationRepository indexes created/verified.")
        except Exception as e:
            logger.warning("Error creating indexes in NotificationRepository: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            doc["_id"] = str(doc["_id"])
        return doc

    async def create_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new notification document."""
        await self.ensure_indexes()
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        data["read"] = data.get("read", False)
        result = await self.notifications.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["id"] = str(data.get("id") or data.get("notification_id") or data["_id"])
        return self._convert_doc(data)

    async def get_user_notifications(
        self, user_id: str, limit: int = 50, unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch notifications list for user sorted newest first."""
        query: Dict[str, Any] = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        cursor = self.notifications.find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc(d) for d in docs if d]

    async def get_unread_count(self, user_id: str) -> int:
        """Count total unread notifications for user."""
        return await self.notifications.count_documents({"user_id": user_id, "read": False})

    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark single notification as read."""
        now = datetime.now(timezone.utc)
        or_conds: List[Dict[str, Any]] = [{"notification_id": notification_id}, {"_id": notification_id}, {"id": notification_id}]
        if ObjectId.is_valid(notification_id):
            or_conds.append({"_id": ObjectId(notification_id)})

        query = {"user_id": user_id, "$or": or_conds}
        res = await self.notifications.update_one(query, {"$set": {"read": True, "read_at": now}})
        return res.modified_count > 0 or res.matched_count > 0

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all unread notifications for user as read."""
        now = datetime.now(timezone.utc)
        res = await self.notifications.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True, "read_at": now}}
        )
        return res.modified_count

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification by ID."""
        or_conds: List[Dict[str, Any]] = [{"notification_id": notification_id}, {"_id": notification_id}, {"id": notification_id}]
        if ObjectId.is_valid(notification_id):
            or_conds.append({"_id": ObjectId(notification_id)})

        query = {"user_id": user_id, "$or": or_conds}
        res = await self.notifications.delete_one(query)
        return res.deleted_count > 0

    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Fetch user notification preferences or return defaults."""
        doc = await self.preferences.find_one({"user_id": user_id})
        if not doc:
            return {
                "user_id": user_id,
                "task_reminders": True,
                "achievement_notifications": True,
                "roadmap_notifications": True,
                "interview_notifications": True,
                "general_notifications": True,
            }
        return self._convert_doc(doc)

    async def update_preferences(self, user_id: str, pref_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification preferences."""
        pref_data["user_id"] = user_id
        pref_data["updated_at"] = datetime.now(timezone.utc)
        await self.preferences.update_one(
            {"user_id": user_id},
            {"$set": pref_data},
            upsert=True
        )
        return await self.get_preferences(user_id)
