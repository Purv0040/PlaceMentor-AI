import logging
import httpx
from typing import Dict, List, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class LeetCodeClientError(Exception):
    """Base exception for LeetCode API client errors."""
    pass


class LeetCodeUserNotFoundError(LeetCodeClientError):
    """Exception raised when a LeetCode username is not found."""
    pass


class LeetCodeAPIError(LeetCodeClientError):
    """Exception raised when LeetCode API communication fails."""
    pass


_QUERY_PROFILE = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      realName
      aboutMe
      ranking
      reputation
      userAvatar
    }
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
  }
  allQuestionsCount {
    difficulty
    count
  }
}
"""

_QUERY_TOPIC_TAGS = """
query userTopicTags($username: String!) {
  matchedUser(username: $username) {
    tagProblemCounts {
      advanced { tagName slug problemsSolved }
      intermediate { tagName slug problemsSolved }
      fundamental { tagName slug problemsSolved }
    }
  }
}
"""

_QUERY_RECENT = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    timestamp
  }
}
"""

_QUERY_CONTEST = """
query userContestRankingInfo($username: String!) {
  userContestRanking(username: $username) {
    rating
    globalRanking
    totalParticipants
    topPercentage
    attendedContestsCount
  }
}
"""


class LeetCodeAPIClient:
    """Async HTTP Client communicating with LeetCode's public GraphQL endpoint."""

    def __init__(self, endpoint_url: Optional[str] = None) -> None:
        self.endpoint_url = (endpoint_url or settings.LEETCODE_API_URL or "https://leetcode.com/graphql")
        self._headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
            "User-Agent": "AI-Placement-Copilot-Backend/1.0"
        }

    async def _post_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query against LeetCode endpoint."""
        payload = {"query": query, "variables": variables}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(self.endpoint_url, json=payload, headers=self._headers)
                if res.status_code == 404:
                    raise LeetCodeUserNotFoundError("LeetCode user not found.")
                elif res.status_code != 200:
                    raise LeetCodeAPIError(f"HTTP {res.status_code} from LeetCode API: {res.text[:200]}")

                body = res.json()
                if "errors" in body:
                    err_msg = str(body["errors"])
                    if "user does not exist" in err_msg.lower() or "not found" in err_msg.lower():
                        raise LeetCodeUserNotFoundError("LeetCode user not found.")
                    raise LeetCodeAPIError(f"GraphQL errors: {err_msg}")
                return body.get("data", {})
        except httpx.RequestError as e:
            logger.error("Network error connecting to LeetCode GraphQL: %s", e)
            raise LeetCodeAPIError(f"LeetCode API connection failed: {type(e).__name__}")

    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch user profile metadata and submitStats from GraphQL."""
        data = await self._post_query(_QUERY_PROFILE, {"username": username})
        user = data.get("matchedUser")
        if not user:
            raise LeetCodeUserNotFoundError(f"LeetCode user '{username}' not found.")

        profile = user.get("profile", {})
        return {
            "username": user.get("username", username),
            "real_name": profile.get("realName"),
            "about": profile.get("aboutMe"),
            "ranking": profile.get("ranking"),
            "reputation": profile.get("reputation"),
            "avatar_url": profile.get("userAvatar"),
        }

    async def get_solved_problems(self, username: str) -> Dict[str, Any]:
        """Fetch problem statistics by difficulty."""
        data = await self._post_query(_QUERY_PROFILE, {"username": username})
        user = data.get("matchedUser")
        if not user:
            raise LeetCodeUserNotFoundError(f"LeetCode user '{username}' not found.")

        ac_nums = {
            entry["difficulty"]: entry
            for entry in user.get("submitStats", {}).get("acSubmissionNum", [])
        }
        all_counts = {
            entry["difficulty"]: entry["count"]
            for entry in data.get("allQuestionsCount", [])
        }

        easy_solved = ac_nums.get("Easy", {}).get("count", 0)
        medium_solved = ac_nums.get("Medium", {}).get("count", 0)
        hard_solved = ac_nums.get("Hard", {}).get("count", 0)
        total_solved = ac_nums.get("All", {}).get("count", easy_solved + medium_solved + hard_solved)

        all_submissions = ac_nums.get("All", {}).get("submissions", 0)
        acceptance_rate = round(total_solved / all_submissions * 100, 1) if (all_submissions and total_solved) else None

        return {
            "total_solved": total_solved,
            "easy_solved": easy_solved,
            "medium_solved": medium_solved,
            "hard_solved": hard_solved,
            "total_questions": all_counts.get("All", 0),
            "easy_total": all_counts.get("Easy", 0),
            "medium_total": all_counts.get("Medium", 0),
            "hard_total": all_counts.get("Hard", 0),
            "acceptance_rate": acceptance_rate,
        }

    async def get_topic_tags(self, username: str) -> List[Dict[str, Any]]:
        """Fetch solved problem counts per topic tag."""
        try:
            data = await self._post_query(_QUERY_TOPIC_TAGS, {"username": username})
            user = data.get("matchedUser")
            if not user:
                return []
            tag_counts = user.get("tagProblemCounts", {})
            flat: List[Dict[str, Any]] = []
            for tier in ("fundamental", "intermediate", "advanced"):
                for entry in tag_counts.get(tier, []):
                    flat.append({
                        "tagName": entry.get("tagName", ""),
                        "slug": entry.get("slug", ""),
                        "problemsSolved": entry.get("problemsSolved", 0),
                        "tier": tier,
                    })
            return flat
        except Exception as e:
            logger.warning("Topic tags fetch failed for %s: %s", username, e)
            return []

    async def get_recent_submissions(self, username: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch recent accepted submissions."""
        try:
            data = await self._post_query(_QUERY_RECENT, {"username": username, "limit": limit})
            submissions = data.get("recentAcSubmissionList") or []
            return [
                {
                    "title": s.get("title", "Unknown"),
                    "timestamp": str(s.get("timestamp")) if s.get("timestamp") else None
                }
                for s in submissions
            ]
        except Exception as e:
            logger.warning("Recent submissions fetch failed for %s: %s", username, e)
            return []

    async def get_contest_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch contest ranking information."""
        try:
            data = await self._post_query(_QUERY_CONTEST, {"username": username})
            ranking = data.get("userContestRanking")
            if not ranking:
                return None
            return {
                "rating": ranking.get("rating"),
                "global_ranking": ranking.get("globalRanking"),
                "attended_contests": ranking.get("attendedContestsCount"),
                "top_percentage": ranking.get("topPercentage"),
            }
        except Exception as e:
            logger.warning("Contest info fetch failed for %s: %s", username, e)
            return None


# Alias for backward compatibility with pre-existing integration exports
LeetCodeClient = LeetCodeAPIClient
