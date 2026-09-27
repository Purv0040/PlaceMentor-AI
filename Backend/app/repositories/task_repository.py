from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class TaskRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db["daily_tasks"]

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        data["created_at"] = data.get("created_at", now)
        data["updated_at"] = now
        result = await self.collection.insert_one(data)
        data["_id"] = str(result.inserted_id)
        if "task_id" not in data or not data["task_id"]:
            data["task_id"] = data["_id"]
            await self.collection.update_one({"_id": result.inserted_id}, {"$set": {"task_id": data["_id"]}})
        data["id"] = str(data.get("id") or data["task_id"])
        return data

    async def create_many(self, tasks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not tasks_data:
            return []
        now = datetime.now(timezone.utc)
        for t in tasks_data:
            t["created_at"] = t.get("created_at", now)
            t["updated_at"] = now
        results = await self.collection.insert_many(tasks_data)
        inserted_list = []
        for idx, doc_id in enumerate(results.inserted_ids):
            t = tasks_data[idx]
            t["_id"] = str(doc_id)
            if "task_id" not in t or not t["task_id"]:
                t["task_id"] = t["_id"]
                await self.collection.update_one({"_id": doc_id}, {"$set": {"task_id": t["_id"]}})
            t["id"] = str(t.get("id") or t["task_id"])
            inserted_list.append(t)
        return inserted_list

    async def get_by_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id, "task_id": task_id}
        if ObjectId.is_valid(task_id):
            query = {"user_id": user_id, "$or": [{"_id": ObjectId(task_id)}, {"task_id": task_id}]}
        doc = await self.collection.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
            if "task_id" not in doc or not doc["task_id"]:
                doc["task_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["task_id"])
        return doc

    async def get_by_user_and_date(self, user_id: str, date_str: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id, "date": date_str})
        docs = await cursor.to_list(length=200)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "task_id" not in doc or not doc["task_id"]:
                doc["task_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["task_id"])
        return docs

    async def get_by_roadmap_id(self, roadmap_id: str, user_id: str) -> List[Dict[str, Any]]:
        cursor = self.collection.find({"user_id": user_id, "roadmap_id": roadmap_id})
        docs = await cursor.to_list(length=1000)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "task_id" not in doc or not doc["task_id"]:
                doc["task_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["task_id"])
        return docs

    async def get_all_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if status:
            query["status"] = status
        if category:
            query["category"] = category
        cursor = self.collection.find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            if "task_id" not in doc or not doc["task_id"]:
                doc["task_id"] = doc["_id"]
            doc["id"] = str(doc.get("id") or doc["task_id"])
        return docs

    async def update(self, task_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        data["updated_at"] = now
        query: Dict[str, Any] = {"user_id": user_id, "task_id": task_id}
        if ObjectId.is_valid(task_id):
            query = {"user_id": user_id, "$or": [{"_id": ObjectId(task_id)}, {"task_id": task_id}]}

        await self.collection.update_one(query, {"$set": data})
        return await self.get_by_id(task_id, user_id)

    async def update_status(
        self,
        task_id: str,
        user_id: str,
        status: str,
        actual_minutes: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        update_data: Dict[str, Any] = {
            "status": status,
            "updated_at": now,
        }
        if status == "completed":
            update_data["completed_at"] = now
            update_data["completion_percentage"] = 100.0
        elif status == "in_progress":
            update_data["completion_percentage"] = 50.0
        elif status == "pending":
            update_data["completion_percentage"] = 0.0

        if actual_minutes is not None:
            update_data["actual_minutes"] = actual_minutes
        if notes is not None:
            update_data["notes"] = notes

        query: Dict[str, Any] = {"user_id": user_id, "task_id": task_id}
        if ObjectId.is_valid(task_id):
            query = {"user_id": user_id, "$or": [{"_id": ObjectId(task_id)}, {"task_id": task_id}]}

        await self.collection.update_one(query, {"$set": update_data})
        return await self.get_by_id(task_id, user_id)

    async def delete(self, task_id: str, user_id: str) -> bool:
        query: Dict[str, Any] = {"user_id": user_id, "task_id": task_id}
        if ObjectId.is_valid(task_id):
            query = {"user_id": user_id, "$or": [{"_id": ObjectId(task_id)}, {"task_id": task_id}]}
        res = await self.collection.delete_one(query)
        return res.deleted_count > 0
