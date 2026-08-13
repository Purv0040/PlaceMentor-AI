"""Activity signal analyzer for GitHub activity and commit frequency."""

from datetime import datetime, timezone
from typing import List, Dict, Any
from models.github import RepositorySummary


class ActivityAnalyzer:
    """Analyzes recent activity signals, commit frequency, and repository push dates."""

    @staticmethod
    def analyze_activity(
        repositories: List[RepositorySummary],
        events: List[Dict[str, Any]]
    ) -> float:
        """
        Calculates Activity Score out of 25 based on push timestamps and public activity events.
        """
        if not repositories and not events:
            return 0.0

        score = 0.0
        now = datetime.now(timezone.utc)

        # 1. Event activity score (Max 10)
        # PushEvents, CreateEvents, PullRequestEvents, IssueEvents in recent events feed
        push_events = sum(1 for e in events if e.get("type") == "PushEvent")
        pr_events = sum(1 for e in events if e.get("type") in ("PullRequestEvent", "PullRequestReviewEvent"))
        issue_events = sum(1 for e in events if e.get("type") == "IssuesEvent")
        total_meaningful_events = push_events + pr_events + issue_events

        if total_meaningful_events >= 30:
            score += 10.0
        elif total_meaningful_events >= 15:
            score += 7.5
        elif total_meaningful_events >= 5:
            score += 5.0
        elif len(events) > 0:
            score += 2.5

        # 2. Recency of pushed repositories (Max 15)
        # Check pushed_at dates for non-fork repositories
        recent_30_days = 0
        recent_90_days = 0
        recent_180_days = 0

        for repo in repositories:
            pushed_str = repo.pushed_at or repo.updated_at
            if not pushed_str:
                continue

            try:
                # Standard ISO format parsing e.g. 2026-08-10T12:00:00Z
                pushed_dt = datetime.fromisoformat(pushed_str.replace("Z", "+00:00"))
                days_diff = (now - pushed_dt).days

                if days_diff <= 30:
                    recent_30_days += 1
                    recent_90_days += 1
                    recent_180_days += 1
                elif days_diff <= 90:
                    recent_90_days += 1
                    recent_180_days += 1
                elif days_diff <= 180:
                    recent_180_days += 1
            except Exception:
                pass

        if recent_30_days >= 2:
            score += 15.0
        elif recent_30_days >= 1:
            score += 12.0
        elif recent_90_days >= 2:
            score += 9.0
        elif recent_90_days >= 1:
            score += 6.0
        elif recent_180_days >= 1:
            score += 3.0

        return min(25.0, round(score, 2))
