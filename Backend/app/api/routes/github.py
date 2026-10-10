import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, Query, status
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

# Swagger tag is defined centrally in app/api/routes/__init__.py
router = APIRouter()


def get_github_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> GitHubService:
    return GitHubService(db)


@router.post(
    "/connect",
    response_model=ResponseModel[GitHubConnectResponse],
    status_code=status.HTTP_200_OK,
)
async def connect_github(
    payload: GitHubConnectRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Connect a GitHub profile username to the authenticated student account."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    result = await service.connect_github(
        user_id,
        payload.github_username,
    )

    data = GitHubConnectResponse(
        user_id=user_id,
        github_username=result["github_username"],
        is_connected=True,
        profile=result.get("profile"),
        status="connected",
    )

    return ResponseModel(
        success=True,
        data=data,
        message=(
            f"GitHub account "
            f"'@{result['github_username']}' connected successfully."
        ),
    )


@router.get(
    "",
    response_model=ResponseModel[GitHubProfileResponse],
)
async def get_github_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Retrieve connected GitHub profile metadata, statistics, and sync status."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

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
        updated_at=profile.get("updated_at"),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub profile retrieved successfully.",
    )


@router.post(
    "/sync",
    response_model=ResponseModel[GitHubProfileResponse],
)
async def sync_github(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Synchronize GitHub profile and repositories from GitHub API."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

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
        updated_at=profile.get("updated_at"),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub profile synchronized successfully.",
    )


@router.get(
    "/repositories",
    response_model=ResponseModel[GitHubRepoListResponse],
)
async def get_github_repositories(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Retrieve paginated list of user's synchronized GitHub repositories."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    repos, total = await service.get_github_repositories(
        user_id,
        page=page,
        limit=limit,
    )

    items = [
        GitHubRepoItem(
            id=str(repo["id"]),
            repo_id=repo.get("repo_id"),
            name=repo.get("name", ""),
            full_name=repo.get(
                "full_name",
                repo.get("name", ""),
            ),
            description=repo.get("description"),
            html_url=repo.get("html_url"),
            language=repo.get("language"),
            languages=repo.get("languages", {}),
            stars=repo.get("stars", 0),
            forks=repo.get("forks", 0),
            topics=repo.get("topics", []),
            has_readme=repo.get("has_readme", False),
            is_fork=repo.get("is_fork", False),
            ast_score=repo.get("ast_score") or repo.get("quality_score", 0),
            quality_score=repo.get("quality_score") or repo.get("ast_score", 0),
            quality_tier=repo.get("quality_tier", "Active Project"),
            tags=repo.get(
                "topics",
                [repo["language"]]
                if repo.get("language")
                else [],
            ),
            created_at=repo.get("created_at"),
            updated_at=repo.get("updated_at"),
            pushed_at=repo.get("pushed_at"),
        )
        for repo in repos
    ]

    return ResponseModel(
        success=True,
        data=GitHubRepoListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
        message="GitHub repositories retrieved successfully.",
    )


@router.post(
    "/analyze",
    response_model=ResponseModel[GitHubAnalysisResponse],
)
async def analyze_github(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Trigger AI analysis for the connected GitHub profile."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    profile = await service.analyze_github(user_id)

    data = GitHubAnalysisResponse(
        user_id=user_id,
        github_username=profile["github_username"],
        analysis_version=profile.get(
            "analysis_version",
            "1.0",
        ),
        analyzed_at=profile.get("updated_at"),
        analysis=profile.get("analysis"),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub AI analysis completed successfully.",
    )


@router.get(
    "/analysis",
    response_model=ResponseModel[GitHubAnalysisResponse],
)
async def get_github_analysis(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Fetch stored AI analysis for connected GitHub profile."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    result = await service.get_github_analysis(user_id)

    data = GitHubAnalysisResponse(
        user_id=user_id,
        github_username=result["github_username"],
        analysis_version=result["analysis_version"],
        analyzed_at=result.get("analyzed_at"),
        analysis=result["analysis"],
    )

    return ResponseModel(
        success=True,
        data=data,
        message="GitHub AI analysis retrieved successfully.",
    )


@router.delete(
    "",
    response_model=ResponseModel[Dict[str, bool]],
)
async def disconnect_github(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: GitHubService = Depends(get_github_service),
):
    """Disconnect GitHub profile and delete stored repository metadata."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    deleted = await service.disconnect_github(user_id)

    return ResponseModel(
        success=True,
        data={"disconnected": deleted},
        message="GitHub profile disconnected successfully.",
    )