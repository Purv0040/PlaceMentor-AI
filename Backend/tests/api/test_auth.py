from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    bcrypt only supports passwords up to 72 bytes.
    """

    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a plain password against a bcrypt hash."""

    try:
        password_bytes = plain_password.encode("utf-8")[:72]
        hashed_bytes = hashed_password.encode("utf-8")

        return bcrypt.checkpw(
            password_bytes,
            hashed_bytes,
        )

    except (ValueError, TypeError):
        return False


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a JWT access token."""

    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""

    now = datetime.now(timezone.utc)

    expire = (
        now + expires_delta
        if expires_delta
        else now
        + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT.

    This validates:
    - signature
    - expiration
    - token structure

    Token type must be checked by the caller.
    """

    if not token:
        raise UnauthorizedException(
            "Authentication token is required."
        )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        if not payload.get("sub"):
            raise UnauthorizedException(
                "Invalid token payload."
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(
            "Token has expired."
        )

    except jwt.InvalidTokenError:
        raise UnauthorizedException(
            "Could not validate credentials."
        )