from typing import Any, Dict, Optional

from app.core.exceptions import (
    ConflictException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Authentication service.

    Handles:
    - User registration
    - User login
    - JWT access token generation
    - JWT refresh token generation
    - Refresh token validation
    """

    def __init__(
        self,
        user_repo: UserRepository,
        profile_repo: Optional[ProfileRepository] = None,
    ):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    # ========================================================
    # REGISTER
    # ========================================================

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> Dict[str, Any]:
        """
        Register a new student user.
        """

        # Normalize input
        email = email.strip().lower()
        full_name = full_name.strip()

        # ----------------------------------------------------
        # Check whether email already exists
        # ----------------------------------------------------
        existing_user = await self.user_repo.get_by_email(
            email
        )

        if existing_user:
            raise ConflictException(
                "A user with this email already exists."
            )

        # ----------------------------------------------------
        # Hash password
        # ----------------------------------------------------
        hashed_password = hash_password(password)

        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_onboarded": False,
        }

        created_user = await self.user_repo.create(
            user_data
        )

        user_id = str(
            created_user.get(
                "id",
                created_user.get("_id"),
            )
        )

        # ----------------------------------------------------
        # Create initial student profile
        # ----------------------------------------------------
        if self.profile_repo:
            await self.profile_repo.create_profile(
                user_id=user_id,
            )

        # ----------------------------------------------------
        # Generate tokens
        # ----------------------------------------------------
        access_token = create_access_token(
            subject=user_id,
            extra_claims={
                "email": email,
            },
        )

        refresh_token = create_refresh_token(
            subject=user_id,
        )

        # ----------------------------------------------------
        # Return registration result
        # ----------------------------------------------------
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "is_onboarded": False,
            },
        }

    # ========================================================
    # LOGIN
    # ========================================================

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Authenticate user and return JWT tokens.
        """

        # Normalize email
        email = email.strip().lower()

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------
        user = await self.user_repo.get_by_email(
            email
        )

        if not user:
            raise UnauthorizedException(
                "Invalid email or password."
            )

        # ----------------------------------------------------
        # Verify password
        # ----------------------------------------------------
        password_valid = verify_password(
            password,
            user.get("hashed_password", ""),
        )

        if not password_valid:
            raise UnauthorizedException(
                "Invalid email or password."
            )

        # ----------------------------------------------------
        # Check account status
        # ----------------------------------------------------
        if not user.get("is_active", True):
            raise UnauthorizedException(
                "Account is deactivated."
            )

        # ----------------------------------------------------
        # Normalize user ID
        # ----------------------------------------------------
        user_id = str(
            user.get(
                "id",
                user.get("_id"),
            )
        )

        # ----------------------------------------------------
        # Generate access token
        # ----------------------------------------------------
        access_token = create_access_token(
            subject=user_id,
            extra_claims={
                "email": user.get("email"),
            },
        )

        # ----------------------------------------------------
        # Generate refresh token
        # ----------------------------------------------------
        refresh_token = create_refresh_token(
            subject=user_id,
        )

        # ----------------------------------------------------
        # Return login result
        # ----------------------------------------------------
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": user.get("email"),
                "full_name": user.get("full_name"),
                "is_onboarded": user.get(
                    "is_onboarded",
                    False,
                ),
            },
        }

    # ========================================================
    # REFRESH TOKENS
    # ========================================================

    async def refresh_tokens(
        self,
        refresh_token: str,
    ) -> Dict[str, Any]:
        """
        Validate a refresh token and issue new
        access and refresh tokens.
        """

        # ----------------------------------------------------
        # 1. Make sure refresh token was provided
        # ----------------------------------------------------
        if not refresh_token:
            raise UnauthorizedException(
                "Refresh token required."
            )

        # ----------------------------------------------------
        # 2. Decode JWT
        # ----------------------------------------------------
        payload = decode_token(
            refresh_token.strip()
        )

        # ----------------------------------------------------
        # 3. Make sure it is a refresh token
        # ----------------------------------------------------
        if payload.get("type") != "refresh":
            raise UnauthorizedException(
                "Invalid token type. Refresh token required."
            )

        # ----------------------------------------------------
        # 4. Get user ID from token
        # ----------------------------------------------------
        user_id = payload.get("sub")

        if not user_id:
            raise UnauthorizedException(
                "Invalid refresh token payload."
            )

        user_id = str(user_id)

        # ----------------------------------------------------
        # 5. Find user in MongoDB
        # ----------------------------------------------------
        user = await self.user_repo.get_by_id(
            user_id
        )

        if not user:
            raise UnauthorizedException(
                "User not found."
            )

        # ----------------------------------------------------
        # 6. Check account status
        # ----------------------------------------------------
        if not user.get("is_active", True):
            raise UnauthorizedException(
                "Account is deactivated."
            )

        # ----------------------------------------------------
        # 7. Normalize user ID
        # ----------------------------------------------------
        normalized_user_id = str(
            user.get(
                "id",
                user.get(
                    "_id",
                    user_id,
                ),
            )
        )

        # ----------------------------------------------------
        # 8. Generate new access token
        # ----------------------------------------------------
        new_access_token = create_access_token(
            subject=normalized_user_id,
            extra_claims={
                "email": user.get("email"),
            },
        )

        # ----------------------------------------------------
        # 9. Generate new refresh token
        # ----------------------------------------------------
        new_refresh_token = create_refresh_token(
            subject=normalized_user_id,
        )

        # ----------------------------------------------------
        # 10. Return new tokens
        # ----------------------------------------------------
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": {
                "id": normalized_user_id,
                "email": user.get("email"),
                "full_name": user.get("full_name"),
                "is_onboarded": user.get(
                    "is_onboarded",
                    False,
                ),
            },
        }