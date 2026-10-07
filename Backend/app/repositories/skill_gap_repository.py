import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class SkillGapRepository:
    """Database access layer for Skill Gap Analyses in MongoDB Atlas."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.analyses = db["skill_gap_analyses"]

    async def init_indexes(self) -> None:
        """Create indexes idempotently for user_id and created_at."""
        try:
            await self.analyses.create_index("user_id")
            await self.analyses.create_index([("user_id", 1), ("created_at", -1)])
            logger.info("SkillGapRepository indexes verified.")
        except Exception as e:
            logger.warning("Could not create skill_gap indexes: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        res = dict(doc)
        if "_id" in res:
            res["id"] = str(res["_id"])
            res["_id"] = str(res["_id"])
        return res

    async def create_analysis(self, user_id: str, analysis_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create and persist a new skill gap analysis document."""
        now = datetime.utcnow()
        doc = {
            "user_id": str(user_id),
            "target_role": analysis_dict.get("target_role", "Software Engineer"),
            "overall_coverage": analysis_dict.get("overall_coverage", 0),
            "confidence_index": analysis_dict.get("confidence_index", 95.0),
            "total_audited": analysis_dict.get("total_audited", 0),
            "summary": analysis_dict.get("summary", {}),
            "category_coverage": analysis_dict.get("category_coverage", []),
            "skills": analysis_dict.get("skills", []),
            "priority_gaps": analysis_dict.get("priority_gaps", []),
            "strengths": analysis_dict.get("strengths", []),
            "recommendations": analysis_dict.get("recommendations", []),
            "matrix2x2": analysis_dict.get("matrix2x2", {}),
            "data_quality": analysis_dict.get("data_quality", {}),
            "stale_data": analysis_dict.get("stale_data", []),
            "ai_summary": analysis_dict.get("ai_summary"),
            "analysis_version": analysis_dict.get("analysis_version", "1.0"),
            "created_at": now,
            "updated_at": now
        }
        res = await self.analyses.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
        doc["id"] = str(res.inserted_id)
        return doc

    async def get_latest_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the most recent skill gap analysis document for user."""
        cursor = self.analyses.find({"user_id": str(user_id)}).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        doc = docs[0] if docs else None
        return self._convert_doc(doc)

    async def get_by_id(self, analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find skill gap analysis by ID with optional user ownership check."""
        query: Dict[str, Any] = {}
        try:
            query["_id"] = ObjectId(analysis_id)
        except Exception:
            query["_id"] = analysis_id

        if user_id:
            query["user_id"] = str(user_id)

        doc = await self.analyses.find_one(query)
        return self._convert_doc(doc)

    async def get_history_by_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve historical skill gap snapshots for user."""
        cursor = self.analyses.find({"user_id": str(user_id)}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc(d) for d in docs if d]

    async def delete_by_user_id(self, user_id: str) -> bool:
        """Delete all skill gap records for a user."""
        if hasattr(self.analyses, "delete_many"):
            res = await self.analyses.delete_many({"user_id": str(user_id)})
            return res.deleted_count > 0
        else:
            docs = await self.get_history_by_user(user_id, limit=100)
            deleted = False
            for d in docs:
                res = await self.analyses.delete_one({"_id": d["_id"]})
                if res.deleted_count > 0:
                    deleted = True
            return deleted
