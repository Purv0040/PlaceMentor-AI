import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, get_db
from app.services.leetcode_service import LeetCodeService
from app.schemas.common import ResponseModel
from app.schemas.leetcode import (
    LeetCodeConnectRequest,
    LeetCodeConnectResponse,
    LeetCodeProfileResponse,
    LeetCodeStatisticsResponse,
    LeetCodeActivityResponse,
    LeetCodeAnalysisResponse,
    DailyPracticePlanResponse,
    ActivityTrendResponse,
    FocusAreaTopic,
    ReadinessBreakdown,
)

logger = logging.getLogger(__name__)

# Swagger tag is defined in app/api/routes/__init__.py
router = APIRouter()


def get_leetcode_service(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> LeetCodeService:
    return LeetCodeService(db)


@router.post(
    "/connect",
    response_model=ResponseModel[LeetCodeConnectResponse],
    status_code=status.HTTP_200_OK,
)
async def connect_leetcode(
    payload: LeetCodeConnectRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Connect a LeetCode username to the authenticated student account."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    result = await service.connect_leetcode(
        user_id,
        payload.username,
    )

    data = LeetCodeConnectResponse(
        user_id=user_id,
        leetcode_username=result["leetcode_username"],
        is_connected=True,
        profile=result.get("profile"),
        status="connected",
    )

    return ResponseModel(
        success=True,
        data=data,
        message=(
            f"LeetCode account "
            f"'@{result['leetcode_username']}' connected successfully."
        ),
    )


@router.get(
    "",
    response_model=ResponseModel[LeetCodeProfileResponse],
)
async def get_leetcode_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Retrieve connected LeetCode profile metadata, statistics, and sync status."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    profile = await service.get_leetcode_profile(user_id)

    data = LeetCodeProfileResponse(
        id=str(profile.get("id") or profile.get("_id") or ""),
        user_id=user_id,
        leetcode_username=profile["leetcode_username"],
        is_connected=True,
        profile=profile.get("profile"),
        statistics=profile.get("statistics"),
        contest=profile.get("contest"),
        topic_statistics=profile.get("topic_statistics", []),
        recent_activity=profile.get("recent_activity", []),
        sync=profile.get("sync", {}),
        analysis_version=profile.get("analysis_version", "1.0"),
        has_analysis=bool(profile.get("analysis")),
        daily_plan=profile.get("daily_plan"),
        focus_areas=profile.get("focus_areas"),
        readiness_breakdown=profile.get("readiness_breakdown"),
        activity_history=profile.get("activity_history"),
        created_at=profile.get("created_at"),
        updated_at=profile.get("updated_at"),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="LeetCode profile retrieved successfully.",
    )


@router.delete(
    "",
    response_model=ResponseModel[Dict[str, bool]],
)
async def disconnect_leetcode(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Disconnect LeetCode profile and delete stored data for authenticated user."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    deleted = await service.disconnect_leetcode(user_id)

    return ResponseModel(
        success=True,
        data={"disconnected": deleted},
        message="LeetCode profile disconnected successfully.",
    )


@router.post(
    "/sync",
    response_model=ResponseModel[LeetCodeProfileResponse],
)
async def sync_leetcode(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Synchronize LeetCode profile and problem statistics from LeetCode provider."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    profile = await service.sync_leetcode(user_id)

    data = LeetCodeProfileResponse(
        id=str(profile.get("id") or profile.get("_id") or ""),
        user_id=user_id,
        leetcode_username=profile["leetcode_username"],
        is_connected=True,
        profile=profile.get("profile"),
        statistics=profile.get("statistics"),
        contest=profile.get("contest"),
        topic_statistics=profile.get("topic_statistics", []),
        recent_activity=profile.get("recent_activity", []),
        sync=profile.get("sync", {}),
        analysis_version=profile.get("analysis_version", "1.0"),
        has_analysis=bool(profile.get("analysis")),
        daily_plan=profile.get("daily_plan"),
        focus_areas=profile.get("focus_areas"),
        readiness_breakdown=profile.get("readiness_breakdown"),
        activity_history=profile.get("activity_history"),
        created_at=profile.get("created_at"),
        updated_at=profile.get("updated_at"),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="LeetCode profile synchronized successfully.",
    )


@router.get(
    "/daily-plan",
    response_model=ResponseModel[DailyPracticePlanResponse],
)
async def get_daily_practice_plan(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Retrieve today's DSA practice plan with recommended problems and completion status."""

    user_id = str(current_user.get("id") or current_user.get("_id"))
    plan = await service.get_daily_practice_plan(user_id)

    return ResponseModel(
        success=True,
        data=DailyPracticePlanResponse(**plan),
        message="Today's DSA practice plan retrieved successfully.",
    )


@router.post(
    "/daily-plan/{task_id}/toggle",
    response_model=ResponseModel[DailyPracticePlanResponse],
)
async def toggle_daily_practice_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Toggle completion status of a daily DSA task in the practice plan."""

    user_id = str(current_user.get("id") or current_user.get("_id"))
    updated_plan = await service.toggle_practice_task(user_id, task_id)

    return ResponseModel(
        success=True,
        data=DailyPracticePlanResponse(**updated_plan),
        message="Practice task status updated successfully.",
    )


@router.get(
    "/history",
    response_model=ResponseModel[ActivityTrendResponse],
)
async def get_activity_history(
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Retrieve historical daily problem solving activity and contest rating history (7, 30, or 90 days)."""

    user_id = str(current_user.get("id") or current_user.get("_id"))
    history = await service.get_activity_history(user_id, days=days)

    return ResponseModel(
        success=True,
        data=ActivityTrendResponse(**history),
        message=f"LeetCode activity trend for past {history.get('days', days)} days retrieved successfully.",
    )


@router.get(
    "/focus-areas",
    response_model=ResponseModel[List[FocusAreaTopic]],
)
async def get_focus_areas(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Retrieve prioritized 14 DSA focus areas with bounded mastery and recommended problems."""

    user_id = str(current_user.get("id") or current_user.get("_id"))
    focus_areas = await service.get_focus_areas(user_id)

    return ResponseModel(
        success=True,
        data=[FocusAreaTopic(**f) for f in focus_areas],
        message="DSA focus areas retrieved successfully.",
    )


@router.get(
    "/readiness-breakdown",
    response_model=ResponseModel[ReadinessBreakdown],
)
async def get_readiness_breakdown(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Retrieve detailed mathematical breakdown, rubric weights, and insights for DSA Readiness."""

    user_id = str(current_user.get("id") or current_user.get("_id"))
    breakdown = await service.get_readiness_breakdown(user_id)

    return ResponseModel(
        success=True,
        data=ReadinessBreakdown(**breakdown),
        message="DSA Readiness breakdown retrieved successfully.",
    )


@router.get(
    "/statistics",
    response_model=ResponseModel[LeetCodeStatisticsResponse],
)
async def get_leetcode_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Fetch problem-solving statistics, difficulty breakdown, and contest ranking."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    result = await service.get_leetcode_statistics(user_id)

    data = LeetCodeStatisticsResponse(
        user_id=user_id,
        leetcode_username=result["leetcode_username"],
        statistics=result.get("statistics"),
        contest=result.get("contest"),
        topic_statistics=result.get("topic_statistics", []),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="LeetCode statistics retrieved successfully.",
    )


@router.get(
    "/activity",
    response_model=ResponseModel[LeetCodeActivityResponse],
)
async def get_leetcode_activity(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Fetch recent problem submission activity."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    result = await service.get_leetcode_activity(user_id)

    data = LeetCodeActivityResponse(
        user_id=user_id,
        leetcode_username=result["leetcode_username"],
        recent_activity=result.get("recent_activity", []),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="LeetCode activity retrieved successfully.",
    )


@router.post(
    "/analyze",
    response_model=ResponseModel[LeetCodeAnalysisResponse],
)
async def analyze_leetcode(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Trigger AI LeetCode Analyzer microservice for the connected profile."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    profile = await service.analyze_leetcode(user_id)

    data = LeetCodeAnalysisResponse(
        user_id=user_id,
        leetcode_username=profile["leetcode_username"],
        analysis_version=profile.get("analysis_version", "1.0"),
        analyzed_at=profile.get("updated_at"),
        analysis=profile.get("analysis"),
    )

    return ResponseModel(
        success=True,
        data=data,
        message="LeetCode AI analysis completed successfully.",
    )


@router.get(
    "/analysis",
    response_model=ResponseModel[LeetCodeAnalysisResponse],
)
async def get_leetcode_analysis(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: LeetCodeService = Depends(get_leetcode_service),
):
    """Fetch stored AI analysis for connected LeetCode profile."""

    user_id = str(current_user.get("id") or current_user.get("_id"))

    result = await service.get_leetcode_analysis(user_id)

    data = LeetCodeAnalysisResponse(
        user_id=user_id,
        leetcode_username=result["leetcode_username"],
        analysis_version=result["analysis_version"],
        analyzed_at=result.get("analyzed_at"),
        analysis=result["analysis"],
    )

    return ResponseModel(
        success=True,
        data=data,
        message="LeetCode AI analysis retrieved successfully.",
    )