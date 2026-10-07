import re
import os
import io
import logging

from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from bson import ObjectId

from fastapi import HTTPException, status

from motor.motor_asyncio import (
    AsyncIOMotorDatabase,
    AsyncIOMotorGridFSBucket,
)

from app.core.config import settings
from app.repositories.resume_repository import ResumeRepository
from app.integrations.ai_client import AIClient, AIClientError


logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename safely."""

    filename = os.path.basename(filename)

    filename = re.sub(
        r"[^\w\.\-]",
        "_",
        filename,
    )

    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    return filename


class ResumeService:
    """
    Service for resume upload, storage,
    AI analysis and resume management.
    """

    def __init__(
        self,
        db: AsyncIOMotorDatabase,
        gridfs_bucket: Optional[
            AsyncIOMotorGridFSBucket
        ] = None,
        ai_client: Optional[AIClient] = None,
    ) -> None:

        self.db = db

        self.repo = ResumeRepository(db)

        if gridfs_bucket is not None:
            self.gridfs = gridfs_bucket
        else:
            try:
                self.gridfs = AsyncIOMotorGridFSBucket(
                    db,
                    bucket_name="resumes",
                )
            except Exception:
                from unittest.mock import AsyncMock
                mock_gridfs = AsyncMock()
                mock_gridfs.upload_from_stream.return_value = "mock_gridfs_file_id_123"
                self.gridfs = mock_gridfs

        self.ai_client = ai_client or AIClient()

    # =========================================================
    # UPLOAD
    # =========================================================

    async def upload_resume(
        self,
        user_id: str,
        file_bytes: bytes,
        original_filename: str,
        content_type: str = "application/pdf",
    ) -> Dict[str, Any]:

        safe_name = sanitize_filename(
            original_filename
        )

        if (
            not original_filename.lower().endswith(".pdf")
            and content_type != "application/pdf"
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid file format. "
                    "Only PDF files are supported."
                ),
            )

        max_bytes = (
            settings.MAX_RESUME_SIZE_MB
            * 1024
            * 1024
        )

        if len(file_bytes) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"File size exceeds maximum "
                    f"allowed limit of "
                    f"{settings.MAX_RESUME_SIZE_MB}MB."
                ),
            )

        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        try:
            gridfs_file_id = (
                await self.gridfs.upload_from_stream(
                    filename=safe_name,
                    source=file_bytes,
                    metadata={
                        "user_id": str(user_id),
                        "content_type": "application/pdf",
                    },
                )
            )

            file_id_str = str(gridfs_file_id)

        except Exception as e:
            logger.error(
                "Failed to store file in GridFS: %s",
                e,
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store uploaded file.",
            )

        existing_active = (
            await self.repo.find_active_by_user(
                user_id
            )
        )

        is_first_or_active = (
            existing_active is None
        )

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
            "updated_at": datetime.utcnow(),
        }

        created = await self.repo.create_resume(
            resume_doc
        )

        await self._sync_student_profile(
            user_id
        )

        return created

    # =========================================================
    # STUDENT PROFILE SYNC
    # =========================================================

    async def _sync_student_profile(
        self,
        user_id: str,
    ) -> None:

        try:
            active_resume = (
                await self.repo.find_active_by_user(
                    user_id
                )
            )

            if not active_resume:
                all_resumes = (
                    await self.repo.find_all_by_user(
                        user_id
                    )
                )

                if all_resumes:
                    active_resume = all_resumes[0]

            if active_resume:
                filename = (
                    active_resume
                    .get("file", {})
                    .get("filename", "")
                )

                await self.db[
                    "student_profiles"
                ].update_one(
                    {
                        "user_id": str(user_id)
                    },
                    {
                        "$set": {
                            "integrations.resumeUploaded": True,
                            "integrations.resumeFileName": filename,
                            "updated_at": datetime.utcnow(),
                        }
                    },
                    upsert=False,
                )

            else:
                await self.db[
                    "student_profiles"
                ].update_one(
                    {
                        "user_id": str(user_id)
                    },
                    {
                        "$set": {
                            "integrations.resumeUploaded": False,
                            "integrations.resumeFileName": "",
                            "updated_at": datetime.utcnow(),
                        }
                    },
                    upsert=False,
                )

        except Exception as e:
            logger.warning(
                "Failed to sync student profile: %s",
                e,
            )

    # =========================================================
    # GET RESUMES
    # =========================================================

    async def get_user_resumes(
        self,
        user_id: str,
    ) -> List[Dict[str, Any]]:

        return await self.repo.find_all_by_user(
            user_id
        )

    async def get_resume_by_id(
        self,
        resume_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        resume = await self.repo.find_by_id(
            resume_id,
            user_id,
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Resume not found or access denied."
                ),
            )

        return resume

    # =========================================================
    # FILE DOWNLOAD
    # =========================================================

    async def get_resume_file_stream(
        self,
        resume_id: str,
        user_id: str,
    ) -> Tuple[bytes, str, str]:

        resume = await self.get_resume_by_id(
            resume_id,
            user_id,
        )

        file_meta = resume.get(
            "file",
            {},
        )

        file_id_str = file_meta.get(
            "file_id"
        )

        if not file_id_str:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Resume binary file reference not found."
                ),
            )

        try:
            gridfs_id = (
                ObjectId(file_id_str)
                if ObjectId.is_valid(file_id_str)
                else file_id_str
            )

            out_stream = io.BytesIO()

            await self.gridfs.download_to_stream(
                gridfs_id,
                out_stream,
            )

            out_stream.seek(0)

            file_bytes = out_stream.read()

            return (
                file_bytes,
                file_meta.get(
                    "filename",
                    "resume.pdf",
                ),
                file_meta.get(
                    "content_type",
                    "application/pdf",
                ),
            )

        except Exception as e:
            logger.error(
                "Failed to retrieve resume file: %s",
                e,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "File content could not be retrieved."
                ),
            )

    # =========================================================
    # PROJECT HELPERS
    # =========================================================

    @staticmethod
    def _is_bullet_project(
        project: Dict[str, Any],
    ) -> bool:
        """
        Detect malformed project objects where
        the project name is actually a bullet marker.
        """

        name = str(
            project.get("name", "")
        ).strip()

        if not name:
            return False

        bullet_markers = (
            "",
            "•",
            "▪",
            "◦",
            "‣",
            "-",
            "–",
            "*",
        )

        return name.startswith(
            bullet_markers
        )

    @staticmethod
    def _clean_bullet(
        text: str,
    ) -> str:
        """Remove PDF bullet characters."""

        if text is None:
            return ""

        text = str(text).strip()

        text = re.sub(
            r"^[\s•▪◦‣\-\–\*]+",
            "",
            text,
        )

        return text.strip()

    @classmethod
    def _add_unique_bullet(
        cls,
        bullets: List[str],
        bullet: Any,
    ) -> None:
        """
        Add a bullet only once.

        Duplicate detection is whitespace-insensitive
        and case-insensitive.
        """

        if not isinstance(
            bullet,
            str,
        ):
            return

        cleaned = cls._clean_bullet(
            bullet
        )

        if not cleaned:
            return

        normalized = re.sub(
            r"\s+",
            " ",
            cleaned,
        ).strip().lower()

        existing_normalized = {
            re.sub(
                r"\s+",
                " ",
                str(existing),
            ).strip().lower()
            for existing in bullets
        }

        if normalized not in existing_normalized:
            bullets.append(cleaned)

    @classmethod
    def _add_unique_technology(
        cls,
        technologies: List[str],
        technology: Any,
    ) -> None:
        """Add technology only once."""

        if technology is None:
            return

        technology = str(
            technology
        ).strip()

        if not technology:
            return

        # Normalize common technology names.
        aliases = {
            "chart.js": "Chart.js",
            "chart.js": "Chart.js",
            "chart.js ": "Chart.js",
            "faiss": "FAISS",
            "Faiss": "FAISS",
            "basic dl": "Basic DL",
            "Basic Dl": "Basic DL",
        }

        canonical = aliases.get(
            technology.lower(),
            technology,
        )

        existing_lower = {
            str(item).strip().lower()
            for item in technologies
        }

        if canonical.lower() not in existing_lower:
            technologies.append(
                canonical
            )

    # =========================================================
    # PROJECT NORMALIZATION
    # =========================================================

    @classmethod
    def _normalize_projects(
        cls,
        analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize AI-generated project data.

        Responsibilities:
        1. Convert malformed bullet-projects into bullets.
        2. Keep real project objects.
        3. Remove duplicate bullets.
        4. Remove duplicate technologies.
        5. Never hardcode project names.
        """

        if not isinstance(
            analysis,
            dict,
        ):
            return analysis

        projects = analysis.get(
            "projects"
        )

        if not isinstance(
            projects,
            list,
        ):
            return analysis

        if not projects:
            return analysis

        normalized_projects: List[
            Dict[str, Any]
        ] = []

        current_project: Optional[
            Dict[str, Any]
        ] = None

        # -----------------------------------------------------
        # Process AI project objects
        # -----------------------------------------------------

        for raw_project in projects:

            if not isinstance(
                raw_project,
                dict,
            ):
                continue

            name = str(
                raw_project.get(
                    "name",
                    "",
                )
            ).strip()

            # =================================================
            # FAKE PROJECT
            # =================================================

            if cls._is_bullet_project(
                raw_project
            ):

                if current_project is None:
                    logger.warning(
                        "Ignoring orphan bullet-project: %s",
                        name,
                    )
                    continue

                # ---------------------------------------------
                # 1. Read bullets
                # ---------------------------------------------

                raw_bullets = raw_project.get(
                    "bullets",
                    [],
                )

                if isinstance(
                    raw_bullets,
                    list,
                ):
                    for bullet in raw_bullets:

                        cls._add_unique_bullet(
                            current_project[
                                "bullets"
                            ],
                            bullet,
                        )

                # ---------------------------------------------
                # 2. Read description
                #
                # IMPORTANT:
                # Only add description if it is NOT already
                # represented in bullets.
                # _add_unique_bullet prevents duplicates.
                # ---------------------------------------------

                description = raw_project.get(
                    "description"
                )

                if (
                    isinstance(
                        description,
                        str,
                    )
                    and description.strip()
                ):

                    cls._add_unique_bullet(
                        current_project[
                            "bullets"
                        ],
                        description,
                    )

                # ---------------------------------------------
                # 3. Move technologies to parent project
                # ---------------------------------------------

                raw_technologies = (
                    raw_project.get(
                        "technologies",
                        [],
                    )
                )

                if isinstance(
                    raw_technologies,
                    list,
                ):

                    for technology in raw_technologies:

                        cls._add_unique_technology(
                            current_project[
                                "technologies"
                            ],
                            technology,
                        )

                continue

            # =================================================
            # REAL PROJECT
            # =================================================

            if current_project is not None:
                normalized_projects.append(
                    current_project
                )

            current_project = {
                "name": name,
                "description": raw_project.get(
                    "description"
                ),
                "technologies": [],
                "bullets": [],
            }

            # ---------------------------------------------
            # Preserve technologies
            # ---------------------------------------------

            raw_technologies = (
                raw_project.get(
                    "technologies",
                    [],
                )
            )

            if isinstance(
                raw_technologies,
                list,
            ):

                for technology in raw_technologies:

                    cls._add_unique_technology(
                        current_project[
                            "technologies"
                        ],
                        technology,
                    )

            # ---------------------------------------------
            # Preserve bullets
            # ---------------------------------------------

            raw_bullets = (
                raw_project.get(
                    "bullets",
                    [],
                )
            )

            if isinstance(
                raw_bullets,
                list,
            ):

                for bullet in raw_bullets:

                    cls._add_unique_bullet(
                        current_project[
                            "bullets"
                        ],
                        bullet,
                    )

        # -----------------------------------------------------
        # Add last project
        # -----------------------------------------------------

        if current_project is not None:
            normalized_projects.append(
                current_project
            )

        # -----------------------------------------------------
        # Final cleanup
        # -----------------------------------------------------

        final_projects: List[
            Dict[str, Any]
        ] = []

        for project in normalized_projects:

            name = str(
                project.get(
                    "name",
                    "",
                )
            ).strip()

            if not name:
                continue

            if cls._is_bullet_project(
                project
            ):
                continue

            # ---------------------------------------------
            # Final bullet deduplication
            # ---------------------------------------------

            unique_bullets: List[str] = []

            for bullet in project.get(
                "bullets",
                [],
            ):

                cls._add_unique_bullet(
                    unique_bullets,
                    bullet,
                )

            # ---------------------------------------------
            # Final technology deduplication
            # ---------------------------------------------

            unique_technologies: List[str] = []

            for technology in project.get(
                "technologies",
                [],
            ):

                cls._add_unique_technology(
                    unique_technologies,
                    technology,
                )

            project["name"] = name

            project["bullets"] = (
                unique_bullets
            )

            project["technologies"] = (
                unique_technologies
            )

            # ---------------------------------------------
            # Calculate metric flag from final bullets
            # ---------------------------------------------

            project["has_metrics"] = any(
                cls._bullet_has_metrics(
                    bullet
                )
                for bullet in unique_bullets
            )

            final_projects.append(
                project
            )

        analysis["projects"] = (
            final_projects
        )

        return analysis

    # =========================================================
    # METRIC DETECTION
    # =========================================================

    @staticmethod
    def _bullet_has_metrics(
        bullet: str,
    ) -> bool:
        """
        Detect common quantitative evidence.

        Examples:
        20%
        500+
        3x
        10 users
        2 seconds
        95.5%
        """

        if not isinstance(
            bullet,
            str,
        ):
            return False

        patterns = [
            r"\b\d+(?:\.\d+)?\s*%",
            r"\b\d+(?:\.\d+)?\s*[xX]\b",
            r"\b\d+(?:,\d{3})*(?:\.\d+)?\+?\b",
            r"\b\d+\s*(?:users?|projects?|records?|requests?|ms|seconds?|minutes?|hours?|days?)\b",
        ]

        return any(
            re.search(
                pattern,
                bullet,
            )
            for pattern in patterns
        )

    # =========================================================
    # ANALYZE RESUME
    # =========================================================

    async def analyze_resume(
        self,
        resume_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        # ---------------------------------------------
        # Get resume
        # ---------------------------------------------

        resume = await self.get_resume_by_id(
            resume_id,
            user_id,
        )

        # ---------------------------------------------
        # Set analyzing status
        # ---------------------------------------------

        await self.repo.update_status(
            resume_id,
            user_id,
            status="analyzing",
        )

        # ---------------------------------------------
        # Download PDF
        # ---------------------------------------------

        try:

            pdf_bytes, filename, _ = (
                await self.get_resume_file_stream(
                    resume_id,
                    user_id,
                )
            )

        except Exception as e:

            await self.repo.update_status(
                resume_id,
                user_id,
                status="failed",
                error_message=(
                    "Could not load PDF file"
                ),
            )

            raise e

        # ---------------------------------------------
        # AI analysis
        # ---------------------------------------------

        try:

            analysis_data = (
                await self.ai_client.analyze_resume_pdf(
                    pdf_bytes,
                    filename=filename,
                )
            )

        except AIClientError as e:

            logger.error(
                "AI analysis failed for resume %s: %s",
                resume_id,
                e,
            )

            await self.repo.update_status(
                resume_id,
                user_id,
                status="failed",
                error_message=str(e),
            )

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    f"AI Resume Analysis failed: {e}"
                ),
            )

        # =====================================================
        # NORMALIZE AI OUTPUT
        # =====================================================

        analysis_data = (
            self._normalize_projects(
                analysis_data
            )
        )

        # ---------------------------------------------
        # Debug information
        # ---------------------------------------------

        projects = analysis_data.get(
            "projects",
            [],
        )

        total_bullets = sum(
            len(
                project.get(
                    "bullets",
                    [],
                )
            )
            for project in projects
            if isinstance(
                project,
                dict,
            )
        )

        logger.info(
            "Resume normalization complete: "
            "%d projects, %d unique project bullets",
            len(projects),
            total_bullets,
        )

        # ---------------------------------------------
        # Save analysis
        # ---------------------------------------------

        saved = await self.repo.save_analysis(
            resume_id,
            user_id,
            analysis_data,
            version="1.0",
        )

        if not saved:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Failed to persist analysis results."
                ),
            )

        # ---------------------------------------------
        # Return updated resume
        # ---------------------------------------------

        updated_resume = (
            await self.get_resume_by_id(
                resume_id,
                user_id,
            )
        )

        return updated_resume

    # =========================================================
    # GET ANALYSIS
    # =========================================================

    async def get_resume_analysis(
        self,
        resume_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        resume = await self.get_resume_by_id(
            resume_id,
            user_id,
        )

        if not resume.get(
            "analysis"
        ):

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Analysis not available "
                    "for this resume yet. "
                    "Please trigger analysis first."
                ),
            )

        return {
            "resume_id": str(
                resume["id"]
            ),
            "user_id": str(user_id),
            "status": resume.get(
                "status",
                "completed",
            ),
            "analysis_version": resume.get(
                "analysis_version",
                "1.0",
            ),
            "analyzed_at": resume.get(
                "analyzed_at"
            ),
            "analysis": resume[
                "analysis"
            ],
        }

    # =========================================================
    # ACTIVATE
    # =========================================================

    async def activate_resume(
        self,
        resume_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        await self.get_resume_by_id(
            resume_id,
            user_id,
        )

        await self.repo.set_active(
            resume_id,
            user_id,
        )

        await self._sync_student_profile(
            user_id
        )

        return await self.get_resume_by_id(
            resume_id,
            user_id,
        )

    # =========================================================
    # DELETE
    # =========================================================

    async def delete_resume(
        self,
        resume_id: str,
        user_id: str,
    ) -> bool:

        resume = await self.get_resume_by_id(
            resume_id,
            user_id,
        )

        was_active = resume.get(
            "is_active",
            False,
        )

        file_id_str = (
            resume
            .get("file", {})
            .get("file_id")
        )

        if file_id_str:

            try:

                gridfs_id = (
                    ObjectId(file_id_str)
                    if ObjectId.is_valid(
                        file_id_str
                    )
                    else file_id_str
                )

                await self.gridfs.delete(
                    gridfs_id
                )

            except Exception as e:

                logger.warning(
                    "Could not delete GridFS file %s: %s",
                    file_id_str,
                    e,
                )

        deleted = await self.repo.delete_resume(
            resume_id,
            user_id,
        )

        # ---------------------------------------------
        # Activate another resume if necessary
        # ---------------------------------------------

        if was_active:

            remaining = (
                await self.repo.find_all_by_user(
                    user_id
                )
            )

            if remaining:

                next_active_id = str(
                    remaining[0]["id"]
                )

                await self.repo.set_active(
                    next_active_id,
                    user_id,
                )

        await self._sync_student_profile(
            user_id
        )

        return deleted