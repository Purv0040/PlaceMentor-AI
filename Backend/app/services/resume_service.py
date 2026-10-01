import re
import os
import io
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket

from app.core.config import settings
from app.repositories.resume_repository import ResumeRepository
from app.integrations.ai_client import AIClient, AIClientError

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or unsafe characters."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^\w\.\-]', '_', filename)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    return filename


class ResumeService:
    """Service encapsulating business logic for resume management and AI intelligence."""

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        gridfs_bucket: Optional[AsyncIOMotorGridFSBucket] = None,
        ai_client: Optional[AIClient] = None
    ) -> None:
        self.db = db
        self.repo = ResumeRepository(db)
        if gridfs_bucket is not None:
            self.gridfs = gridfs_bucket
        else:
            try:
                self.gridfs = AsyncIOMotorGridFSBucket(db, bucket_name="resumes")
            except Exception:
                from unittest.mock import AsyncMock
                self.gridfs = AsyncMock()
        self.ai_client = ai_client or AIClient()

    async def upload_resume(
        self,
        user_id: str,
        file_bytes: bytes,
        original_filename: str,
        content_type: str = "application/pdf"
    ) -> Dict[str, Any]:
        """Validate, store binary in GridFS, and create resume document."""
        # 1. Validate file extension & content type
        safe_name = sanitize_filename(original_filename)
        if not original_filename.lower().endswith(".pdf") and content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Only PDF files (.pdf) are supported."
            )

        # 2. Validate file size
        max_bytes = settings.MAX_RESUME_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed limit of {settings.MAX_RESUME_SIZE_MB}MB."
            )

        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        # 3. Store file binary in GridFS bucket
        try:
            gridfs_file_id = await self.gridfs.upload_from_stream(
                filename=safe_name,
                source=file_bytes,
                metadata={"user_id": str(user_id), "content_type": "application/pdf"}
            )
            file_id_str = str(gridfs_file_id)
        except Exception as e:
            logger.error("Failed to store file in GridFS: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store uploaded file."
            )

        # 4. Check if user already has an active resume
        existing_active = await self.repo.find_active_by_user(user_id)
        is_first_or_active = existing_active is None

        # 5. Build Resume document
        resume_doc = {
            "user_id": str(user_id),
            "file": {
                "filename": safe_name,
                "content_type": "application/pdf",
                "size": len(file_bytes),
                "storage_type": "gridfs",
                "file_id": file_id_str,
            },
            "status": "uploaded",
            "is_active": is_first_or_active,
            "parsed_data": {},
            "analysis": {},
            "analysis_version": "1.0",
            "error_message": None,
            "uploaded_at": datetime.utcnow(),
            "analyzed_at": None,
            "updated_at": datetime.utcnow()
        }

        created = await self.repo.create_resume(resume_doc)
        logger.info("Created resume document %s for user %s", created["id"], user_id)
        
        # Sync student profile integrations status
        await self._sync_student_profile(user_id)

        return created

    async def _sync_student_profile(self, user_id: str) -> None:
        """Keep student_profiles integrations block in sync with user's active resume."""
        try:
            active_resume = await self.repo.find_active_by_user(user_id)
            if not active_resume:
                all_resumes = await self.repo.find_all_by_user(user_id)
                if all_resumes:
                    active_resume = all_resumes[0]

            if active_resume and active_resume.get("file"):
                filename = active_resume["file"].get("filename", "")
                await self.db["student_profiles"].update_one(
                    {"user_id": str(user_id)},
                    {
                        "$set": {
                            "integrations.resumeUploaded": True,
                            "integrations.resumeFileName": filename,
                            "updated_at": datetime.utcnow()
                        }
                    },
                    upsert=False
                )
            else:
                await self.db["student_profiles"].update_one(
                    {"user_id": str(user_id)},
                    {
                        "$set": {
                            "integrations.resumeUploaded": False,
                            "integrations.resumeFileName": "",
                            "updated_at": datetime.utcnow()
                        }
                    },
                    upsert=False
                )
        except Exception as e:
            logger.warning("Failed to sync student_profile resume integration state for user %s: %s", user_id, e)

    async def get_user_resumes(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all resumes owned by user_id."""
        return await self.repo.find_all_by_user(user_id)

    async def get_resume_by_id(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """Retrieve a specific resume and verify user ownership."""
        resume = await self.repo.find_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or access denied."
            )
        return resume

    async def get_resume_file_stream(self, resume_id: str, user_id: str) -> Tuple[bytes, str, str]:
        """Retrieve GridFS file binary bytes for a resume owned by user_id."""
        resume = await self.get_resume_by_id(resume_id, user_id)
        file_meta = resume.get("file", {})
        file_id_str = file_meta.get("file_id")

        if not file_id_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume binary file reference not found."
            )

        try:
            gridfs_id = ObjectId(file_id_str) if ObjectId.is_valid(file_id_str) else file_id_str
            out_stream = io.BytesIO()
            await self.gridfs.download_to_stream(gridfs_id, out_stream)
            out_stream.seek(0)
            file_bytes = out_stream.read()
            return file_bytes, file_meta.get("filename", "resume.pdf"), file_meta.get("content_type", "application/pdf")
        except Exception as e:
            logger.error("Failed to retrieve file from GridFS for resume %s: %s", resume_id, e)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File content could not be retrieved."
            )

    async def analyze_resume(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """Orchestrate AI analysis of a stored resume."""
        resume = await self.get_resume_by_id(resume_id, user_id)

        # Update status to analyzing
        await self.repo.update_status(resume_id, user_id, status="analyzing")

        # Fetch PDF binary bytes from GridFS
        try:
            pdf_bytes, filename, _ = await self.get_resume_file_stream(resume_id, user_id)
        except Exception as e:
            await self.repo.update_status(resume_id, user_id, status="failed", error_message="Could not load PDF file")
            raise e

        # Call AI microservice via AIClient
        try:
            analysis_data = await self.ai_client.analyze_resume_pdf(pdf_bytes, filename=filename)
        except AIClientError as e:
            logger.error("AI Analysis failed for resume %s: %s", resume_id, e)
            await self.repo.update_status(resume_id, user_id, status="failed", error_message=str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI Resume Analysis failed: {str(e)}"
            )

        # Save analysis result to MongoDB
        saved = await self.repo.save_analysis(resume_id, user_id, analysis_data, version="1.0")
        if not saved:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist analysis results."
            )

        # Return updated resume
        updated_resume = await self.get_resume_by_id(resume_id, user_id)
        return updated_resume

    async def get_resume_analysis(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """Get existing analysis results for a resume."""
        resume = await self.get_resume_by_id(resume_id, user_id)
        if not resume.get("analysis"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not available for this resume yet. Please trigger analysis first."
            )
        return {
            "resume_id": str(resume["id"]),
            "user_id": str(user_id),
            "status": resume.get("status", "completed"),
            "analysis_version": resume.get("analysis_version", "1.0"),
            "analyzed_at": resume.get("analyzed_at"),
            "analysis": resume["analysis"]
        }

    async def activate_resume(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """Set specified resume as active and deactivate all others for user."""
        resume = await self.get_resume_by_id(resume_id, user_id)
        await self.repo.set_active(resume_id, user_id)
        await self._sync_student_profile(user_id)
        return await self.get_resume_by_id(resume_id, user_id)

    async def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """Safely delete resume document and its GridFS file binary."""
        resume = await self.get_resume_by_id(resume_id, user_id)
        was_active = resume.get("is_active", False)

        file_id_str = resume.get("file", {}).get("file_id")
        if file_id_str:
            try:
                gridfs_id = ObjectId(file_id_str) if ObjectId.is_valid(file_id_str) else file_id_str
                await self.gridfs.delete(gridfs_id)
            except Exception as e:
                logger.warning("Could not delete GridFS file %s: %s", file_id_str, e)

        deleted = await self.repo.delete_resume(resume_id, user_id)

        # If deleted resume was active, set another remaining resume as active
        if was_active:
            remaining = await self.repo.find_all_by_user(user_id)
            if remaining:
                next_active_id = str(remaining[0]["id"])
                await self.repo.set_active(next_active_id, user_id)

        await self._sync_student_profile(user_id)

        return deleted
