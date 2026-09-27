import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_db, get_current_user
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectFeaturedRequest,
    ProjectResponse,
    ProjectListResponse,
    ProjectSingleResponse,
    ProjectAnalysisResponse
)
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ProjectSingleResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new portfolio project for authenticated user."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    created = await service.create_project(user_id, project_in)
    return ProjectSingleResponse(
        success=True,
        message=f"Project '{created['title']}' created successfully.",
        data=created
    )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    include_archived: bool = Query(False, description="Include archived projects"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all projects belonging to the authenticated user."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    projects = await service.get_user_projects(user_id, include_archived=include_archived)
    return ProjectListResponse(
        success=True,
        total=len(projects),
        data=projects
    )


@router.get("/{project_id}", response_model=ProjectSingleResponse)
async def get_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch single project details by ID with ownership verification."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id, user_id)
    return ProjectSingleResponse(
        success=True,
        message="Project details retrieved successfully.",
        data=project
    )


@router.put("/{project_id}", response_model=ProjectSingleResponse)
async def update_project(
    project_id: str,
    project_in: ProjectUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update complete or partial project details."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    updated = await service.update_project(project_id, user_id, project_in)
    return ProjectSingleResponse(
        success=True,
        message="Project updated successfully.",
        data=updated
    )


@router.patch("/{project_id}", response_model=ProjectSingleResponse)
async def patch_project(
    project_id: str,
    project_in: ProjectUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Partially update project attributes."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    updated = await service.update_project(project_id, user_id, project_in)
    return ProjectSingleResponse(
        success=True,
        message="Project updated successfully.",
        data=updated
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    soft_delete: bool = Query(True, description="Soft delete status='archived' or permanent delete"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete or archive project with ownership validation."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    deleted = await service.delete_project(project_id, user_id, soft_delete=soft_delete)
    return {
        "success": True,
        "message": "Project removed successfully.",
        "data": {"project_id": project_id, "deleted": deleted}
    }


@router.patch("/{project_id}/featured", response_model=ProjectSingleResponse)
async def toggle_featured_project(
    project_id: str,
    req: ProjectFeaturedRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Mark or unmark project as featured."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    updated = await service.toggle_featured(project_id, user_id, req.is_featured)
    return ProjectSingleResponse(
        success=True,
        message="Project featured status updated.",
        data=updated
    )


@router.post("/{project_id}/analyze", response_model=ProjectSingleResponse)
async def analyze_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Trigger AI Project Intelligence analysis and AST code audit."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    analyzed = await service.analyze_project(project_id, user_id)
    return ProjectSingleResponse(
        success=True,
        message="Project analyzed successfully.",
        data=analyzed
    )


@router.get("/{project_id}/analysis", response_model=ProjectAnalysisResponse)
async def get_project_analysis(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Fetch stored AI Project Intelligence analysis report."""
    user_id = str(current_user["id"])
    service = ProjectService(db)
    analysis_payload = await service.get_project_analysis(project_id, user_id)
    return ProjectAnalysisResponse(
        success=True,
        message="Project AI analysis report retrieved.",
        data=analysis_payload
    )
