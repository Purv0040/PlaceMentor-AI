import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class LeetCodeRepository:
    """Database access layer for LeetCode profiles in MongoDB Atlas."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.profiles = db["leetcode_profiles"]

    async def init_indexes(self) -> None:
        """Create indexes idempotently for uniqueness and performance."""
        try:
            await self.profiles.create_index("user_id", unique=True)
        except Exception as e:
            logger.warning("Could not create LeetCode indexes: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        res = dict(doc)
        if "_id" in res:
            res["id"] = str(res["_id"])
            res["_id"] = str(res["_id"])
        return res

    async def find_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve LeetCode profile for authenticated user."""
        doc = await self.profiles.find_one({"user_id": str(user_id)})
        return self._convert_doc(doc)

    async def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve profile document by LeetCode username."""
        doc = await self.profiles.find_one({"leetcode_username": username.strip()})
        return self._convert_doc(doc)

    async def upsert_leetcode_profile(
        self,
        user_id: str,
        leetcode_username: str,
        profile_info: Optional[Dict[str, Any]] = None,
        statistics: Optional[Dict[str, Any]] = None,
        contest_info: Optional[Dict[str, Any]] = None,
        topic_stats: Optional[List[Dict[str, Any]]] = None,
        recent_activity: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create or update LeetCode profile document."""
        now = datetime.utcnow()
        existing = await self.find_by_user_id(user_id)

        if existing:
            update_fields: Dict[str, Any] = {
                "leetcode_username": leetcode_username,
                "updated_at": now,
            }
            if profile_info is not None:
                update_fields["profile"] = profile_info
                if profile_info.get("submission_calendar") is not None:
                    update_fields["submission_calendar"] = profile_info.get("submission_calendar")
            if statistics is not None:
                update_fields["statistics"] = statistics
            if contest_info is not None:
                update_fields["contest"] = contest_info
            if topic_stats is not None:
                update_fields["topic_statistics"] = topic_stats
            if recent_activity is not None:
                update_fields["recent_activity"] = recent_activity

            await self.profiles.update_one(
                {"user_id": str(user_id)},
                {"$set": update_fields}
            )
            updated = await self.find_by_user_id(user_id)
            return updated or existing
        else:
            doc = {
                "user_id": str(user_id),
                "leetcode_username": leetcode_username,
                "profile": profile_info or {},
                "statistics": statistics or {},
                "contest": contest_info or {},
                "topic_statistics": topic_stats or [],
                "recent_activity": recent_activity or [],
                "submission_calendar": (profile_info or {}).get("submission_calendar"),
                "analysis": None,
                "sync": {
                    "status": "not_synced",
                    "last_synced_at": None,
                    "last_successful_sync_at": None,
                    "error": None
                },
                "analysis_version": "1.0",
                "created_at": now,
                "updated_at": now
            }
            res = await self.profiles.insert_one(doc)
            doc["_id"] = str(res.inserted_id)
            doc["id"] = str(res.inserted_id)
            return doc

    async def update_sync_status(
        self,
        user_id: str,
        status: str,
        error: Optional[str] = None,
        is_success: bool = False
    ) -> bool:
        """Update sync status and timestamps."""
        now = datetime.utcnow()
        sync_update: Dict[str, Any] = {
            "sync.status": status,
            "sync.last_synced_at": now,
            "sync.error": error,
            "updated_at": now
        }
        if is_success:
            sync_update["sync.last_successful_sync_at"] = now
            sync_update["sync.error"] = None

        res = await self.profiles.update_one(
            {"user_id": str(user_id)},
            {"$set": sync_update}
        )
        return res.modified_count > 0

    async def save_analysis(
        self,
        user_id: str,
        analysis_data: Dict[str, Any],
        version: str = "1.0"
    ) -> bool:
        """Save AI analysis payload to profile document."""
        now = datetime.utcnow()
        res = await self.profiles.update_one(
            {"user_id": str(user_id)},
            {
                "$set": {
                    "analysis": analysis_data,
                    "analysis_version": version,
                    "updated_at": now
                }
            }
        )
        return res.modified_count > 0 or res.matched_count > 0

    async def delete_by_user_id(self, user_id: str) -> bool:
        """Disconnect LeetCode profile by deleting the document."""
        res = await self.profiles.delete_one({"user_id": str(user_id)})
        return res.deleted_count > 0
