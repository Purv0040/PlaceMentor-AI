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
    submissionCalendar
    userCalendar {
      streak
      totalActiveDays
      submissionCalendar
    }
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
      totalSubmissionNum {
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
      advanced { tagName tagSlug problemsSolved }
      intermediate { tagName tagSlug problemsSolved }
      fundamental { tagName tagSlug problemsSolved }
    }
  }
}
"""

_QUERY_RECENT = """
query recentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
    statusDisplay
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
  userContestRankingHistory(username: $username) {
    attended
    rating
    ranking
    contest {
      title
      startTime
    }
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
        user_cal = user.get("userCalendar") or {}
        raw_cal = user.get("submissionCalendar") or user_cal.get("submissionCalendar")
        return {
            "username": user.get("username", username),
            "real_name": profile.get("realName"),
            "about": profile.get("aboutMe"),
            "ranking": profile.get("ranking"),
            "reputation": profile.get("reputation"),
            "avatar_url": profile.get("userAvatar"),
            "submission_calendar": raw_cal,
            "streak": user_cal.get("streak", 0),
            "total_active_days": user_cal.get("totalActiveDays", 0),
        }

    async def get_solved_problems(self, username: str) -> Dict[str, Any]:
        """Fetch problem statistics by difficulty, calculate acceptance rate and streaks."""
        data = await self._post_query(_QUERY_PROFILE, {"username": username})
        user = data.get("matchedUser")
        if not user:
            raise LeetCodeUserNotFoundError(f"LeetCode user '{username}' not found.")

        user_cal = user.get("userCalendar") or {}
        ac_nums = {
            entry["difficulty"]: entry
            for entry in user.get("submitStats", {}).get("acSubmissionNum", [])
        }
        total_nums = {
            entry["difficulty"]: entry
            for entry in user.get("submitStats", {}).get("totalSubmissionNum", [])
        }
        all_counts = {
            entry["difficulty"]: entry["count"]
            for entry in data.get("allQuestionsCount", [])
        }

        easy_solved = ac_nums.get("Easy", {}).get("count", 0)
        medium_solved = ac_nums.get("Medium", {}).get("count", 0)
        hard_solved = ac_nums.get("Hard", {}).get("count", 0)
        total_solved = ac_nums.get("All", {}).get("count", easy_solved + medium_solved + hard_solved)

        ac_submissions = ac_nums.get("All", {}).get("submissions", 0) or total_solved
        total_submissions = total_nums.get("All", {}).get("submissions", 0)

        # Standard LeetCode Acceptance Rate = (accepted_submissions / total_submissions) * 100
        if total_submissions and total_submissions > 0:
            acceptance_rate = round((ac_submissions / total_submissions) * 100, 1)
        elif ac_submissions and ac_submissions > 0:
            acceptance_rate = round((total_solved / ac_submissions) * 100, 1)
        else:
            acceptance_rate = None

        # Parse submissionCalendar to evaluate streak metrics
        raw_cal = user.get("submissionCalendar") or user_cal.get("submissionCalendar")
        dates = set()
        if raw_cal:
            try:
                import json
                cal_dict = json.loads(raw_cal) if isinstance(raw_cal, str) else raw_cal
                if isinstance(cal_dict, dict):
                    from datetime import datetime, timezone, timedelta
                    try:
                        from zoneinfo import ZoneInfo
                        tz = ZoneInfo("Asia/Kolkata")
                    except Exception:
                        tz = timezone(timedelta(hours=5, minutes=30))
                    for ts in cal_dict.keys():
                        dates.add(datetime.fromtimestamp(int(ts), tz).date())
            except Exception as e:
                logger.warning("Error parsing submissionCalendar for streak: %s", e)

        # Calculate longest continuous daily streak
        sorted_dates = sorted(list(dates))
        longest_streak = 0
        running = 0
        prev_d = None
        for d in sorted_dates:
            from datetime import timedelta
            if prev_d is None or d == prev_d + timedelta(days=1):
                running += 1
            else:
                running = 1
            longest_streak = max(longest_streak, running)
            prev_d = d

        # LeetCode's userCalendar.streak represents the maximum/best streak achieved in the calendar
        cal_streak = int(user_cal.get("streak") or 0)
        longest_streak = max(longest_streak, cal_streak)

        # Calculate REAL current active streak leading up to today (or yesterday if pending today's submission)
        current_streak = 0
        if dates:
            from datetime import datetime, timezone, timedelta
            try:
                from zoneinfo import ZoneInfo
                tz = ZoneInfo("Asia/Kolkata")
            except Exception:
                tz = timezone(timedelta(hours=5, minutes=30))
            today = datetime.now(tz).date()
            yesterday = today - timedelta(days=1)

            # If user submitted today or yesterday, streak is currently active
            if today in dates:
                check_date = today
            elif yesterday in dates:
                check_date = yesterday
            else:
                check_date = None

            while check_date and check_date in dates:
                current_streak += 1
                check_date -= timedelta(days=1)
        elif cal_streak:
            # Fallback only if no submission calendar timestamps were provided
            current_streak = cal_streak

        longest_streak = max(longest_streak, current_streak)
        total_active_days = user_cal.get("totalActiveDays", len(dates))

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
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "total_active_days": total_active_days,
            "accepted_submissions": ac_submissions,
            "total_submissions": total_submissions,
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
                        "slug": entry.get("tagSlug", "") or entry.get("slug", ""),
                        "problemsSolved": entry.get("problemsSolved", 0),
                        "tier": tier,
                    })
            return flat
        except Exception as e:
            logger.warning("Topic tags fetch failed for %s: %s", username, e)
            return []

    async def get_recent_submissions(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recent accepted submissions."""
        try:
            data = await self._post_query(_QUERY_RECENT, {"username": username, "limit": limit})
            submissions = data.get("recentAcSubmissionList") or []
            return [
                {
                    "title": s.get("title", "Unknown"),
                    "title_slug": s.get("titleSlug"),
                    "url": f"https://leetcode.com/problems/{s.get('titleSlug')}/" if s.get("titleSlug") else f"https://leetcode.com/problems/{s.get('title', '').lower().replace(' ', '-')}/",
                    "timestamp": str(s.get("timestamp")) if s.get("timestamp") else None,
                    "status": s.get("statusDisplay") or "Accepted",
                    "difficulty": None
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
            history = [h for h in (data.get("userContestRankingHistory") or []) if h.get("attended")]
            if not ranking and not history:
                return None
            return {
                "rating": ranking.get("rating") if ranking else None,
                "global_ranking": ranking.get("globalRanking") if ranking else None,
                "attended_contests": ranking.get("attendedContestsCount") if ranking else 0,
                "top_percentage": ranking.get("topPercentage") if ranking else None,
                "history": history
            }
        except Exception as e:
            logger.warning("Contest info fetch failed for %s: %s", username, e)
            return None


# Alias for backward compatibility with pre-existing integration exports
LeetCodeClient = LeetCodeAPIClient
