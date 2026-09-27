from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.repositories.profile_repository import ProfileRepository
from app.services.profile_service import ProfileService
from app.schemas.profile import ProfileUpdate

router = APIRouter()


@router.get("/me/profile", status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve profile of the authenticated student."""
    user_id = current_user["id"]
    service = ProfileService(ProfileRepository(db))
    profile = await service.get_or_create_profile(
        user_id=user_id,
        user_email=current_user.get("email"),
        user_name=current_user.get("full_name"),
    )
    return {
        "success": True,
        "data": profile,
        "message": "Student profile retrieved successfully.",
    }


@router.put("/me/profile", status_code=status.HTTP_200_OK)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Replace/Update profile sections of the authenticated student."""
    user_id = current_user["id"]
    service = ProfileService(ProfileRepository(db))
    updated = await service.update_profile(user_id, profile_update)
    return {
        "success": True,
        "data": updated,
        "message": "Student profile updated successfully.",
    }


@router.patch("/me/profile", status_code=status.HTTP_200_OK)
async def patch_my_profile(
    profile_update: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Partially update profile sections of the authenticated student."""
    user_id = current_user["id"]
    service = ProfileService(ProfileRepository(db))
    updated = await service.update_profile(user_id, profile_update)
    return {
        "success": True,
        "data": updated,
        "message": "Student profile updated successfully.",
    }


@router.get("/test")
async def test_users_route() -> dict:
    """Placeholder test endpoint for users router."""
    return {
        "status": "success",
        "module": "users",
        "message": "Users router operational",
    }
