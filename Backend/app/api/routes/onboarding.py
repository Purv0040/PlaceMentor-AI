from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.services.onboarding_service import OnboardingService
from app.schemas.onboarding import OnboardingStepUpdate, OnboardingStateResponse, OnboardingCompleteResponse
from app.schemas.profile import ProfileUpdate

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
async def get_onboarding_state(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve current onboarding state and saved progress for the authenticated student."""
    user_id = current_user["id"]
    service = OnboardingService(ProfileRepository(db), UserRepository(db))
    profile = await service.get_onboarding_state(user_id)
    return {
        "success": True,
        "data": profile,
        "message": "Onboarding state retrieved.",
    }


@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def initialize_onboarding(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Initialize or get onboarding state for the authenticated student."""
    user_id = current_user["id"]
    service = OnboardingService(ProfileRepository(db), UserRepository(db))
    profile = await service.get_onboarding_state(user_id)
    return {
        "success": True,
        "data": profile,
        "message": "Onboarding state initialized.",
    }


@router.put("", status_code=status.HTTP_200_OK)
@router.put("/", status_code=status.HTTP_200_OK)
async def update_onboarding(
    profile_update: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Update complete onboarding profile state."""
    user_id = current_user["id"]
    service = OnboardingService(ProfileRepository(db), UserRepository(db))
    step_update = OnboardingStepUpdate(
        step_number=1,
        profile=profile_update.personal,
        career=profile_update.career,
        skills=profile_update.skills,
        integrations=profile_update.integrations,
        preferences=profile_update.preferences,
        goals=profile_update.goals,
    )
    updated = await service.save_step_data(user_id, step_update)
    return {
        "success": True,
        "data": updated,
        "message": "Onboarding state updated.",
    }


@router.patch("/step", status_code=status.HTTP_200_OK)
async def update_onboarding_step(
    step_update: OnboardingStepUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Save data for a specific onboarding step (step 1 to 7)."""
    user_id = current_user["id"]
    service = OnboardingService(ProfileRepository(db), UserRepository(db))
    updated = await service.save_step_data(user_id, step_update)
    return {
        "success": True,
        "data": updated,
        "message": f"Onboarding step {step_update.step_number} saved successfully.",
    }


@router.post("/complete", status_code=status.HTTP_200_OK)
async def complete_onboarding(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Complete onboarding workflow and mark student onboarding status as finished."""
    user_id = current_user["id"]
    service = OnboardingService(ProfileRepository(db), UserRepository(db))
    result = await service.complete_onboarding(user_id)
    return {
        "success": True,
        "data": result,
        "message": "Onboarding completed successfully!",
    }


@router.get("/test")
async def test_onboarding_route() -> dict:
    """Placeholder endpoint for onboarding routes."""
    return {
        "status": "success",
        "module": "onboarding",
        "message": "Onboarding router operational",
    }
