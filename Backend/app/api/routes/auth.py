from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshTokenRequest, TokenResponse
from app.schemas.common import ResponseModel

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Register a new student user and initialize profile."""
    auth_service = AuthService(UserRepository(db), ProfileRepository(db))
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


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    req: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Authenticate user credentials and return JWT tokens."""
    auth_service = AuthService(UserRepository(db), ProfileRepository(db))
    result = await auth_service.authenticate_user(
        email=req.email,
        password=req.password,
    )
    return {
        "success": True,
        "data": result,
        "message": "Login successful!",
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    req: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Issue a new access token using a valid refresh token."""
    auth_service = AuthService(UserRepository(db))
    result = await auth_service.refresh_tokens(req.refresh_token)
    return {
        "success": True,
        "data": result,
        "message": "Tokens refreshed successfully!",
    }


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Retrieve current authenticated user details."""
    safe_user = {
        "id": current_user["id"],
        "email": current_user.get("email"),
        "full_name": current_user.get("full_name"),
        "is_onboarded": current_user.get("is_onboarded", False),
    }
    return {
        "success": True,
        "data": safe_user,
        "message": "Authenticated user retrieved.",
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Logout current user session."""
    return {
        "success": True,
        "message": "Successfully logged out.",
    }


@router.get("/test")
async def test_auth_route() -> dict:
    """Placeholder test endpoint for auth router."""
    return {
        "status": "success",
        "module": "auth",
        "message": "Auth router operational",
    }
