from typing import Any, Dict, Optional
import logging

# pyrefly: ignore [missing-import]
from google.oauth2 import id_token as google_id_token  # type: ignore
# pyrefly: ignore [missing-import]
from google.auth.transport import requests as google_requests  # type: ignore

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
from app.core.config import settings
from app.repositories.profile_repository import ProfileRepository
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


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

        try:
            created_user = await self.user_repo.create(
                user_data
            )
        except Exception as e:
            if "duplicate" in str(e).lower() or "e11000" in str(e).lower():
                raise ConflictException(
                    "A user with this email already exists."
                )
            logger.error("Failed to create user during registration: %s", e)
            raise

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

    # ========================================================
    # GOOGLE OAUTH AUTHENTICATION
    # ========================================================

    async def google_authenticate(
        self,
        credential: str,
    ) -> Dict[str, Any]:
        """
        Authenticate a user via Google OAuth.

        Verifies the Google ID token, finds or creates
        the user, and returns JWT tokens.
        """

        # ----------------------------------------------------
        # 1. Verify Google ID token
        # ----------------------------------------------------
        try:
            idinfo = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError as e:
            logger.warning("Google token verification failed: %s", e)
            raise UnauthorizedException(
                "Invalid Google credentials. Please try again."
            )
        except Exception as e:
            logger.error("Google authentication network or verification error: %s", e)
            raise UnauthorizedException(
                "Unable to verify Google credentials at this time. Please try again or sign up with email and password."
            )

        # ----------------------------------------------------
        # 2. Extract user info from token
        # ----------------------------------------------------
        google_email = idinfo.get("email", "").strip().lower()
        google_name = idinfo.get("name", "")
        email_verified = idinfo.get("email_verified", False)

        if not google_email or not email_verified:
            raise UnauthorizedException(
                "Google account email is not verified."
            )

        # ----------------------------------------------------
        # 3. Find or create user
        # ----------------------------------------------------
        existing_user = await self.user_repo.get_by_email(
            google_email
        )

        if existing_user:
            # Existing user — log them in
            user = existing_user
            user_id = str(
                user.get("id", user.get("_id"))
            )
            is_onboarded = user.get("is_onboarded", False)
        else:
            # New user — create account (no password for OAuth)
            import secrets
            random_password = secrets.token_urlsafe(32)
            hashed = hash_password(random_password)

            user_data = {
                "email": google_email,
                "hashed_password": hashed,
                "full_name": google_name or google_email.split("@")[0],
                "is_active": True,
                "is_onboarded": False,
                "auth_provider": "google",
            }

            try:
                created_user = await self.user_repo.create(user_data)
            except Exception as e:
                if "duplicate" in str(e).lower() or "e11000" in str(e).lower():
                    existing_user = await self.user_repo.get_by_email(google_email)
                    if existing_user:
                        created_user = existing_user
                    else:
                        raise ConflictException("An account with this email already exists.")
                else:
                    logger.error("Failed to create OAuth user: %s", e)
                    raise

            user_id = str(
                created_user.get("id", created_user.get("_id"))
            )
            user = created_user
            is_onboarded = False

            # Create initial profile
            if self.profile_repo:
                await self.profile_repo.create_profile(
                    user_id=user_id,
                )

        # ----------------------------------------------------
        # 4. Generate JWT tokens
        # ----------------------------------------------------
        access_token = create_access_token(
            subject=user_id,
            extra_claims={
                "email": google_email,
            },
        )

        refresh_token = create_refresh_token(
            subject=user_id,
        )

        # ----------------------------------------------------
        # 5. Return result
        # ----------------------------------------------------
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": google_email,
                "full_name": user.get("full_name", google_name),
                "is_onboarded": is_onboarded,
            },
        }
