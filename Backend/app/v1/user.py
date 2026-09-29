from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, get_db
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileUpdateRequest


router = APIRouter()


# ============================================================
# GET CURRENT USER PROFILE
# ============================================================

@router.get(
    "/me/profile",
    status_code=status.HTTP_200_OK,
)
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:

    user_id = str(current_user["id"])

    profile_repository = ProfileRepository(db)

    profile = await profile_repository.get_by_user_id(user_id)

    if not profile:
        return {
            "success": True,
            "data": None,
            "message": "Student profile not found.",
        }

    return {
        "success": True,
        "data": profile,
        "message": "Student profile retrieved successfully.",
    }


# ============================================================
# PUT CURRENT USER PROFILE
# ============================================================

@router.put(
    "/me/profile",
    status_code=status.HTTP_200_OK,
)
async def update_my_profile(
    profile_data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:

    user_id = str(current_user["id"])

    profile_repository = ProfileRepository(db)

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    updated_profile = await profile_repository.update(
        user_id=user_id,
        update_data=update_data,
    )

    if not updated_profile:
        return {
            "success": False,
            "data": None,
            "message": "Student profile not found or update failed.",
        }

    return {
        "success": True,
        "data": updated_profile,
        "message": "Student profile updated successfully.",
    }


# ============================================================
# PATCH CURRENT USER PROFILE
# ============================================================

@router.patch(
    "/me/profile",
    status_code=status.HTTP_200_OK,
)
async def patch_my_profile(
    profile_data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:

    user_id = str(current_user["id"])

    profile_repository = ProfileRepository(db)

    # IMPORTANT:
    # exclude_unset=True means only fields sent by the
    # frontend are included.
    #
    # exclude_none=False means:
    #
    # "githubHandle": null
    #
    # is NOT removed.
    #
    # Therefore null can clear an existing MongoDB value.

    update_data = profile_data.model_dump(
        exclude_unset=True,
        exclude_none=False,
    )

    if not update_data:
        return {
            "success": False,
            "data": None,
            "message": "No profile fields were provided.",
        }

    updated_profile = await profile_repository.patch(
        user_id=user_id,
        update_data=update_data,
    )

    if not updated_profile:
        return {
            "success": False,
            "data": None,
            "message": "Student profile not found or update failed.",
        }

    return {
        "success": True,
        "data": updated_profile,
        "message": "Student profile patched successfully.",
    }


# ============================================================
# TEST USERS ROUTE
# ============================================================

@router.get(
    "/test",
    status_code=status.HTTP_200_OK,
)
async def test_users_route() -> Dict[str, str]:

    return {
        "status": "success",
        "module": "users",
        "message": "Users router operational",
    }