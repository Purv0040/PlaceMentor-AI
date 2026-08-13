"""LeetCode GraphQL API client abstraction for collecting user DSA statistics."""

import json
from typing import Dict, Any, Optional
import httpx

from utils.constants import LEETCODE_GRAPHQL_URL
from utils.exceptions import LeetCodeUserNotFoundError, LeetCodeDataUnavailableError, ExternalAPIError
from utils.logger import logger

LEETCODE_USER_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      reputation
    }
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    submissionCalendar
    tagProblemCounts {
      advanced {
        tagName
        problemsSolved
      }
      intermediate {
        tagName
        problemsSolved
      }
      fundamental {
        tagName
        problemsSolved
      }
    }
  }
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    totalParticipants
    topPercentage
  }
}
"""


class LeetCodeClient:
    """HTTP client abstraction for fetching public LeetCode profile data via GraphQL."""

    def __init__(self, endpoint_url: str = LEETCODE_GRAPHQL_URL):
        self.endpoint_url = endpoint_url
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "PlaceMentor-AI-LeetCode-Analyzer/1.0"
        }

    async def get_user_data(self, username: str) -> Dict[str, Any]:
        """
        Executes GraphQL query to collect user problem stats, topic breakdown, contest ranking, and submission calendar.
        """
        payload = {
            "query": LEETCODE_USER_QUERY,
            "variables": {"username": username}
        }

        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            try:
                res = await client.post(self.endpoint_url, json=payload)
                if res.status_code != 200:
                    logger.error(f"LeetCode GraphQL returned HTTP {res.status_code}: {res.text}")
                    raise LeetCodeDataUnavailableError(message=f"LeetCode service responded with HTTP {res.status_code}.")

                data = res.json()
                if "errors" in data and not data.get("data", {}).get("matchedUser"):
                    logger.warning(f"LeetCode user '{username}' not found or error returned: {data.get('errors')}")
                    raise LeetCodeUserNotFoundError(username=username)

                data_inner = data.get("data", {})
                matched_user = data_inner.get("matchedUser")
                if not matched_user:
                    raise LeetCodeUserNotFoundError(username=username)

                return {
                    "matchedUser": matched_user,
                    "userContestRanking": data_inner.get("userContestRanking")
                }

            except (LeetCodeUserNotFoundError, LeetCodeDataUnavailableError):
                raise
            except httpx.RequestError as exc:
                logger.error(f"Network error querying LeetCode for user '{username}': {exc}")
                raise LeetCodeDataUnavailableError(message=f"Network error communicating with LeetCode API: {str(exc)}")
            except Exception as exc:
                logger.error(f"Unexpected exception in LeetCode client for '{username}': {exc}", exc_info=True)
                raise ExternalAPIError(message=f"Failed to process LeetCode response: {str(exc)}")
