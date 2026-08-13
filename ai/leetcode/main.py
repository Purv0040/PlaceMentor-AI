"""Main FastAPI application entry point for AI LeetCode Analyzer."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from api.leetcode import router as leetcode_router
from utils.exceptions import LeetCodeAnalyzerException
from utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Phase 2: AI LeetCode Analyzer backend for Indian Students. Evaluates solved DSA problems, difficulty ratios, 13 core DSA topics, practice consistency, and contest rankings.",
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
app.include_router(leetcode_router)


@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint verifying LeetCode Analyzer service operational status."""
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Exception Handlers
@app.exception_handler(LeetCodeAnalyzerException)
async def leetcode_exception_handler(request: Request, exc: LeetCodeAnalyzerException):
    """Global handler for custom LeetCode Analyzer exceptions."""
    logger.warning(f"LeetCodeAnalyzerException: {exc.message} (HTTP {exc.status_code})")
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
