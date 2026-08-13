"""FastAPI router for LeetCode Analyzer endpoints."""

from fastapi import APIRouter, HTTPException, status
from models.leetcode import LeetCodeAnalyzeRequest, LeetCodeAnalyzeResponse
from services.leetcode_pipeline import LeetCodePipeline
from utils.exceptions import (
    LeetCodeUserNotFoundError,
    LeetCodeDataUnavailableError,
    ExternalAPIError,
    LeetCodeAnalyzerException
)
from utils.logger import logger

router = APIRouter(prefix="/api/v1/leetcode", tags=["LeetCode Analyzer"])


@router.post("/analyze", response_model=LeetCodeAnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_leetcode(request: LeetCodeAnalyzeRequest) -> LeetCodeAnalyzeResponse:
    """
    Analyze LeetCode profile, solved problem difficulty distribution, 13 core DSA topics,
    activity consistency, and contest rankings.
    Returns structured metrics, score breakdown, weak topic analysis, and prioritized improvement recommendations.
    """
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username parameter cannot be empty.")

    try:
        pipeline = LeetCodePipeline()
        response = await pipeline.run(username)
        return response
    except LeetCodeUserNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except LeetCodeDataUnavailableError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except ExternalAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except LeetCodeAnalyzerException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as exc:
        logger.error(f"Unexpected error analyzing LeetCode user '{username}': {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while analyzing LeetCode profile.")
