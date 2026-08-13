"""Unit tests for Activity Analyzer."""

from datetime import datetime, timezone
from services.activity_analyzer import ActivityAnalyzer
from models.github import RepositorySummary


def test_activity_analyzer():
    now_iso = datetime.now(timezone.utc).isoformat()
    repos = [
        RepositorySummary(
            name="active-repo",
            full_name="user/active-repo",
            pushed_at=now_iso
        )
    ]
    events = [
        {"type": "PushEvent"},
        {"type": "PushEvent"},
        {"type": "PullRequestEvent"}
    ]

    score = ActivityAnalyzer.analyze_activity(repos, events)
    assert score > 0.0
