import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.onboarding import OnboardingStepUpdate
from app.core.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class OnboardingService:
    """Service layer handling onboarding workflow steps and completion."""

    def __init__(self, profile_repo: ProfileRepository, user_repo: Optional[UserRepository] = None) -> None:
        self.profile_repo = profile_repo
        self.user_repo = user_repo

    async def get_onboarding_state(self, user_id: str) -> Dict[str, Any]:
        """Fetch current onboarding state and step data for user."""
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            profile = await self.profile_repo.create_profile(user_id)

        if "_id" in profile and not isinstance(profile["_id"], str):
            profile["_id"] = str(profile["_id"])
        return profile

    async def save_step_data(self, user_id: str, step_update: OnboardingStepUpdate) -> Dict[str, Any]:
        """Save onboarding step data and update step progression."""
        profile = await self.get_onboarding_state(user_id)

        step_num = step_update.step_number
        update_fields: Dict[str, Any] = {}

        if step_update.profile is not None:
            for k, v in step_update.profile.model_dump(exclude_none=True).items():
                update_fields[f"personal.{k}"] = v

        if step_update.career is not None:
            for k, v in step_update.career.model_dump(exclude_none=True).items():
                update_fields[f"career.{k}"] = v

        if step_update.skills is not None:
            for k, v in step_update.skills.model_dump(exclude_none=True).items():
                update_fields[f"skills.{k}"] = v

        if step_update.integrations is not None:
            for k, v in step_update.integrations.model_dump(exclude_none=True).items():
                update_fields[f"integrations.{k}"] = v

        if step_update.preferences is not None:
            for k, v in step_update.preferences.model_dump(exclude_none=True).items():
                update_fields[f"preferences.{k}"] = v

        if step_update.goals is not None:
            for k, v in step_update.goals.model_dump(exclude_none=True).items():
                update_fields[f"goals.{k}"] = v

        # Update step tracking
        completed_steps = set(profile.get("onboarding", {}).get("completed_steps", [1]))
        completed_steps.add(step_num)
        
        next_step = max(step_num, profile.get("onboarding", {}).get("current_step", 1))
        
        update_fields["onboarding.current_step"] = next_step
        update_fields["onboarding.completed_steps"] = sorted(list(completed_steps))

        updated_profile = await self.profile_repo.update_profile(user_id, update_fields)
        return updated_profile

    async def complete_onboarding(self, user_id: str, user_repo: Optional[UserRepository] = None) -> Dict[str, Any]:
        """Validate and finalize student onboarding."""
        profile = await self.get_onboarding_state(user_id)

        # Basic validation: ensure required personal and career fields are filled
        personal = profile.get("personal", {})
        career = profile.get("career", {})

        if not personal.get("name") or not personal.get("college") or not personal.get("degree"):
            raise BadRequestException("Cannot complete onboarding: missing required personal information.")

        if not career.get("targetRole"):
            raise BadRequestException("Cannot complete onboarding: missing target career role.")

        # Mark profile onboarding completed
        await self.profile_repo.complete_onboarding(user_id)

        # Mark user collection is_onboarded = True if user_repo provided
        repo = user_repo or self.user_repo
        if repo:
            await repo.update(user_id, {"is_onboarded": True, "onboarding_completed": True})

        # Evaluate and unlock onboarding achievements
        try:
            from app.services.achievement_service import AchievementService
            await AchievementService(self.profile_repo.db).evaluate_and_unlock(user_id)
        except Exception as e:
            logger.warning("Error evaluating achievements after onboarding completion: %s", e)

        return {
            "user_id": user_id,
            "onboarding_completed": True,
            "completed_at": datetime.utcnow(),
            "message": "Onboarding completed successfully!",
        }
