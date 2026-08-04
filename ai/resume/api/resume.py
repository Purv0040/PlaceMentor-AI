"""API Route Endpoints for Resume Analysis with enhanced file validation."""

import os
from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, File, UploadFile, HTTPException, status

from config import settings
from models.resume import ResumeAnalysisResponse, ErrorResponse
from services.resume_pipeline import resume_pipeline
from utils.exceptions import (
    ResumeAnalyzerException,
    InvalidPDFError,
    EmptyResumeError,
    ResumeTooLargeError
)
from utils.logger import logger

router = APIRouter(prefix="/api/v1/resume", tags=["Resume Analyzer"])


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    response_model_exclude_none=True,
    summary="Upload & Analyze Resume PDF",
    description="Upload a student PDF resume to extract metadata, section-wise ATS scores, missing sections, technical skills, statistics, and actionable recommendations.",
    responses={
        200: {"model": ResumeAnalysisResponse, "description": "Analysis complete."},
        400: {"model": ErrorResponse, "description": "Invalid file format, unsupported extension, or corrupted/encrypted PDF."},
        413: {"model": ErrorResponse, "description": "File exceeds maximum size limit (5MB)."},
        422: {"model": ErrorResponse, "description": "Unprocessable PDF or empty text extracted."},
        500: {"model": ErrorResponse, "description": "Internal server processing error."}
    }
)
async def analyze_resume(file: Annotated[UploadFile, File(...)]) -> ResumeAnalysisResponse:
    """Endpoint handling multipart PDF upload and triggering the resume pipeline."""
    import time
    upload_start = time.perf_counter()

    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided in upload request."
        )

    # 1. Validate File Extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext != ".pdf":
        logger.warning(f"Rejected upload for unsupported file extension: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{file_ext}'. Only PDF files (.pdf) are allowed."
        )

    # 2. Validate MIME Type
    allowed_mimes = ["application/pdf", "application/x-pdf", "application/acrobat", "applications/vnd.pdf", "text/pdf"]
    if file.content_type and file.content_type.lower() not in allowed_mimes and file.content_type != "application/octet-stream":
        logger.warning(f"Rejected upload for invalid MIME type '{file.content_type}': {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{file.content_type}'. Only PDF documents are supported."
        )

    # 3. Read contents & Validate File Size
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file stream: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file contents."
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        logger.warning(f"File size {len(content)} bytes exceeds limit of {max_bytes} bytes.")
        raise ResumeTooLargeError(max_mb=settings.MAX_UPLOAD_SIZE_MB)

    if len(content) == 0:
        raise EmptyResumeError("The uploaded PDF file is empty (0 bytes).")

    # 4. Optional: Save copy to uploads/ for auditing
    temp_filepath = settings.UPLOAD_DIR / f"upload_{file.filename}"
    try:
        with open(temp_filepath, "wb") as f:
            f.write(content)
        
        upload_time = time.perf_counter() - upload_start
        logger.info(f"Upload Time: {upload_time:.2f} sec for {file.filename}")

        # 5. Process through resume pipeline
        response = resume_pipeline.process_resume(content, filename=file.filename)
        return response

    except ResumeAnalyzerException as exc:
        logger.warning(f"Resume Analyzer Exception during analysis: {exc.message}")
        logger.error(f"Errors: {exc.__class__.__name__} - {exc.message}")
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except HTTPException as e:
        logger.error(f"Errors: HTTPException - {str(e.detail)}")
        raise
    except Exception as e:
        logger.error(f"Unhandled server error while processing {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the resume: {str(e)}"
        )
    finally:
        # 6. Clean up temporary upload file
        if temp_filepath.exists():
            try:
                os.remove(temp_filepath)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_filepath}: {e}")
