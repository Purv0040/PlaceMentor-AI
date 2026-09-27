import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class ResumeRepository:
    """Repository handling raw MongoDB queries for the resumes collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db["resumes"]

    async def ensure_indexes(self) -> None:
        """Create indexes for performance and queries."""
        try:
            await self.collection.create_index("user_id")
            await self.collection.create_index([("user_id", 1), ("is_active", 1)])
            await self.collection.create_index([("user_id", 1), ("uploaded_at", -1)])
            logger.info("ResumeRepository indexes created/verified.")
        except Exception as e:
            logger.warning("Error creating indexes in ResumeRepository: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Convert MongoDB ObjectId _id to string in document dict."""
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
            doc["_id"] = str(doc["_id"])
        return doc

    async def create_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert new resume document."""
        if "_id" in resume_data and resume_data["_id"] is None:
            del resume_data["_id"]
        
        resume_data["uploaded_at"] = resume_data.get("uploaded_at", datetime.utcnow())
        resume_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(resume_data)
        resume_data["_id"] = str(result.inserted_id)
        resume_data["id"] = str(result.inserted_id)
        return resume_data

    async def find_by_id(self, resume_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Find a resume by ID belonging to user_id."""
        query: Dict[str, Any] = {"user_id": str(user_id)}
        if ObjectId.is_valid(resume_id):
            query["$or"] = [{"_id": ObjectId(resume_id)}, {"_id": resume_id}]
        else:
            query["_id"] = resume_id
            
        doc = await self.collection.find_one(query)
        return self._convert_doc(doc)

    async def find_all_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find all resumes owned by user_id sorted newest first."""
        cursor = self.collection.find({"user_id": str(user_id)}).sort("uploaded_at", -1)
        docs = await cursor.to_list(length=100)
        return [self._convert_doc(d) for d in docs if d]

    async def find_active_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find the active resume for user_id."""
        doc = await self.collection.find_one({"user_id": str(user_id), "is_active": True})
        return self._convert_doc(doc)

    async def set_active(self, resume_id: str, user_id: str) -> bool:
        """Deactivate all resumes for user_id and set specified resume active."""
        # 1. Deactivate all for user
        await self.collection.update_many(
            {"user_id": str(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        # 2. Activate requested resume
        search_id = ObjectId(resume_id) if ObjectId.is_valid(resume_id) else resume_id
        result = await self.collection.update_one(
            {"$or": [{"_id": search_id}, {"_id": resume_id}], "user_id": str(user_id)},
            {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def update_status(self, resume_id: str, user_id: str, status: str, error_message: Optional[str] = None) -> bool:
        """Update status and optional error message."""
        search_id = ObjectId(resume_id) if ObjectId.is_valid(resume_id) else resume_id
        update_fields: Dict[str, Any] = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if error_message is not None:
            update_fields["error_message"] = error_message

        result = await self.collection.update_one(
            {"$or": [{"_id": search_id}, {"_id": resume_id}], "user_id": str(user_id)},
            {"$set": update_fields}
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def save_analysis(self, resume_id: str, user_id: str, analysis_data: Dict[str, Any], version: str = "1.0") -> bool:
        """Save AI analysis result into resume document and mark completed."""
        search_id = ObjectId(resume_id) if ObjectId.is_valid(resume_id) else resume_id
        now = datetime.utcnow()
        result = await self.collection.update_one(
            {"$or": [{"_id": search_id}, {"_id": resume_id}], "user_id": str(user_id)},
            {"$set": {
                "analysis": analysis_data,
                "analysis_version": version,
                "status": "completed",
                "analyzed_at": now,
                "updated_at": now,
                "error_message": None
            }}
        )
        return result.modified_count > 0 or result.matched_count > 0

    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Delete a resume document by ID belonging to user_id."""
        search_id = ObjectId(resume_id) if ObjectId.is_valid(resume_id) else resume_id
        result = await self.collection.delete_one({"$or": [{"_id": search_id}, {"_id": resume_id}], "user_id": str(user_id)})
        return result.deleted_count > 0
