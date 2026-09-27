import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class ProjectRepository:
    """Database access layer for Projects in MongoDB Atlas."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.projects = db["projects"]

    async def init_indexes(self) -> None:
        """Create indexes idempotently for user_id, status, and is_featured."""
        try:
            await self.projects.create_index("user_id")
            await self.projects.create_index([("user_id", 1), ("status", 1)])
            await self.projects.create_index([("user_id", 1), ("is_featured", 1)])
            await self.projects.create_index([("user_id", 1), ("created_at", -1)])
        except Exception as e:
            logger.warning("Could not create project indexes: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        res = dict(doc)
        if "_id" in res:
            res["id"] = str(res["_id"])
            res["_id"] = str(res["_id"])
        return res

    async def create_project(self, user_id: str, project_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project document."""
        now = datetime.utcnow()
        doc = {
            "user_id": str(user_id),
            "title": project_dict.get("title", ""),
            "description": project_dict.get("description", ""),
            "category": project_dict.get("category", "Full Stack / AI"),
            "role": project_dict.get("role"),
            "duration": project_dict.get("duration") or {"start_date": None, "end_date": None},
            "technologies": project_dict.get("technologies", []),
            "features": project_dict.get("features", []),
            "achievements": project_dict.get("achievements", []),
            "architectureTags": project_dict.get("architectureTags", []),
            "links": project_dict.get("links") or {"github": None, "live": None, "demo": None},
            "githubUrl": project_dict.get("githubUrl"),
            "liveUrl": project_dict.get("liveUrl"),
            "github": project_dict.get("github") or {"repository_id": None, "repository_url": None, "connected": False},
            "status": project_dict.get("status", "active"),
            "is_featured": project_dict.get("is_featured", False),
            "score": project_dict.get("score", 85),
            "scoreBadge": project_dict.get("scoreBadge", "Production Grade"),
            "complexityScore": project_dict.get("complexityScore", 85),
            "evidenceBullets": project_dict.get("evidenceBullets", []),
            "analysis": project_dict.get("analysis"),
            "analysis_status": project_dict.get("analysis_status", "not_analyzed"),
            "analysis_version": project_dict.get("analysis_version", "1.0"),
            "created_at": now,
            "updated_at": now
        }
        res = await self.projects.insert_one(doc)
        doc["_id"] = str(res.inserted_id)
        doc["id"] = str(res.inserted_id)
        return doc

    async def find_by_user_id(self, user_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        """List all projects belonging to user."""
        query: Dict[str, Any] = {"user_id": str(user_id)}
        if not include_archived:
            query["status"] = "active"

        cursor = self.projects.find(query).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [self._convert_doc(d) for d in docs if d]

    async def find_by_id(self, project_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find single project by ID and optional user ownership check."""
        query: Dict[str, Any] = {}
        try:
            query["_id"] = ObjectId(project_id)
        except Exception:
            query["_id"] = project_id

        if user_id:
            query["user_id"] = str(user_id)

        doc = await self.projects.find_one(query)
        return self._convert_doc(doc)

    async def update_project(self, project_id: str, user_id: str, update_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing project fields."""
        query: Dict[str, Any] = {"user_id": str(user_id)}
        try:
            query["_id"] = ObjectId(project_id)
        except Exception:
            query["_id"] = project_id

        update_dict["updated_at"] = datetime.utcnow()
        clean_update = {k: v for k, v in update_dict.items() if k not in ["_id", "id", "user_id", "created_at"]}

        await self.projects.update_one(query, {"$set": clean_update})
        return await self.find_by_id(project_id, user_id)

    async def delete_project(self, project_id: str, user_id: str, soft_delete: bool = True) -> bool:
        """Soft delete (set status='archived') or permanently delete project."""
        query: Dict[str, Any] = {"user_id": str(user_id)}
        try:
            query["_id"] = ObjectId(project_id)
        except Exception:
            query["_id"] = project_id

        if soft_delete:
            res = await self.projects.update_one(query, {"$set": {"status": "archived", "updated_at": datetime.utcnow()}})
            return res.modified_count > 0
        else:
            res = await self.projects.delete_one(query)
            return res.deleted_count > 0

    async def save_analysis(
        self,
        project_id: str,
        user_id: str,
        analysis_data: Dict[str, Any],
        version: str = "1.0"
    ) -> bool:
        """Save AI analysis report to project document."""
        query: Dict[str, Any] = {"user_id": str(user_id)}
        try:
            query["_id"] = ObjectId(project_id)
        except Exception:
            query["_id"] = project_id

        now = datetime.utcnow()
        update_fields: Dict[str, Any] = {
            "analysis": analysis_data,
            "analysis_status": "completed",
            "analysis_version": version,
            "updated_at": now
        }

        # If AI analysis extracted evidence bullets or complexity score, update root fields gracefully
        if "evidence_bullets" in analysis_data and isinstance(analysis_data["evidence_bullets"], list):
            update_fields["evidenceBullets"] = analysis_data["evidence_bullets"]
        if "score" in analysis_data and isinstance(analysis_data["score"], (int, float)):
            update_fields["score"] = int(analysis_data["score"])
            update_fields["complexityScore"] = int(analysis_data["score"])

        res = await self.projects.update_one(query, {"$set": update_fields})
        return res.modified_count > 0 or res.matched_count > 0

    async def update_analysis_status(self, project_id: str, user_id: str, status: str) -> bool:
        """Update analysis status (e.g. stale, analyzing, failed)."""
        query: Dict[str, Any] = {"user_id": str(user_id)}
        try:
            query["_id"] = ObjectId(project_id)
        except Exception:
            query["_id"] = project_id

        res = await self.projects.update_one(
            query,
            {"$set": {"analysis_status": status, "updated_at": datetime.utcnow()}}
        )
        return res.modified_count > 0

    async def toggle_featured(self, project_id: str, user_id: str, is_featured: bool) -> Optional[Dict[str, Any]]:
        """Set project featured state."""
        return await self.update_project(project_id, user_id, {"is_featured": is_featured})
