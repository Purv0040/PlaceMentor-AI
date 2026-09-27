import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, get_db
from app.services.github_service import GitHubService
from app.schemas.common import ResponseModel
from app.schemas.github import (
    GitHubConnectRequest,
    GitHubConnectResponse,
    GitHubProfileResponse,
    GitHubRepoListResponse,
    GitHubRepoItem,
    GitHubAnalysisResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["GitHub"])


def get_github_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> GitHubService:
    return GitHubService(db)


@router.post("/connect", response_model=ResponseModel[GitHubConnectResponse], status_code=status.HTTP_200_OK)
async def connect_github(
    payload: GitHubConnectRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Connect a GitHub profile username to the authenticated student account."""
    user_id = str(current_user["_id"])
    result = await service.connect_github(user_id, payload.github_username)

    data = GitHubConnectResponse(
        user_id=user_id,
        github_username=result["github_username"],
        is_connected=True,
        profile=result.get("profile"),
        status="connected"
    )

    return ResponseModel(
        success=True,
        data=data,
        message=f"GitHub account '@{result['github_username']}' connected successfully."
    )


@router.get("", response_model=ResponseModel[GitHubProfileResponse])
async def get_github_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Retrieve connected GitHub profile metadata, statistics, and sync status."""
    user_id = str(current_user["_id"])
    profile = await service.get_github_profile(user_id)

    data = GitHubProfileResponse(
        id=str(profile["id"]),
        user_id=user_id,
        github_username=profile["github_username"],
        is_connected=True,
        profile=profile.get("profile"),
        statistics=profile.get("statistics"),
        sync=profile.get("sync", {}),
        analysis_version=profile.get("analysis_version", "1.0"),
        has_analysis=bool(profile.get("analysis")),
        created_at=profile.get("created_at"),
        updated_at=profile.get("updated_at")
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub profile retrieved successfully."
    )


@router.post("/sync", response_model=ResponseModel[GitHubProfileResponse])
async def sync_github(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Synchronize GitHub profile and repositories from GitHub API."""
    user_id = str(current_user["_id"])
    profile = await service.sync_github(user_id)

    data = GitHubProfileResponse(
        id=str(profile["id"]),
        user_id=user_id,
        github_username=profile["github_username"],
        is_connected=True,
        profile=profile.get("profile"),
        statistics=profile.get("statistics"),
        sync=profile.get("sync", {}),
        analysis_version=profile.get("analysis_version", "1.0"),
        has_analysis=bool(profile.get("analysis")),
        created_at=profile.get("created_at"),
        updated_at=profile.get("updated_at")
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub profile synchronized successfully."
    )


@router.get("/repositories", response_model=ResponseModel[GitHubRepoListResponse])
async def get_github_repositories(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Retrieve paginated list of user's synchronized GitHub repositories."""
    user_id = str(current_user["_id"])
    repos, total = await service.get_github_repositories(user_id, page=page, limit=limit)

    items = [
        GitHubRepoItem(
            id=str(r["id"]),
            repo_id=r.get("repo_id"),
            name=r.get("name", ""),
            full_name=r.get("full_name", r.get("name", "")),
            description=r.get("description"),
            html_url=r.get("html_url"),
            language=r.get("language"),
            languages=r.get("languages", {}),
            stars=r.get("stars", 0),
            forks=r.get("forks", 0),
            topics=r.get("topics", []),
            has_readme=r.get("has_readme", False),
            is_fork=r.get("is_fork", False),
            size=r.get("size", 0),
            ast_score=85,
            qualityTier="Verified",
            tags=r.get("topics", [r["language"]] if r.get("language") else []),
            created_at=r.get("created_at"),
            updated_at=r.get("updated_at"),
            pushed_at=r.get("pushed_at")
        )
        for r in repos
    ]

    return ResponseModel(
        success=True,
        data=GitHubRepoListResponse(items=items, total=total, page=page, limit=limit),
        message="GitHub repositories retrieved successfully."
    )


@router.post("/analyze", response_model=ResponseModel[GitHubAnalysisResponse])
async def analyze_github(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Trigger AI analysis for the connected GitHub profile."""
    user_id = str(current_user["_id"])
    profile = await service.analyze_github(user_id)

    data = GitHubAnalysisResponse(
        user_id=user_id,
        github_username=profile["github_username"],
        analysis_version=profile.get("analysis_version", "1.0"),
        analyzed_at=profile.get("updated_at"),
        analysis=profile.get("analysis")
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub AI analysis completed successfully."
    )


@router.get("/analysis", response_model=ResponseModel[GitHubAnalysisResponse])
async def get_github_analysis(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Fetch stored AI analysis for connected GitHub profile."""
    user_id = str(current_user["_id"])
    result = await service.get_github_analysis(user_id)

    data = GitHubAnalysisResponse(
        user_id=user_id,
        github_username=result["github_username"],
        analysis_version=result["analysis_version"],
        analyzed_at=result.get("analyzed_at"),
        analysis=result["analysis"]
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub AI analysis retrieved successfully."
    )


@router.delete("", response_model=ResponseModel[Dict[str, bool]])
async def disconnect_github(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service)
):
    """Disconnect GitHub profile and delete stored repository metadata for authenticated user."""
    user_id = str(current_user["_id"])
    deleted = await service.disconnect_github(user_id)

    return ResponseModel(
        success=True,
        data={"disconnected": deleted},
        message="GitHub profile disconnected successfully."
    )
