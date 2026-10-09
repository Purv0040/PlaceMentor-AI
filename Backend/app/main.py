import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import db_manager
from app.core.redis import redis_manager
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.api.routes import api_router

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown event hooks."""
    logger.info("Starting up %s Backend Application...", settings.APP_NAME)
    
    # Connect to MongoDB
    await db_manager.connect_to_mongo()

    # Connect to Redis
    await redis_manager.connect_to_redis()

    yield

    logger.info("Shutting down %s Backend Application...", settings.APP_NAME)
    
    # Cleanup connection resources
    await db_manager.close_mongo_connection()
    await redis_manager.close_redis_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API foundation for AI Placement Copilot",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Custom Middlewares
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RequestIDMiddleware)

# Configure CORS middleware (Must be added last so it is the outermost middleware)
cors_origins = (
    settings.CORS_ORIGINS
    if isinstance(settings.CORS_ORIGINS, list)
    else [settings.CORS_ORIGINS]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root Endpoint
@app.get("/", status_code=status.HTTP_200_OK, tags=["System"])
async def root() -> Dict[str, str]:
    """Root application status endpoint."""
    return {
        "message": "AI Placement Copilot API",
        "status": "running",
    }


# Health Check Endpoints
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Placement Copilot API",
    }


@app.get(f"{settings.API_V1_PREFIX}/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def api_v1_health() -> Dict[str, Any]:
    """Detailed health check endpoint reporting services status."""
    mongo_ping = await db_manager.ping_database()
    redis_ping = await redis_manager.ping_redis()

    overall_status = "ok" if (mongo_ping and redis_ping) else "degraded"

    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "components": {
            "database": "connected" if mongo_ping else "disconnected",
            "redis": "connected" if redis_ping else "disconnected",
        },
    }


@app.get(f"{settings.API_V1_PREFIX}/health/database", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_database() -> Dict[str, Any]:
    """Health check endpoint specifically for MongoDB database."""
    mongo_ping = await db_manager.ping_database()
    return {
        "component": "MongoDB",
        "database_name": settings.MONGODB_DATABASE,
        "status": "connected" if mongo_ping else "disconnected",
    }


@app.get(f"{settings.API_V1_PREFIX}/health/redis", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_redis() -> Dict[str, Any]:
    """Health check endpoint specifically for Redis."""
    redis_ping = await redis_manager.ping_redis()
    return {
        "component": "Redis",
        "status": "connected" if redis_ping else "disconnected",
    }
