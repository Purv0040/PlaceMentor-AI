import time
import logging
from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, Response
from app.core.redis import redis_manager

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Production Redis-backed rate limiting middleware with fail-safe fallback."""

    # Configured rate limits (requests per minute)
    SENSITIVE_PATHS = {
        "/api/v1/auth/login": 15,
        "/api/v1/auth/register": 15,
        "/api/v1/resume/upload": 20,
        "/api/v1/mentor/chat": 30,
        "/api/v1/mock-interview/generate": 20,
    }
    DEFAULT_LIMIT_PER_MINUTE = 180

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Bypass rate limiting for static/docs/health checks
        if path.startswith(("/docs", "/redoc", "/openapi.json", "/health")) or request.method == "OPTIONS":
            return await call_next(request)

        # Determine rate limit key & threshold
        client_ip = request.client.host if request.client else "127.0.0.1"
        user_id = getattr(request.state, "user_id", None)
        caller_id = user_id or client_ip

        limit = self.SENSITIVE_PATHS.get(path, self.DEFAULT_LIMIT_PER_MINUTE)
        current_minute = int(time.time() // 60)
        rate_key = f"rate_limit:{caller_id}:{path}:{current_minute}"

        try:
            client = redis_manager.get_client()
            if client:
                current_count = await client.incr(rate_key)
                if current_count == 1:
                    await client.expire(rate_key, 60)

                if current_count > limit:
                    logger.warning("Rate limit exceeded for %s on %s (%d/%d)", caller_id, path, current_count, limit)
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "success": False,
                            "error": {
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": f"Rate limit exceeded. Maximum {limit} requests per minute allowed.",
                                "details": None,
                            },
                        },
                        headers={"Retry-After": "60"},
                    )
        except Exception as exc:
            # Graceful failure: log warning and continue serving request if Redis fails
            logger.warning("Redis rate limit check failed, allowing request: %s", str(exc))

        return await call_next(request)

