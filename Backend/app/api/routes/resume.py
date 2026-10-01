import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, Query, status
from fastapi.responses import Response, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket

from app.api.deps import get_current_user, get_db
from app.core.database import get_gridfs_bucket
from app.services.resume_service import ResumeService
from app.schemas.common import ResponseModel
from app.schemas.resume import (
    ResumeUploadResponse,
    ResumeMetadataResponse,
    ResumeListResponse,
    ResumeDetailResponse,
    ResumeAnalysisResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Resume"])


def get_resume_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
    gridfs: AsyncIOMotorGridFSBucket = Depends(get_gridfs_bucket)
) -> ResumeService:
    return ResumeService(db, gridfs_bucket=gridfs)


@router.post("/upload", response_model=ResponseModel[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Upload a new PDF resume for the authenticated student."""
    user_id = str(current_user["_id"])
    contents = await file.read()
    
    created = await service.upload_resume(
        user_id=user_id,
        file_bytes=contents,
        original_filename=file.filename or "resume.pdf",
        content_type=file.content_type or "application/pdf"
    )

    data = ResumeUploadResponse(
        id=str(created["id"]),
        user_id=user_id,
        filename=created["file"]["filename"],
        size=created["file"]["size"],
        content_type=created["file"]["content_type"],
        status=created["status"],
        is_active=created["is_active"],
        uploaded_at=created["uploaded_at"]
    )

    return ResponseModel(
        success=True,
        data=data,
        message="Resume uploaded successfully."
    )


@router.get("", response_model=ResponseModel[ResumeListResponse])
async def list_resumes(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """List all resumes uploaded by the authenticated student."""
    user_id = str(current_user["_id"])
    resumes = await service.get_user_resumes(user_id)

    items = [
        ResumeMetadataResponse(
            id=str(r["id"]),
            user_id=user_id,
            filename=r["file"]["filename"],
            size=r["file"]["size"],
            content_type=r["file"]["content_type"],
            status=r["status"],
            is_active=r["is_active"],
            analysis_version=r.get("analysis_version", "1.0"),
            uploaded_at=r["uploaded_at"],
            analyzed_at=r.get("analyzed_at"),
            has_analysis=bool(r.get("analysis"))
        )
        for r in resumes
    ]

    return ResponseModel(
        success=True,
        data=ResumeListResponse(items=items, total=len(items)),
        message="Resumes retrieved successfully."
    )


@router.get("/{resume_id}", response_model=ResponseModel[ResumeDetailResponse])
async def get_resume_detail(
    resume_id: str,
    bucket_name: Optional[str] = Query("resumes"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Get detailed information for a specific resume."""
    user_id = str(current_user["_id"])
    resume = await service.get_resume_by_id(resume_id, user_id)

    data = ResumeDetailResponse(
        id=str(resume["id"]),
        user_id=user_id,
        file=resume["file"],
        status=resume["status"],
        is_active=resume["is_active"],
        parsed_data=resume.get("parsed_data", {}),
        analysis=resume.get("analysis", {}),
        analysis_version=resume.get("analysis_version", "1.0"),
        error_message=resume.get("error_message"),
        uploaded_at=resume["uploaded_at"],
        analyzed_at=resume.get("analyzed_at"),
        updated_at=resume.get("updated_at", resume["uploaded_at"])
    )

    return ResponseModel(
        success=True,
        data=data,
        message="Resume detail retrieved successfully."
    )


@router.get("/{resume_id}/file")
async def download_resume_file(
    resume_id: str,
    bucket_name: Optional[str] = Query("resumes"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Download/stream the PDF resume binary stored in GridFS."""
    user_id = str(current_user["_id"])
    file_bytes, filename, content_type = await service.get_resume_file_stream(resume_id, user_id)

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )


@router.post("/{resume_id}/analyze", response_model=ResponseModel[ResumeAnalysisResponse])
async def analyze_resume(
    resume_id: str,
    bucket_name: Optional[str] = Query("resumes"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Trigger AI analysis for an uploaded resume."""
    user_id = str(current_user["_id"])
    resume = await service.analyze_resume(resume_id, user_id)

    data = ResumeAnalysisResponse(
        resume_id=str(resume["id"]),
        user_id=user_id,
        status=resume["status"],
        analysis_version=resume.get("analysis_version", "1.0"),
        analyzed_at=resume.get("analyzed_at"),
        analysis=resume.get("analysis", {})
    )

    return ResponseModel(
        success=True,
        data=data,
        message="Resume analysis completed successfully."
    )


@router.get("/{resume_id}/analysis", response_model=ResponseModel[ResumeAnalysisResponse])
async def get_resume_analysis(
    resume_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Fetch existing AI analysis for a resume."""
    user_id = str(current_user["_id"])
    result = await service.get_resume_analysis(resume_id, user_id)

    data = ResumeAnalysisResponse(
        resume_id=result["resume_id"],
        user_id=result["user_id"],
        status=result["status"],
        analysis_version=result["analysis_version"],
        analyzed_at=result.get("analyzed_at"),
        analysis=result["analysis"]
    )

    return ResponseModel(
        success=True,
        data=data,
        message="Resume analysis retrieved successfully."
    )


@router.patch("/{resume_id}/activate", response_model=ResponseModel[ResumeMetadataResponse])
async def activate_resume(
    resume_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Set the specified resume as the active resume for the student."""
    user_id = str(current_user["_id"])
    resume = await service.activate_resume(resume_id, user_id)

    data = ResumeMetadataResponse(
        id=str(resume["id"]),
        user_id=user_id,
        filename=resume["file"]["filename"],
        size=resume["file"]["size"],
        content_type=resume["file"]["content_type"],
        status=resume["status"],
        is_active=resume["is_active"],
        analysis_version=resume.get("analysis_version", "1.0"),
        uploaded_at=resume["uploaded_at"],
        analyzed_at=resume.get("analyzed_at"),
        has_analysis=bool(resume.get("analysis"))
    )

    return ResponseModel(
        success=True,
        data=data,
        message="Resume activated successfully."
    )


@router.delete("/{resume_id}", response_model=ResponseModel[Dict[str, bool]])
async def delete_resume(
    resume_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: ResumeService = Depends(get_resume_service)
):
    """Delete a resume document and its binary file from GridFS."""
    user_id = str(current_user["_id"])
    deleted = await service.delete_resume(resume_id, user_id)

    return ResponseModel(
        success=True,
        data={"deleted": deleted},
        message="Resume deleted successfully."
    )
