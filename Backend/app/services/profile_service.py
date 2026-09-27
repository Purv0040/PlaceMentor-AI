import logging
from typing import Dict, Any, Optional
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileUpdate
from app.core.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ProfileService:
    """Service layer handling business logic for Student Profile operations."""

    def __init__(self, profile_repo: ProfileRepository) -> None:
        self.profile_repo = profile_repo

    async def get_or_create_profile(self, user_id: str, user_email: Optional[str] = None, user_name: Optional[str] = None) -> Dict[str, Any]:
        """Fetch student profile by user_id or auto-initialize one if missing."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            initial_data = {}
            if user_name:
                initial_data["personal.name"] = user_name
            if user_email:
                initial_data["personal.email"] = user_email
            profile = await self.profile_repo.create_profile(user_id, initial_data=initial_data)
        
        if "_id" in profile and not isinstance(profile["_id"], str):
            profile["_id"] = str(profile["_id"])
        return profile

    async def update_profile(self, user_id: str, profile_update: ProfileUpdate) -> Dict[str, Any]:
        """Update student profile sections."""
        existing = await self.get_or_create_profile(user_id)
        if not existing:
            raise NotFoundException("Student profile not found.")

        update_fields: Dict[str, Any] = {}

        if profile_update.personal is not None:
            for k, v in profile_update.personal.model_dump(exclude_none=True).items():
                update_fields[f"personal.{k}"] = v

        if profile_update.career is not None:
            for k, v in profile_update.career.model_dump(exclude_none=True).items():
                update_fields[f"career.{k}"] = v

        if profile_update.skills is not None:
            for k, v in profile_update.skills.model_dump(exclude_none=True).items():
                update_fields[f"skills.{k}"] = v

        if profile_update.integrations is not None:
            for k, v in profile_update.integrations.model_dump(exclude_none=True).items():
                update_fields[f"integrations.{k}"] = v

        if profile_update.preferences is not None:
            for k, v in profile_update.preferences.model_dump(exclude_none=True).items():
                update_fields[f"preferences.{k}"] = v

        if profile_update.goals is not None:
            for k, v in profile_update.goals.model_dump(exclude_none=True).items():
                update_fields[f"goals.{k}"] = v

        if not update_fields:
            return existing

        updated_profile = await self.profile_repo.update_profile(user_id, update_fields)
        return updated_profile
