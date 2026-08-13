"""Unit tests for full LeetCode Pipeline orchestration with mocked client."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from services.leetcode_pipeline import LeetCodePipeline


def test_leetcode_pipeline_run():
    async def _test():
        mock_client = MagicMock()
        now_ts = int(time.time())

        mock_client.get_user_data = AsyncMock(return_value={
            "matchedUser": {
                "username": "testuser",
                "submitStatsGlobal": {
                    "acSubmissionNum": [
                        {"difficulty": "All", "count": 250},
                        {"difficulty": "Easy", "count": 80},
                        {"difficulty": "Medium", "count": 140},
                        {"difficulty": "Hard", "count": 30}
                    ]
                },
                "tagProblemCounts": {
                    "fundamental": [
                        {"tagName": "Array", "problemsSolved": 40},
                        {"tagName": "String", "problemsSolved": 30}
                    ],
                    "intermediate": [
                        {"tagName": "Dynamic Programming", "problemsSolved": 25},
                        {"tagName": "Tree", "problemsSolved": 20}
                    ]
                },
                "submissionCalendar": f'{{"{now_ts - 86400}": 5, "{now_ts - 86400 * 2}": 3}}'
            },
            "userContestRanking": {
                "attendedContestsCount": 5,
                "rating": 1650.0,
                "globalRanking": 12000
            }
        })

        pipeline = LeetCodePipeline(client=mock_client)
        res = await pipeline.run("testuser")

        assert res.success is True
        assert res.username == "testuser"
        assert res.problem_statistics.total_solved == 250
        assert res.dsa_score.total_score > 50.0
        assert len(res.weak_topics) > 0

    asyncio.run(_test())
