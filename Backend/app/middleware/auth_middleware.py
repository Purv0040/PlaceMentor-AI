import logging
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, Response
from app.core.security import decode_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware stub for parsing Authorization Bearer tokens into request state."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        authorization: Optional[str] = request.headers.get("Authorization")
        request.state.user_id = None
        request.state.token_payload = None

        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            try:
                payload = decode_token(token)
                request.state.user_id = payload.get("sub")
                request.state.token_payload = payload
            except Exception:
                # Middleware does not reject requests directly; route dependencies handle auth protection.
                pass

        return await call_next(request)
