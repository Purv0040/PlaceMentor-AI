from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, get_db
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from app.services.auth_service import AuthService


router = APIRouter()


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    req: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """
    Register a new student user.
    """

    auth_service = AuthService(
        UserRepository(db),
        ProfileRepository(db),
    )

    result = await auth_service.register_user(
        email=req.email,
        password=req.password,
        full_name=req.full_name,
    )

    return {
        "success": True,
        "data": result,
        "message": "User registered successfully!",
    }


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    req: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """
    Authenticate a user and return access and refresh tokens.
    """

    auth_service = AuthService(
        UserRepository(db),
        ProfileRepository(db),
    )

    result = await auth_service.authenticate_user(
        email=req.email,
        password=req.password,
    )

    return {
        "success": True,
        "data": result,
        "message": "Login successful!",
    }


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate a new access token using a refresh token.
    """

    auth_service = AuthService(
        UserRepository(db),
    )

    result = await auth_service.refresh_tokens(
        req.refresh_token
    )

    return {
        "success": True,
        "data": result,
        "message": "Tokens refreshed successfully!",
    }


# ============================================================
# GET CURRENT USER
# ============================================================

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
) -> Dict[str, Any]:
    """
    Return the currently authenticated user.
    """

    return {
        "success": True,
        "data": {
            "id": current_user.get("id"),
            "email": current_user.get("email"),
            "full_name": current_user.get("full_name"),
            "is_onboarded": current_user.get(
                "is_onboarded",
                False,
            ),
        },
        "message": "Authenticated user retrieved.",
    }


# ============================================================
# LOGOUT
# ============================================================

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    current_user: Dict[str, Any] = Depends(
        get_current_user
    ),
) -> Dict[str, Any]:
    """
    Logout the current authenticated user.

    JWTs are currently stateless, so this endpoint confirms
    logout on the client side. Token revocation can be added
    later using Redis/token blacklist functionality.
    """

    return {
        "success": True,
        "message": "Successfully logged out.",
    }


# ============================================================
# AUTH ROUTER TEST
# ============================================================

@router.get("/test")
async def test_auth_route() -> Dict[str, str]:
    """
    Authentication router health/test endpoint.
    """

    return {
        "status": "success",
        "module": "auth",
        "message": "Auth router operational",
    }