import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)


class GitHubRepository:
    """Database access layer for GitHub profiles and repositories in MongoDB Atlas."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.profiles = db["github_profiles"]
        self.repositories = db["github_repositories"]

    async def init_indexes(self) -> None:
        """Create indexes idempotently for performance and uniqueness."""
        try:
            await self.profiles.create_index("user_id", unique=True)
            await self.repositories.create_index([("user_id", 1), ("repo_id", 1)], unique=True)
            await self.repositories.create_index("user_id")
        except Exception as e:
            logger.warning("Could not create GitHub indexes: %s", e)

    def _convert_doc(self, doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not doc:
            return None
        res = dict(doc)
        if "_id" in res:
            res["id"] = str(res["_id"])
            res["_id"] = str(res["_id"])
        return res

    async def find_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve GitHub profile document for authenticated user."""
        doc = await self.profiles.find_one({"user_id": str(user_id)})
        return self._convert_doc(doc)

    async def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find profile by GitHub username."""
        doc = await self.profiles.find_one({"github_username": username.strip()})
        return self._convert_doc(doc)

    async def upsert_github_profile(
        self,
        user_id: str,
        github_username: str,
        profile_info: Optional[Dict[str, Any]] = None,
        statistics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create or update GitHub profile document for user."""
        now = datetime.utcnow()
        existing = await self.find_by_user_id(user_id)

        if existing:
            update_fields: Dict[str, Any] = {
                "github_username": github_username,
                "updated_at": now,
            }
            if profile_info is not None:
                update_fields["profile"] = profile_info
            if statistics is not None:
                update_fields["statistics"] = statistics

            await self.profiles.update_one(
                {"user_id": str(user_id)},
                {"$set": update_fields}
            )
            updated = await self.find_by_user_id(user_id)
            return updated or existing
        else:
            doc = {
                "user_id": str(user_id),
                "github_username": github_username,
                "profile": profile_info or {},
                "statistics": statistics or {},
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
        """Update synchronization status and timestamps."""
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
        """Save AI analysis result to GitHub profile document."""
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

    async def upsert_repositories(
        self,
        user_id: str,
        profile_id: str,
        repos: List[Dict[str, Any]]
    ) -> int:
        """Upsert a list of synchronized repositories for the user."""
        count = 0
        for repo in repos:
            repo_id = repo.get("repo_id") or repo.get("id")
            if not repo_id:
                continue

            repo_doc = {
                "user_id": str(user_id),
                "github_profile_id": str(profile_id),
                "repo_id": repo_id,
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", repo.get("name", "")),
                "description": repo.get("description"),
                "html_url": repo.get("html_url"),
                "language": repo.get("language"),
                "languages": repo.get("languages", {}),
                "stars": repo.get("stars", repo.get("stargazers_count", 0)),
                "forks": repo.get("forks", repo.get("forks_count", 0)),
                "topics": repo.get("topics", []),
                "has_readme": repo.get("has_readme", False),
                "is_fork": repo.get("is_fork", repo.get("fork", False)),
                "size": repo.get("size", 0),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
            }

            await self.repositories.update_one(
                {"user_id": str(user_id), "repo_id": repo_id},
                {"$set": repo_doc},
                upsert=True
            )
            count += 1
        return count

    async def find_repositories_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve paginated list of user's repositories."""
        cursor = self.repositories.find({"user_id": str(user_id)}).sort("stars", -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._convert_doc(d) for d in docs]

    async def count_repositories_by_user_id(self, user_id: str) -> int:
        """Get total count of user's stored repositories."""
        if hasattr(self.repositories, "count_documents"):
            return await self.repositories.count_documents({"user_id": str(user_id)})
        cursor = self.repositories.find({"user_id": str(user_id)})
        docs = await cursor.to_list(length=1000)
        return len(docs)

    async def delete_by_user_id(self, user_id: str) -> bool:
        """Disconnect GitHub: delete profile and repository documents for user."""
        res_prof = await self.profiles.delete_one({"user_id": str(user_id)})
        if hasattr(self.repositories, "delete_many"):
            await self.repositories.delete_many({"user_id": str(user_id)})
        else:
            # Fallback for mock collections if delete_many not present
            repos = await self.find_repositories_by_user_id(user_id, limit=1000)
            for r in repos:
                await self.repositories.delete_one({"_id": r["_id"]})
        return res_prof.deleted_count > 0
