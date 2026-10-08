from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class AdaptiveRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["adaptation_events"]

    @staticmethod
    def _serialize_document(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        if not doc.get("id"):
            doc["id"] = str(doc.get("_id"))

        # Repair legacy/corrupted '500 pending tasks' record state to superseded
        if "500 pending tasks" in str(doc.get("reason", "")):
            doc["lifecycle_status"] = "superseded"
            doc["is_actionable"] = False
            doc["applied"] = False
            doc["applied_at"] = None

        if doc.get("lifecycle_status") == "superseded":
            doc["is_actionable"] = False
            doc["applied"] = False
            doc["applied_at"] = None
        elif doc.get("applied") is True and doc.get("applied_at") is not None:
            doc["lifecycle_status"] = "applied"
            doc["is_actionable"] = False
        elif doc.get("trigger") in ("routine_check", "on_track") and not doc.get("changes"):
            doc.setdefault("lifecycle_status", "informational")
            doc["is_actionable"] = False
        else:
            doc.setdefault("lifecycle_status", "pending")
            doc.setdefault("is_actionable", bool(doc.get("changes") or doc.get("trigger") in ("overdue_tasks", "repeated_skipped_tasks")))
        return doc

    @classmethod
    def _serialize_documents(cls, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            cls._serialize_document(doc)
            for doc in docs
            if doc is not None
        ]

    async def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data = dict(data)
        data["created_at"] = data.get("created_at", now)
        data.setdefault("lifecycle_status", "pending")
        data.setdefault("is_actionable", False)
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        data["id"] = str(data.get("id") or data["_id"])
        await self.collection.update_one({"_id": result.inserted_id}, {"$set": {"id": data["id"]}})
        return data

    async def get_by_id(self, event_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        or_conditions: List[Dict[str, Any]] = [{"_id": str(event_id)}, {"id": str(event_id)}]
        if ObjectId.is_valid(event_id):
            or_conditions.append({"_id": ObjectId(event_id)})
        query: Dict[str, Any] = {"user_id": str(user_id), "$or": or_conditions}
        doc = await self.collection.find_one(query)
        if doc and "500 pending tasks" in str(doc.get("reason", "")):
            now_utc = datetime.now(timezone.utc)
            await self.collection.update_one(
                query,
                {"$set": {"lifecycle_status": "superseded", "is_actionable": False, "applied": False, "applied_at": None, "superseded_at": now_utc}}
            )
            doc["lifecycle_status"] = "superseded"
            doc["is_actionable"] = False
            doc["applied"] = False
            doc["applied_at"] = None
        return self._serialize_document(doc)


    async def get_by_user_id(
        self, user_id: str, roadmap_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": str(user_id)}
        if roadmap_id:
            if ObjectId.is_valid(roadmap_id):
                query["$or"] = [{"roadmap_id": str(roadmap_id)}, {"roadmap_id": ObjectId(roadmap_id)}]
            else:
                query["roadmap_id"] = str(roadmap_id)
        cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        return self._serialize_documents(docs)

    async def get_latest_by_user_id(
        self, user_id: str, roadmap_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": str(user_id)}
        if roadmap_id:
            if ObjectId.is_valid(roadmap_id):
                query["$or"] = [{"roadmap_id": str(roadmap_id)}, {"roadmap_id": ObjectId(roadmap_id)}]
            else:
                query["roadmap_id"] = str(roadmap_id)
        cursor = self.collection.find(query).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return self._serialize_document(docs[0]) if docs else None

    async def get_latest_unapplied_by_user_id(
        self, user_id: str, roadmap_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {
            "user_id": str(user_id),
            "applied": False,
            "lifecycle_status": {"$nin": ["superseded", "applied"]},
        }
        if roadmap_id:
            if ObjectId.is_valid(roadmap_id):
                query["$or"] = [{"roadmap_id": str(roadmap_id)}, {"roadmap_id": ObjectId(roadmap_id)}]
            else:
                query["roadmap_id"] = str(roadmap_id)
        cursor = self.collection.find(query).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return self._serialize_document(docs[0]) if docs else None

    async def mark_superseded_unapplied(
        self, user_id: str, roadmap_id: str, exclude_event_id: Optional[str] = None
    ) -> int:
        query: Dict[str, Any] = {
            "user_id": str(user_id),
            "applied": False,
        }
        if ObjectId.is_valid(roadmap_id):
            query["$or"] = [{"roadmap_id": str(roadmap_id)}, {"roadmap_id": ObjectId(roadmap_id)}]
        else:
            query["roadmap_id"] = str(roadmap_id)

        if exclude_event_id:
            query["id"] = {"$ne": str(exclude_event_id)}
            query["_id"] = {"$ne": str(exclude_event_id)}

        now_utc = datetime.now(timezone.utc)
        result = await self.collection.update_many(
            query,
            {"$set": {"lifecycle_status": "superseded", "is_actionable": False, "superseded_at": now_utc}},
        )
        return getattr(result, "modified_count", 0)

    async def mark_applied(self, event_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        or_conditions: List[Dict[str, Any]] = [{"_id": str(event_id)}, {"id": str(event_id)}]
        if ObjectId.is_valid(event_id):
            or_conditions.append({"_id": ObjectId(event_id)})
        query: Dict[str, Any] = {"user_id": str(user_id), "$or": or_conditions}
        now_utc = datetime.now(timezone.utc)
        await self.collection.update_one(
            query,
            {"$set": {"applied": True, "lifecycle_status": "applied", "is_actionable": False, "applied_at": now_utc}},
        )
        doc = await self.collection.find_one(query)
        return self._serialize_document(doc)



