"""Unit tests for full GitHub Pipeline orchestration with mocked client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from services.github_pipeline import GitHubPipeline


def test_github_pipeline_run():
    async def _test():
        mock_client = MagicMock()

        mock_client.get_user_profile = AsyncMock(return_value={
            "login": "pipelineuser",
            "name": "Pipeline User",
            "bio": "Building tools for developers",
            "followers": 20,
            "following": 5,
            "public_repos": 5,
            "avatar_url": "https://example.com/pic.png",
            "location": "India",
            "blog": "https://pipelineuser.dev"
        })

        mock_client.get_user_repositories = AsyncMock(return_value=[
            {
                "name": "awesome-app",
                "full_name": "pipelineuser/awesome-app",
                "description": "An awesome application for testing pipeline",
                "fork": False,
                "stargazers_count": 15,
                "forks_count": 3,
                "language": "Python",
                "topics": ["fastapi", "ai"],
                "license": {"name": "MIT License"},
                "pushed_at": "2026-08-10T10:00:00Z",
                "size": 400
            }
        ])

        mock_client.get_repository_readme = AsyncMock(return_value="""
        # Awesome App
        ## Description
        Great python app.
        ## Installation
        pip install app
        ## Usage
        python run.py
        ## Features
        Feature A
        ## License
        MIT
        """)

        mock_client.get_user_events = AsyncMock(return_value=[
            {"type": "PushEvent"},
            {"type": "PullRequestEvent"}
        ])

        pipeline = GitHubPipeline(client=mock_client)
        res = await pipeline.run("pipelineuser")

        assert res.success is True
        assert res.username == "pipelineuser"
        assert res.profile.name == "Pipeline User"
        assert len(res.repositories) == 1
        assert res.score.total_score > 50.0

    asyncio.run(_test())
