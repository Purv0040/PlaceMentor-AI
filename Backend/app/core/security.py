from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    bcrypt only processes the first 72 bytes of a password,
    so the password is explicitly truncated to 72 UTF-8 bytes.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    password_bytes = password.encode("utf-8")[:72]

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt,
    )

    return hashed_password.decode("utf-8")


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    try:
        if not plain_password or not hashed_password:
            return False

        password_bytes = plain_password.encode(
            "utf-8"
        )[:72]

        hash_bytes = hashed_password.encode(
            "utf-8"
        )

        return bcrypt.checkpw(
            password_bytes,
            hash_bytes,
        )

    except (ValueError, TypeError, Exception):
        return False


# ============================================================
# CREATE ACCESS TOKEN
# ============================================================

def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate a JWT access token.

    Payload contains:
    - sub   -> user ID
    - iat   -> issued-at timestamp
    - exp   -> expiration timestamp
    - type  -> access
    """

    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
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


# ============================================================
# CREATE REFRESH TOKEN
# ============================================================

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a JWT refresh token.

    Payload contains:
    - sub   -> user ID
    - iat   -> issued-at timestamp
    - exp   -> expiration timestamp
    - type  -> refresh
    """

    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
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


# ============================================================
# DECODE / VALIDATE JWT
# ============================================================

def decode_token(
    token: str,
) -> Dict[str, Any]:
    """
    Decode and validate a JWT.

    This function validates:
    - Token exists
    - JWT signature
    - JWT algorithm
    - Token expiration
    - Required subject claim
    """

    if not token or not token.strip():
        raise UnauthorizedException(
            "Authentication token required."
        )

    try:
        payload = jwt.decode(
            token.strip(),
            settings.JWT_SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
        )

        # ----------------------------------------------------
        # Validate required subject
        # ----------------------------------------------------
        if not payload.get("sub"):
            raise UnauthorizedException(
                "Invalid token payload."
            )

        # ----------------------------------------------------
        # Validate token type
        # ----------------------------------------------------
        if payload.get("type") not in {
            "access",
            "refresh",
        }:
            raise UnauthorizedException(
                "Invalid token type."
            )

        return payload

    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(
            "Token has expired."
        )

    except jwt.InvalidSignatureError:
        raise UnauthorizedException(
            "Invalid token signature."
        )

    except jwt.DecodeError:
        raise UnauthorizedException(
            "Could not decode token."
        )

    except jwt.InvalidTokenError:
        raise UnauthorizedException(
            "Could not validate credentials."
        )