import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.profile import StudentProfileModel

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProfileRepository:
    """Data repository layer for student_profiles collection in MongoDB Atlas."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db["student_profiles"]

    async def ensure_indexes(self) -> None:
        """Create idempotent unique index on user_id in student_profiles collection."""
        try:
            await self.collection.create_index([("user_id", 1)], unique=True)
            logger.info("Unique index on student_profiles.user_id verified.")
        except Exception as e:
            logger.warning("Error creating index on student_profiles.user_id: %s", type(e).__name__)

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve student profile document by user_id."""
        doc = await self.collection.find_one({"user_id": user_id})
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def create_profile(self, user_id: str, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create initial student profile for a given user_id."""
        await self.ensure_indexes()

        existing = await self.get_by_user_id(user_id)
        if existing:
            return existing

        profile_obj = StudentProfileModel(user_id=user_id)
        doc = profile_obj.model_dump(by_alias=True, exclude_none=True)
        if "_id" in doc:
            del doc["_id"]

        if initial_data:
            for k, v in initial_data.items():
                if "." in k:
                    parts = k.split(".")
                    curr = doc
                    for p in parts[:-1]:
                        if p not in curr or not isinstance(curr[p], dict):
                            curr[p] = {}
                        curr = curr[p]
                    curr[parts[-1]] = v
                else:
                    doc[k] = v

        doc["created_at"] = utc_now()
        doc["updated_at"] = utc_now()

        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    async def update_profile(self, user_id: str, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields in student profile for a given user_id."""
        update_dict["updated_at"] = utc_now()
        await self.collection.update_one({"user_id": user_id}, {"$set": update_dict}, upsert=True)
        updated = await self.get_by_user_id(user_id)
        return updated or {}

    async def complete_onboarding(self, user_id: str) -> bool:
        """Mark onboarding as completed for a given user_id."""
        now = utc_now()
        result = await self.collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "onboarding.completed": True,
                    "onboarding.completed_at": now,
                    "onboarding.current_step": 7,
                    "updated_at": now,
                }
            },
        )
        return result.modified_count > 0 or result.matched_count > 0
