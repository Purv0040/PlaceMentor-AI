import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class ReadinessRepository:
    """Database access layer for Placement Readiness Analyses in MongoDB Atlas."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.analyses = db["readiness_analyses"]

    async def init_indexes(self) -> None:
        """Create indexes idempotently for user_id and created_at."""
        try:
            await self.analyses.create_index("user_id")
            await self.analyses.create_index([("user_id", 1), ("created_at", -1)])
        except Exception as e:
            logger.warning("Could not create readiness indexes: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        res = dict(doc)
        if "_id" in res:
            res["id"] = str(res["_id"])
            res["_id"] = str(res["_id"])
        return res

    async def create_analysis(self, user_id: str, analysis_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new readiness analysis snapshot document."""
        now = datetime.utcnow()
        doc = {
            "user_id": str(user_id),
            "target_role": analysis_dict.get("target_role") or "Unspecified Role",
            "overall_score": analysis_dict.get("overall_score"),
            "overall_confidence": analysis_dict.get("overall_confidence", 0.0),
            "readiness_label": analysis_dict.get("readiness_label", "Insufficient Evidence"),
            "categories": analysis_dict.get("categories", {}),
            "weights_used": analysis_dict.get("weights_used", {}),
            "scored_categories_count": analysis_dict.get("scored_categories_count", 0),
            "insufficient_categories_count": analysis_dict.get("insufficient_categories_count", 0),
            "strengths": analysis_dict.get("strengths", []),
            "key_gaps": analysis_dict.get("key_gaps", []),
            "recommendations": analysis_dict.get("recommendations", []),
            "role_alignment": analysis_dict.get("role_alignment"),
            "data_completeness": analysis_dict.get("data_completeness"),
            "stale_data": analysis_dict.get("stale_data", []),
            "provenance": analysis_dict.get("provenance", {}),
            "calculation_version": analysis_dict.get("calculation_version", "1.0"),
            "created_at": now,
            "updated_at": now
        }
        res = await self.analyses.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
        doc["id"] = str(res.inserted_id)
        return doc

    async def get_latest_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the most recent readiness analysis document for user."""
        cursor = self.analyses.find({"user_id": str(user_id)}).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        doc = docs[0] if docs else None
        return self._convert_doc(doc)

    async def get_by_id(self, analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find readiness analysis by ID with optional user ownership check."""
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
        """Retrieve historical readiness analysis snapshots for user."""
        cursor = self.analyses.find({"user_id": str(user_id)}).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc(d) for d in docs if d]
