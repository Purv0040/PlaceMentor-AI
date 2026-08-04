"""Main FastAPI application entry point for AI Resume Analyzer."""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from api.resume import router as resume_router
from models.resume import HealthCheckResponse, ErrorResponse
from utils.exceptions import ResumeAnalyzerException
from utils.logger import logger

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Phase 1: AI Resume Analyzer backend for Indian Students. Evaluates resume PDF, extracts technical skills, detects standard sections, computes ATS score, and generates actionable improvement recommendations.",
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

# Register API Routers
app.include_router(resume_router)


@app.get("/health", response_model=HealthCheckResponse, tags=["Health Check"])
async def health_check():
    """Health check endpoint to verify backend service status."""
    return HealthCheckResponse(
        status="ok",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION
    )


# Exception Handlers
@app.exception_handler(ResumeAnalyzerException)
async def custom_exception_handler(request: Request, exc: ResumeAnalyzerException):
    """Global handler for custom application exceptions."""
    logger.warning(f"ResumeAnalyzerException: {exc.message} (HTTP {exc.status_code})")
    error_payload = ErrorResponse(
        success=False,
        error=exc.__class__.__name__,
        message=exc.message,
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global handler for FastAPI HTTP exceptions."""
    error_payload = ErrorResponse(
        success=False,
        error="HTTPException",
        message=str(exc.detail),
        status_code=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload.model_dump()
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Global fallback handler for unhandled internal exceptions."""
    logger.error(f"Unhandled error on path {request.url.path}: {exc}", exc_info=True)
    error_payload = ErrorResponse(
        success=False,
        error="InternalServerError",
        message="An unexpected internal server error occurred.",
        status_code=500
    )
    return JSONResponse(
        status_code=500,
        content=error_payload.model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
