import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.leetcode_repository import LeetCodeRepository
from app.integrations.leetcode_client import (
    LeetCodeAPIClient,
    LeetCodeUserNotFoundError,
    LeetCodeAPIError,
)
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class LeetCodeService:
    """Service layer orchestrating LeetCode profile connection, synchronization, and AI analysis."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        leetcode_client: Optional[LeetCodeAPIClient] = None,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = LeetCodeRepository(db)
        self.leetcode_client = leetcode_client or LeetCodeAPIClient()
        self.ai_client = ai_client or AIClient()

    async def connect_leetcode(self, user_id: str, username: str) -> Dict[str, Any]:
        """Validate LeetCode profile username with GraphQL provider and save connection."""
        clean_user = username.strip().lstrip("@")
        if not clean_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LeetCode username cannot be empty."
            )

        # Validate username with LeetCode GraphQL provider
        try:
            profile_info = await self.leetcode_client.get_user_profile(clean_user)
        except LeetCodeUserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"LeetCode user '{clean_user}' not found on LeetCode."
            )
        except LeetCodeAPIError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LeetCode data provider error: {str(e)}"
            )

        # Upsert profile in DB
        created_or_updated = await self.repo.upsert_leetcode_profile(
            user_id=user_id,
            leetcode_username=profile_info["username"],
            profile_info=profile_info
        )
        logger.info("User %s successfully connected LeetCode account '%s'", user_id, profile_info["username"])
        return created_or_updated

    async def get_leetcode_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve LeetCode profile for user."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode profile not connected for this user."
            )
        return profile

    async def sync_leetcode(self, user_id: str) -> Dict[str, Any]:
        """Synchronize LeetCode profile, problem statistics, topics, and contest rating."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No LeetCode account connected. Please connect your LeetCode account first."
            )

        username = existing["leetcode_username"]
        await self.repo.update_sync_status(user_id, "syncing")

        try:
            # 1. Fetch fresh profile info
            profile_info = await self.leetcode_client.get_user_profile(username)

            # 2. Fetch solved problem statistics
            solved_stats = await self.leetcode_client.get_solved_problems(username)

            # 3. Fetch topic statistics & contest ranking (graceful fallback if unavailable)
            topic_stats = await self.leetcode_client.get_topic_tags(username)
            contest_info = await self.leetcode_client.get_contest_info(username)
            recent_subs = await self.leetcode_client.get_recent_submissions(username)

            # 4. Update profile in database
            updated = await self.repo.upsert_leetcode_profile(
                user_id=user_id,
                leetcode_username=profile_info["username"],
                profile_info=profile_info,
                statistics=solved_stats,
                contest_info=contest_info or {},
                topic_stats=topic_stats,
                recent_activity=recent_subs
            )
            await self.repo.update_sync_status(user_id, "synced", is_success=True)

            logger.info("Successfully synchronized LeetCode data for user %s (%d solved)", user_id, solved_stats.get("total_solved", 0))
            return await self.get_leetcode_profile(user_id)

        except (LeetCodeUserNotFoundError, LeetCodeAPIError) as e:
            error_msg = str(e)
            logger.error("Failed to sync LeetCode profile for user %s: %s", user_id, error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"LeetCode sync failed: {error_msg}"
            )
        except Exception as e:
            error_msg = f"Unexpected sync failure: {str(e)}"
            logger.error(error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

    async def get_leetcode_statistics(self, user_id: str) -> Dict[str, Any]:
        """Fetch problem-solving statistics and contest ranking."""
        profile = await self.get_leetcode_profile(user_id)
        return {
            "user_id": user_id,
            "leetcode_username": profile["leetcode_username"],
            "statistics": profile.get("statistics", {}),
            "contest": profile.get("contest", {}),
            "topic_statistics": profile.get("topic_statistics", [])
        }

    async def get_leetcode_activity(self, user_id: str) -> Dict[str, Any]:
        """Fetch recent submission activity."""
        profile = await self.get_leetcode_profile(user_id)
        return {
            "user_id": user_id,
            "leetcode_username": profile["leetcode_username"],
            "recent_activity": profile.get("recent_activity", [])
        }

    async def analyze_leetcode(self, user_id: str) -> Dict[str, Any]:
        """Trigger AI LeetCode Analyzer microservice for the connected profile."""
        profile = await self.get_leetcode_profile(user_id)
        username = profile["leetcode_username"]

        sync_status = profile.get("sync", {}).get("status")
        if sync_status not in ["synced", "completed"]:
            try:
                profile = await self.sync_leetcode(user_id)
            except Exception as e:
                logger.warning("Auto-sync prior to LeetCode analysis failed: %s", e)

        try:
            analysis_result = await self.ai_client.analyze_leetcode(username)
        except AIClientError as e:
            logger.error("AI LeetCode analysis failed for user %s: %s", user_id, e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI LeetCode analysis failed: {str(e)}"
            )

        saved = await self.repo.save_analysis(user_id, analysis_result, version="1.0")
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save LeetCode analysis result."
            )

        return await self.get_leetcode_profile(user_id)

    async def get_leetcode_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get stored LeetCode AI analysis payload."""
        profile = await self.get_leetcode_profile(user_id)
        analysis = profile.get("analysis")
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LeetCode AI analysis has not been generated yet. Please trigger analysis first."
            )
        return {
            "user_id": user_id,
            "leetcode_username": profile["leetcode_username"],
            "analysis_version": profile.get("analysis_version", "1.0"),
            "analyzed_at": profile.get("updated_at"),
            "analysis": analysis
        }

    async def disconnect_leetcode(self, user_id: str) -> bool:
        """Disconnect and delete LeetCode profile for authenticated user."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No LeetCode account connected."
            )
        deleted = await self.repo.delete_by_user_id(user_id)
        logger.info("Disconnected LeetCode profile for user %s", user_id)
        return deleted
