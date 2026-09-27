import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.github_repository import GitHubRepository
from app.integrations.github_client import (
    GitHubAPIClient,
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
)
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


class GitHubService:
    """Service layer orchestrating GitHub profile connection, synchronization, and AI intelligence."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        github_client: Optional[GitHubAPIClient] = None,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = GitHubRepository(db)
        self.github_client = github_client or GitHubAPIClient()
        self.ai_client = ai_client or AIClient()

    async def connect_github(self, user_id: str, username: str) -> Dict[str, Any]:
        """Validate GitHub profile username with API and save connection for authenticated user."""
        clean_user = username.strip().lstrip("@")
        if not clean_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub username cannot be empty."
            )

        # Validate with GitHub API
        try:
            profile_info = await self.github_client.get_user_profile(clean_user)
        except GitHubUserNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GitHub user '{clean_user}' not found on GitHub."
            )
        except GitHubRateLimitError:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="GitHub API rate limit hit. Please try again later."
            )
        except GitHubAPIError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub API error: {str(e)}"
            )

        # Upsert profile in DB
        created_or_updated = await self.repo.upsert_github_profile(
            user_id=user_id,
            github_username=profile_info["login"],
            profile_info=profile_info
        )
        logger.info("User %s successfully connected GitHub account '%s'", user_id, profile_info["login"])
        return created_or_updated

    async def get_github_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieve GitHub profile for user."""
        profile = await self.repo.find_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub profile not connected for this user."
            )
        return profile

    async def sync_github(self, user_id: str) -> Dict[str, Any]:
        """Synchronize GitHub profile and repositories from GitHub API."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No GitHub account connected. Please connect your GitHub account first."
            )

        username = existing["github_username"]
        await self.repo.update_sync_status(user_id, "syncing")

        try:
            # 1. Fetch fresh profile
            profile_info = await self.github_client.get_user_profile(username)

            # 2. Fetch public repositories
            repos = await self.github_client.get_user_repos(username, page=1, per_page=100)

            # 3. Calculate deterministic statistics
            lang_counts: Dict[str, int] = {}
            total_stars = 0
            total_forks = 0
            forked_repos = 0
            non_fork_repos = 0
            with_readme = 0

            for r in repos:
                is_fork = r.get("is_fork", False)
                if is_fork:
                    forked_repos += 1
                else:
                    non_fork_repos += 1

                total_stars += r.get("stars", 0)
                total_forks += r.get("forks", 0)

                if r.get("has_readme"):
                    with_readme += 1

                lang = r.get("language")
                if lang and not is_fork:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

            primary_lang = max(lang_counts, key=lang_counts.__getitem__) if lang_counts else None

            stats = {
                "total_repositories": len(repos),
                "public_repositories": profile_info.get("public_repos", len(repos)),
                "forked_repositories": forked_repos,
                "non_fork_repositories": non_fork_repos,
                "total_stars": total_stars,
                "total_forks": total_forks,
                "repos_with_readme": with_readme,
                "primary_language": primary_lang,
                "languages": lang_counts
            }

            # 4. Save repositories in DB
            profile_id = str(existing["id"])
            await self.repo.upsert_repositories(user_id, profile_id, repos)

            # 5. Save updated profile with stats & set sync status
            updated_profile = await self.repo.upsert_github_profile(
                user_id=user_id,
                github_username=profile_info["login"],
                profile_info=profile_info,
                statistics=stats
            )
            await self.repo.update_sync_status(user_id, "synced", is_success=True)

            logger.info("Successfully synchronized GitHub data for user %s (%d repos)", user_id, len(repos))
            return await self.get_github_profile(user_id)

        except (GitHubUserNotFoundError, GitHubRateLimitError, GitHubAPIError) as e:
            error_msg = str(e)
            logger.error("Failed to sync GitHub profile for user %s: %s", user_id, error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"GitHub sync failed: {error_msg}"
            )
        except Exception as e:
            error_msg = f"Unexpected sync failure: {str(e)}"
            logger.error(error_msg)
            await self.repo.update_sync_status(user_id, "failed", error=error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

    async def get_github_repositories(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetch paginated list of user's synchronized GitHub repositories."""
        skip = (page - 1) * limit
        repos = await self.repo.find_repositories_by_user_id(user_id, skip=skip, limit=limit)
        total = await self.repo.count_repositories_by_user_id(user_id)
        return repos, total

    async def analyze_github(self, user_id: str) -> Dict[str, Any]:
        """Trigger AI analysis for the user's connected GitHub profile."""
        profile = await self.get_github_profile(user_id)
        username = profile["github_username"]

        sync_status = profile.get("sync", {}).get("status")
        if sync_status not in ["synced", "completed"]:
            # Auto-trigger sync if not synced yet
            try:
                profile = await self.sync_github(user_id)
            except Exception as e:
                logger.warning("Auto-sync prior to analysis failed: %s", e)

        try:
            analysis_result = await self.ai_client.analyze_github(username)
        except AIClientError as e:
            logger.error("AI GitHub analysis failed for user %s: %s", user_id, e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI GitHub analysis failed: {str(e)}"
            )

        saved = await self.repo.save_analysis(user_id, analysis_result, version="1.0")
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save GitHub analysis result."
            )

        return await self.get_github_profile(user_id)

    async def get_github_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get stored GitHub AI analysis result."""
        profile = await self.get_github_profile(user_id)
        analysis = profile.get("analysis")
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub AI analysis has not been generated yet. Please trigger analysis first."
            )
        return {
            "user_id": user_id,
            "github_username": profile["github_username"],
            "analysis_version": profile.get("analysis_version", "1.0"),
            "analyzed_at": profile.get("updated_at"),
            "analysis": analysis
        }

    async def disconnect_github(self, user_id: str) -> bool:
        """Disconnect and delete GitHub profile and repo data for user."""
        existing = await self.repo.find_by_user_id(user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No GitHub account connected."
            )
        deleted = await self.repo.delete_by_user_id(user_id)
        logger.info("Disconnected GitHub profile for user %s", user_id)
        return deleted
