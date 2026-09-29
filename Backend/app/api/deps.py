from typing import Optional, Dict, Any

from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis

from app.core.database import get_database
from app.core.redis import redis_manager
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository


# ============================================================
# HTTP Bearer Authentication
# ============================================================
# This creates the JWT authentication scheme in Swagger.
# Swagger will show the 🔒 Authorize button.
bearer_scheme = HTTPBearer(auto_error=False)


# ============================================================
# MongoDB Dependency
# ============================================================

async def get_db() -> AsyncIOMotorDatabase:
    """
    Dependency helper to get the active MongoDB database instance.
    """
    return await get_database()


# ============================================================
# Redis Dependency
# ============================================================

async def get_redis_client() -> Optional[redis.Redis]:
    """
    Dependency helper to get the active Redis client instance.
    """
    return redis_manager.get_client()


# ============================================================
# Current User Authentication
# ============================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(
        bearer_scheme
    ),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """
    Validate Bearer JWT access token and return
    the currently authenticated user.
    """

    # --------------------------------------------------------
    # 1. Check Authorization header
    # --------------------------------------------------------
    if credentials is None:
        raise UnauthorizedException(
            "Authentication token required."
        )

    # --------------------------------------------------------
    # 2. Get JWT token
    # --------------------------------------------------------
    token = credentials.credentials

    if not token:
        raise UnauthorizedException(
            "Authentication token required."
        )

    # --------------------------------------------------------
    # 3. Decode and validate JWT
    # --------------------------------------------------------
    payload = decode_token(token)

    # --------------------------------------------------------
    # 4. Make sure this is an ACCESS token
    # --------------------------------------------------------
    token_type = payload.get("type")

    if token_type != "access":
        raise UnauthorizedException(
            "Invalid token type. Access token required."
        )

    # --------------------------------------------------------
    # 5. Get user ID from JWT subject
    # --------------------------------------------------------
    user_id = payload.get("sub")

    if not user_id:
        raise UnauthorizedException(
            "Invalid token payload."
        )

    # --------------------------------------------------------
    # 6. Find user in MongoDB
    # --------------------------------------------------------
    user_repository = UserRepository(db)

    user = await user_repository.get_by_id(
        str(user_id)
    )

    # --------------------------------------------------------
    # 7. User must exist
    # --------------------------------------------------------
    if not user:
        raise UnauthorizedException(
            "User not found or account deactivated."
        )

    # --------------------------------------------------------
    # 8. Check whether account is active
    # --------------------------------------------------------
    if not user.get("is_active", True):
        raise UnauthorizedException(
            "User account is deactivated."
        )

    # --------------------------------------------------------
    # 9. Normalize user ID
    # --------------------------------------------------------
    if "id" not in user:
        user["id"] = str(
            user.get("_id", user_id)
        )

    # --------------------------------------------------------
    # 10. Return authenticated user
    # --------------------------------------------------------
    return user