import logging
import certifi
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manager class for async MongoDB client connection and database handles."""

    def __init__(self) -> None:
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

    async def connect_to_mongo(self) -> None:
        """Initialize MongoDB client connection and test reachability."""
        mongo_uri = settings.get_mongo_uri()
        logger.info("Connecting to MongoDB database: %s", settings.MONGODB_DATABASE)
        
        # First attempt with certifi TLS CA file
        try:
            client_kwargs = {"serverSelectionTimeoutMS": 5000}
            if mongo_uri.startswith("mongodb+srv://"):
                try:
                    client_kwargs["tls"] = True
                    client_kwargs["tlsCAFile"] = certifi.where()
                except Exception:
                    pass
            self.client = AsyncIOMotorClient(mongo_uri, **client_kwargs)
            self.db = self.client[settings.MONGODB_DATABASE]
            await self.client.admin.command("ping")
            logger.info("Successfully connected and pinged MongoDB.")
            return
        except Exception as e:
            logger.warning("Default AsyncIOMotorClient SSL connection failed (%s), trying fallback...", type(e).__name__)

        # Fallback attempt with tlsAllowInvalidCertificates=True for Atlas SSL compatibility
        try:
            fallback_kwargs = {
                "serverSelectionTimeoutMS": 5000,
                "tls": True,
                "tlsAllowInvalidCertificates": True,
            }
            self.client = AsyncIOMotorClient(mongo_uri, **fallback_kwargs)
            self.db = self.client[settings.MONGODB_DATABASE]
            await self.client.admin.command("ping")
            logger.info("Successfully connected and pinged MongoDB via SSL fallback.")
        except Exception as e:
            logger.error("Failed to connect to MongoDB: %s", type(e).__name__)

    async def close_mongo_connection(self) -> None:
        """Close MongoDB connection gracefully."""
        if self.client:
            logger.info("Closing MongoDB connection.")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("MongoDB connection closed.")

    async def ping_database(self) -> bool:
        """Ping MongoDB database to check health status."""
        if not self.client:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.warning("MongoDB ping check failed: %s", type(e).__name__)
            return False

    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """Return the active AsyncIOMotorDatabase instance."""
        return self.db


db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency helper to retrieve database instance."""
    if db_manager.db is None:
        raise RuntimeError("Database connection is not initialized.")
    return db_manager.db


async def get_gridfs_bucket(bucket_name: str = "resumes") -> AsyncIOMotorGridFSBucket:
    """Dependency helper to retrieve Motor GridFSBucket handle."""
    db = await get_database()
    return AsyncIOMotorGridFSBucket(db, bucket_name=bucket_name)
