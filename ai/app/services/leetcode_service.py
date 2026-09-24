"""
LeetCode data provider abstraction.

The rest of the application depends ONLY on the abstract interface
`BaseLeetCodeProvider`.  The concrete `LeetCodeGraphQLProvider` uses
LeetCode's public GraphQL endpoint (no auth required for public profiles).

If the data source changes, swap out or add a new concrete class without
touching any other module.

Known limitation:
  LeetCode does not offer an official public API.  This provider uses the
  publicly accessible GraphQL endpoint at https://leetcode.com/graphql.
  It may change without notice.  `DataSourceStatus.notes` always reports
  which fields were successfully retrieved so callers can surface this clearly.
"""
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import httpx

from app.schemas.leetcode import (
    ContestInfo,
    DataSourceStatus,
    LeetCodeProfileRaw,
    ProblemStatistics,
    RecentSubmission,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class LeetCodeUserNotFoundError(Exception):
    """Raised when the LeetCode username does not exist."""


class LeetCodeAPIError(Exception):
    """Raised for unexpected errors communicating with the LeetCode endpoint."""


class LeetCodeDataUnavailableError(Exception):
    """Raised when a requested data field is not publicly accessible."""


# ---------------------------------------------------------------------------
# Raw collected bundle (provider-internal)
# ---------------------------------------------------------------------------


class LeetCodeRawBundle:
    """Holds all raw data fetched by a provider in a single pass."""

    def __init__(self) -> None:
        self.profile: Optional[LeetCodeProfileRaw] = None
        self.stats: Optional[ProblemStatistics] = None
        self.topic_tags: List[Dict[str, Any]] = []   # raw tag data
        self.recent_submissions: List[RecentSubmission] = []
        self.contest: Optional[ContestInfo] = None
        self.status: DataSourceStatus = DataSourceStatus(provider="unknown")


# ---------------------------------------------------------------------------
# Abstract provider interface
# ---------------------------------------------------------------------------


class BaseLeetCodeProvider(ABC):
    """
    Abstract interface for LeetCode data providers.

    Implementors must fill in `fetch_profile`, `fetch_solved_problems`,
    `fetch_topic_data`, and `fetch_recent_activity`.
    """

    @abstractmethod
    def fetch_profile(self, username: str) -> LeetCodeProfileRaw:
        ...

    @abstractmethod
    def fetch_solved_problems(self, username: str) -> ProblemStatistics:
        ...

    @abstractmethod
    def fetch_topic_data(self, username: str) -> List[Dict[str, Any]]:
        """Return raw topic tag statistics for the user."""
        ...

    @abstractmethod
    def fetch_recent_activity(self, username: str) -> List[RecentSubmission]:
        ...

    def fetch_all(self, username: str) -> LeetCodeRawBundle:
        """
        Convenience method: attempt each fetch independently.
        Failures populate DataSourceStatus.notes but do not abort the whole run.
        """
        bundle = LeetCodeRawBundle()
        bundle.status.provider = self.__class__.__name__

        try:
            bundle.profile = self.fetch_profile(username)
            bundle.status.profile_available = True
        except LeetCodeUserNotFoundError:
            raise
        except Exception as e:
            bundle.status.notes.append(f"Profile unavailable: {e}")

        try:
            bundle.stats = self.fetch_solved_problems(username)
            bundle.status.problems_available = True
        except Exception as e:
            bundle.status.notes.append(f"Problem statistics unavailable: {e}")

        try:
            bundle.topic_tags = self.fetch_topic_data(username)
            bundle.status.topics_available = bool(bundle.topic_tags)
        except Exception as e:
            bundle.status.notes.append(f"Topic data unavailable: {e}")

        try:
            bundle.recent_submissions = self.fetch_recent_activity(username)
            bundle.status.recent_activity_available = bool(bundle.recent_submissions)
        except Exception as e:
            bundle.status.notes.append(f"Recent activity unavailable: {e}")

        return bundle


# ---------------------------------------------------------------------------
# GraphQL provider (LeetCode public endpoint)
# ---------------------------------------------------------------------------

_GRAPHQL_URL = "https://leetcode.com/graphql"

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


class LeetCodeGraphQLProvider(BaseLeetCodeProvider):
    """
    Fetches data from LeetCode's public GraphQL endpoint.

    No authentication is required for public profiles.
    Rate-limiting is respected by using a single httpx.Client per call.
    """

    def __init__(self) -> None:
        self._headers = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
        }
        self._timeout = float(os.getenv("LEETCODE_TIMEOUT", "15"))

    def _post(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query and return the `data` dict."""
        payload = {"query": query, "variables": variables}
        try:
            with httpx.Client(headers=self._headers, timeout=self._timeout) as client:
                resp = client.post(_GRAPHQL_URL, json=payload)
                resp.raise_for_status()
                body = resp.json()
                if "errors" in body:
                    raise LeetCodeAPIError(f"GraphQL errors: {body['errors']}")
                return body.get("data", {})
        except httpx.TimeoutException as e:
            raise LeetCodeAPIError(f"Timeout reaching LeetCode API: {e}")
        except httpx.HTTPStatusError as e:
            raise LeetCodeAPIError(f"HTTP {e.response.status_code} from LeetCode API")

    def fetch_profile(self, username: str) -> LeetCodeProfileRaw:
        data = self._post(_QUERY_PROFILE, {"username": username})
        user = data.get("matchedUser")
        if not user:
            raise LeetCodeUserNotFoundError(
                f"LeetCode user '{username}' not found."
            )
        profile = user.get("profile", {})
        return LeetCodeProfileRaw(
            username=user["username"],
            real_name=profile.get("realName"),
            about=profile.get("aboutMe"),
            ranking=profile.get("ranking"),
            reputation=profile.get("reputation"),
            avatar_url=profile.get("userAvatar"),
        )

    def fetch_solved_problems(self, username: str) -> ProblemStatistics:
        data = self._post(_QUERY_PROFILE, {"username": username})
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

        easy_solved   = ac_nums.get("Easy",   {}).get("count", 0)
        medium_solved = ac_nums.get("Medium", {}).get("count", 0)
        hard_solved   = ac_nums.get("Hard",   {}).get("count", 0)
        total_solved  = ac_nums.get("All",    {}).get("count", easy_solved + medium_solved + hard_solved)

        # Acceptance rate from overall submissions vs accepted
        all_submissions = ac_nums.get("All", {}).get("submissions", 0)
        acceptance_rate: Optional[float] = None
        if all_submissions and total_solved:
            acceptance_rate = round(total_solved / all_submissions * 100, 1)

        return ProblemStatistics(
            total_solved=total_solved,
            easy_solved=easy_solved,
            medium_solved=medium_solved,
            hard_solved=hard_solved,
            total_questions=all_counts.get("All", 0),
            easy_total=all_counts.get("Easy", 0),
            medium_total=all_counts.get("Medium", 0),
            hard_total=all_counts.get("Hard", 0),
            acceptance_rate=acceptance_rate,
        )

    def fetch_topic_data(self, username: str) -> List[Dict[str, Any]]:
        data = self._post(_QUERY_TOPIC_TAGS, {"username": username})
        user = data.get("matchedUser")
        if not user:
            raise LeetCodeUserNotFoundError(f"LeetCode user '{username}' not found.")

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

    def fetch_recent_activity(self, username: str) -> List[RecentSubmission]:
        data = self._post(_QUERY_RECENT, {"username": username, "limit": 15})
        submissions = data.get("recentAcSubmissionList") or []
        return [
            RecentSubmission(
                title=s.get("title", "Unknown"),
                timestamp=s.get("timestamp"),
            )
            for s in submissions
        ]

    def fetch_contest_info(self, username: str) -> Optional[ContestInfo]:
        """Separate method — contest data may not be available."""
        try:
            data = self._post(_QUERY_CONTEST, {"username": username})
            ranking = data.get("userContestRanking")
            if not ranking:
                return None
            return ContestInfo(
                rating=ranking.get("rating"),
                global_ranking=ranking.get("globalRanking"),
                attended_contests=ranking.get("attendedContestsCount"),
                top_percentage=ranking.get("topPercentage"),
            )
        except Exception as e:
            logger.warning(f"Contest data unavailable for {username}: {e}")
            return None


# ---------------------------------------------------------------------------
# Provider factory
# ---------------------------------------------------------------------------


def get_leetcode_provider() -> BaseLeetCodeProvider:
    """
    Return the configured LeetCode provider.
    Reads LEETCODE_PROVIDER env var (default: 'graphql').
    Extend here to add new providers without changing callers.
    """
    provider_name = os.getenv("LEETCODE_PROVIDER", "graphql").lower()
    if provider_name == "graphql":
        return LeetCodeGraphQLProvider()
    raise ValueError(f"Unknown LEETCODE_PROVIDER: '{provider_name}'")
