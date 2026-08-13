"""Main FastAPI application entry point for AI GitHub Analyzer."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from api.github import router as github_router
from utils.exceptions import GitHubAnalyzerException
from utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Phase 2: AI GitHub Analyzer backend for Indian Students. Evaluates GitHub profile completeness, repository quality, technology stack diversity, README documentation, and activity signals.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(github_router)


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint verifying GitHub Analyzer service operational status."""
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Exception Handlers
@app.exception_handler(GitHubAnalyzerException)
async def github_exception_handler(request: Request, exc: GitHubAnalyzerException):
    """Global handler for custom GitHub Analyzer exceptions."""
    logger.warning(f"GitHubAnalyzerException: {exc.message} (HTTP {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "HTTPException",
            "message": str(exc.detail),
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Global fallback handler for unhandled internal exceptions."""
    logger.error(f"Unhandled error on path {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": "An unexpected internal server error occurred.",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
