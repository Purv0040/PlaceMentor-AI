import logging
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """Manager class for async Redis client connection and health checks."""

    def __init__(self) -> None:
        self.redis_client: Optional[redis.Redis] = None

    async def connect_to_redis(self) -> None:
        """Initialize Redis connection and attempt health ping."""
        try:
            logger.info("Connecting to Redis at: %s", settings.REDIS_URL.split("@")[-1])
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=3.0,
            )
            await self.redis_client.ping()
            logger.info("Successfully connected and pinged Redis.")
        except Exception as e:
            logger.warning(
                "Redis connection initialization failed or Redis unavailable: %s",
                type(e).__name__,
            )
            # Application should not crash permanently if Redis is temporarily unavailable on startup.

    async def close_redis_connection(self) -> None:
        """Close Redis client connection gracefully."""
        if self.redis_client:
            logger.info("Closing Redis connection.")
            try:
                await self.redis_client.aclose()
            except Exception as e:
                logger.warning("Error while closing Redis connection: %s", type(e).__name__)
            self.redis_client = None
            logger.info("Redis connection closed.")

    async def ping_redis(self) -> bool:
        """Ping Redis server to verify health status."""
        if not self.redis_client:
            return False
        try:
            return await self.redis_client.ping()
        except Exception as e:
            logger.warning("Redis ping check failed: %s", type(e).__name__)
            return False

    def get_client(self) -> Optional[redis.Redis]:
        """Return the active Redis client handle."""
        return self.redis_client


redis_manager = RedisManager()


async def get_redis() -> Optional[redis.Redis]:
    """Dependency helper to retrieve Redis client instance."""
    return redis_manager.get_client()
