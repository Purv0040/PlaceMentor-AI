import logging
from typing import Dict, Any, Optional
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ProfileRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictException, UnauthorizedException, BadRequestException

logger = logging.getLogger(__name__)


class AuthService:
    """Service layer handling authentication logic."""

    def __init__(self, user_repo: UserRepository, profile_repo: Optional[ProfileRepository] = None) -> None:
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    async def register_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Register a new user, create initial profile shell, and return JWT tokens."""
        existing = await self.user_repo.get_by_email(email.lower().strip())
        if existing:
            raise ConflictException("An account with this email already exists.")

        hashed_pwd = hash_password(password)
        user_data = {
            "email": email.lower().strip(),
            "hashed_password": hashed_pwd,
            "full_name": full_name.strip(),
            "is_active": True,
            "is_onboarded": False,
        }

        created_user = await self.user_repo.create(user_data)
        user_id = created_user["_id"]

        # Initialize student profile document for user
        if self.profile_repo:
            await self.profile_repo.create_profile(user_id, initial_data={"personal.name": full_name, "personal.email": email})

        access_token = create_access_token(subject=user_id, extra_claims={"email": email})
        refresh_token = create_refresh_token(subject=user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": created_user["email"],
                "full_name": created_user["full_name"],
                "is_onboarded": created_user["is_onboarded"],
            },
        }

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user credentials and return JWT tokens."""
        user = await self.user_repo.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user.get("hashed_password", "")):
            raise UnauthorizedException("Invalid email or password credentials.")

        if not user.get("is_active", True):
            raise UnauthorizedException("Account is deactivated.")

        user_id = str(user["_id"])
        access_token = create_access_token(subject=user_id, extra_claims={"email": user["email"]})
        refresh_token = create_refresh_token(subject=user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user["email"],
                "full_name": user["full_name"],
                "is_onboarded": user.get("is_onboarded", False),
            },
        }

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Validate refresh token and issue new access token."""
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type for refresh.")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload.")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.get("is_active", True):
            raise UnauthorizedException("User not found or account deactivated.")

        new_access_token = create_access_token(subject=user_id, extra_claims={"email": user["email"]})
        new_refresh_token = create_refresh_token(subject=user_id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
