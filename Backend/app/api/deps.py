from typing import Optional, Dict, Any
from fastapi import Depends, Header
from motor.motor_asyncio import AsyncIOMotorDatabase
import redis.asyncio as redis
from app.core.database import get_database
from app.core.redis import redis_manager
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency helper to get active MongoDB database instance."""
    return await get_database()


async def get_redis_client() -> Optional[redis.Redis]:
    """Dependency helper to get active Redis client instance."""
    return redis_manager.get_client()


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    """Validate Bearer JWT access token and return current authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Authentication token required.")

    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload.")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User not found or account deactivated.")

    user["id"] = str(user.get("_id", user_id))
    return user
