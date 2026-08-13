"""FastAPI router for GitHub Analyzer endpoints."""

from fastapi import APIRouter, HTTPException, status
from models.github import GitHubAnalyzeRequest, GitHubAnalyzeResponse
from services.github_pipeline import GitHubPipeline
from utils.exceptions import (
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
    GitHubAnalyzerException
)
from utils.logger import logger

router = APIRouter(prefix="/api/v1/github", tags=["GitHub Analyzer"])


@router.post("/analyze", response_model=GitHubAnalyzeResponse, status_code=status.HTTP_200_OK)
async def analyze_github(request: GitHubAnalyzeRequest) -> GitHubAnalyzeResponse:
    """
    Analyze public GitHub profile, repositories, documentation, technology stack, and activity.
    Returns structured metrics, score breakdown, and prioritized improvement suggestions.
    """
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username parameter cannot be empty.")

    try:
        pipeline = GitHubPipeline()
        response = await pipeline.run(username)
        return response
    except GitHubUserNotFoundError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except GitHubRateLimitError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except GitHubAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except GitHubAnalyzerException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as exc:
        logger.error(f"Unexpected error analyzing GitHub user '{username}': {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while analyzing GitHub profile.")
