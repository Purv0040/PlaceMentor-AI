import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


def test_github_unauthenticated_access(client: TestClient):
    res = client.get("/api/v1/github")
    assert res.status_code == 401

    res = client.post("/api/v1/github/connect", json={"github_username": "Purv0040"})
    assert res.status_code == 401


def test_github_connect_and_sync_flow(client: TestClient, auth_headers: dict):
    mock_profile = {
        "id": 12345,
        "login": "Purv0040",
        "name": "Purv Patel",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345",
        "bio": "Full Stack & AI Engineer",
        "public_repos": 14,
        "followers": 50,
        "following": 20,
        "html_url": "https://github.com/Purv0040"
    }

    mock_repos = [
        {
            "repo_id": 101,
            "name": "PlaceMentor-AI",
            "full_name": "Purv0040/PlaceMentor-AI",
            "description": "AI placement copilot",
            "html_url": "https://github.com/Purv0040/PlaceMentor-AI",
            "language": "TypeScript",
            "languages": {"TypeScript": 1000},
            "stars": 42,
            "forks": 12,
            "topics": ["react", "fastapi"],
            "has_readme": True,
            "is_fork": False,
            "size": 5000,
        },
        {
            "repo_id": 102,
            "name": "microservice-event-bus",
            "full_name": "Purv0040/microservice-event-bus",
            "description": "Event bus in Go",
            "html_url": "https://github.com/Purv0040/microservice-event-bus",
            "language": "Go",
            "languages": {"Go": 1000},
            "stars": 28,
            "forks": 6,
            "topics": ["go", "rabbitmq"],
            "has_readme": True,
            "is_fork": False,
            "size": 2000,
        }
    ]

    with patch("app.integrations.github_client.GitHubAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.return_value = mock_profile

        res_connect = client.post("/api/v1/github/connect", json={"github_username": "Purv0040"}, headers=auth_headers)
        assert res_connect.status_code == 200
        body_connect = res_connect.json()
        assert body_connect["success"] is True
        assert body_connect["data"]["github_username"] == "Purv0040"

    res_get = client.get("/api/v1/github", headers=auth_headers)
    assert res_get.status_code == 200
    body_get = res_get.json()
    assert body_get["data"]["github_username"] == "Purv0040"

    with patch("app.integrations.github_client.GitHubAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile, \
         patch("app.integrations.github_client.GitHubAPIClient.get_user_repos", new_callable=AsyncMock) as mock_get_repos:
        mock_get_profile.return_value = mock_profile
        mock_get_repos.return_value = mock_repos

        res_sync = client.post("/api/v1/github/sync", headers=auth_headers)
        assert res_sync.status_code == 200
        body_sync = res_sync.json()
        assert body_sync["success"] is True
        assert body_sync["data"]["statistics"]["total_repositories"] == 2
        assert body_sync["data"]["statistics"]["total_stars"] == 70

    res_repos = client.get("/api/v1/github/repositories?page=1&limit=10", headers=auth_headers)
    assert res_repos.status_code == 200
    body_repos = res_repos.json()
    assert body_repos["data"]["total"] == 2
    assert len(body_repos["data"]["items"]) == 2

    mock_ai_output = {
        "profile": {"username": "Purv0040", "public_repos": 14},
        "activity": {"total_public_repos": 14, "total_stars": 70, "total_forks": 18},
        "languages": {"primary_language": "TypeScript", "all_languages": ["TypeScript", "Go"]},
        "technical_categories": [{"name": "Frontend", "detected": True, "evidence": ["PlaceMentor-AI"]}],
        "complexity_analyses": [{"repo_name": "PlaceMentor-AI", "complexity_level": "advanced", "confidence": "high"}],
        "strengths": ["Strong TypeScript and Go technical variety"],
        "gaps": ["Add Kubernetes container orchestration evidence"],
        "technical_patterns": ["Microservices and REST API architecture"],
        "recommendations": ["Add architecture diagrams to repositories"],
        "evidence_summary": "Solid engineering portfolio with production-grade fullstack microservices."
    }

    with patch("app.integrations.ai_client.AIClient.analyze_github", new_callable=AsyncMock) as mock_ai_analyze:
        mock_ai_analyze.return_value = mock_ai_output

        res_analyze = client.post("/api/v1/github/analyze", headers=auth_headers)
        assert res_analyze.status_code == 200
        body_analyze = res_analyze.json()
        assert body_analyze["success"] is True
        assert body_analyze["data"]["analysis"]["profile"]["username"] == "Purv0040"

    res_fetch_analysis = client.get("/api/v1/github/analysis", headers=auth_headers)
    assert res_fetch_analysis.status_code == 200
    assert res_fetch_analysis.json()["data"]["analysis"]["profile"]["username"] == "Purv0040"

    # Verify has_analysis is True when GET /api/v1/github is called
    res_get_after_analysis = client.get("/api/v1/github", headers=auth_headers)
    assert res_get_after_analysis.status_code == 200
    assert res_get_after_analysis.json()["data"]["has_analysis"] is True

    # Test repeated analyze calls behave safely / idempotently
    with patch("app.integrations.ai_client.AIClient.analyze_github", new_callable=AsyncMock) as mock_ai_analyze:
        mock_ai_analyze.return_value = mock_ai_output
        res_analyze_again = client.post("/api/v1/github/analyze", headers=auth_headers)
        assert res_analyze_again.status_code == 200
        assert res_analyze_again.json()["success"] is True

    res_del = client.delete("/api/v1/github", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["disconnected"] is True

    res_after = client.get("/api/v1/github", headers=auth_headers)
    assert res_after.status_code == 404


def test_github_ai_analysis_failure_handling(client: TestClient, auth_headers: dict):
    """Verify that AI service failures return HTTP 502 with structured error details."""
    from app.integrations.ai_client import AIClientError

    mock_profile = {
        "id": 54321,
        "login": "testdev",
        "name": "Test Dev",
        "public_repos": 2,
        "html_url": "https://github.com/testdev"
    }

    with patch("app.integrations.github_client.GitHubAPIClient.get_user_profile", new_callable=AsyncMock) as mock_get_profile:
        mock_get_profile.return_value = mock_profile
        client.post("/api/v1/github/connect", json={"github_username": "testdev"}, headers=auth_headers)

    with patch("app.integrations.ai_client.AIClient.analyze_github", new_callable=AsyncMock) as mock_ai_analyze:
        mock_ai_analyze.side_effect = AIClientError("AI Service error HTTP 500: Failed to generate valid structured output")

        res = client.post("/api/v1/github/analyze", headers=auth_headers)
        assert res.status_code == 502
        body = res.json()
        assert body["success"] is False
        assert "AI GitHub analysis failed" in body["error"]["message"]

    # Cleanup
    client.delete("/api/v1/github", headers=auth_headers)


def test_deterministic_scoring_functions():
    """Unit test scoring formulas, streak calculations, and boundary conditions."""
    from app.services.github_service import (
        calculate_repo_quality,
        calculate_event_metrics,
        calculate_impact_and_quality
    )

    # 1. Boundary: Empty repositories
    empty_events = {"total_commits": 0, "commits_30d": 0, "active_streak": 0, "longest_streak": 0, "last_active_date": None, "weekly_activity": []}
    score, breakdown, avg_q, strengths, improvements = calculate_impact_and_quality([], empty_events)
    assert score == 0
    assert avg_q == 0
    assert "repository_quality" in breakdown
    assert len(improvements) > 0

    # 2. Individual repository quality
    high_q_repo = {
        "name": "enterprise-platform",
        "description": "Production-grade microservices system built with TypeScript and Docker.",
        "has_readme": True,
        "is_fork": False,
        "pushed_at": "2026-10-01T12:00:00Z",
        "stars": 15,
        "forks": 5,
        "size": 5000
    }
    q_score, q_tier = calculate_repo_quality(high_q_repo)
    assert 80 <= q_score <= 100
    assert q_tier == "Production Grade"

    low_q_repo = {
        "name": "temp-fork",
        "description": "",
        "has_readme": False,
        "is_fork": True,
        "pushed_at": "2020-01-01T00:00:00Z",
        "stars": 0,
        "forks": 0,
        "size": 0
    }
    low_score, low_tier = calculate_repo_quality(low_q_repo)
    assert low_score < 40
    assert low_tier == "Early Prototype"

    # 3. Events & Streak calculation
    sample_events = [
        {
            "type": "PushEvent",
            "created_at": "2026-10-09T10:00:00Z",
            "payload": {"size": 3, "commits": [{}, {}, {}]}
        },
        {
            "type": "PushEvent",
            "created_at": "2026-10-08T15:00:00Z",
            "payload": {"size": 2, "commits": [{}, {}]}
        },
        {
            "type": "WatchEvent",  # Non-push event should be ignored
            "created_at": "2026-10-07T10:00:00Z"
        }
    ]
    evt_metrics = calculate_event_metrics(sample_events)
    assert evt_metrics["total_commits"] == 5
    assert len(evt_metrics["weekly_activity"]) == 6


def test_push_activity_metrics_and_coverage():
    """Comprehensive test for push-event counts, commit distinctions, deduplication, date boundaries, and incomplete history."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    from app.services.github_service import calculate_event_metrics, APP_TIMEZONE

    today = datetime.now(APP_TIMEZONE).date()

    # Event 1: Recent push with 3 distinct commits in W6 (2 days ago)
    d_w6 = datetime.now(APP_TIMEZONE) - timedelta(days=2)
    e1 = {
        "id": "push-w6-1",
        "type": "PushEvent",
        "created_at": d_w6.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {
            "push_id": 1001,
            "size": 3,
            "commits": [{"sha": "a1"}, {"sha": "a2"}, {"sha": "a3"}]
        }
    }
    # Duplicate of e1 with same id
    e1_dup_id = {
        "id": "push-w6-1",
        "type": "PushEvent",
        "created_at": d_w6.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {"push_id": 1001, "size": 3}
    }
    # Duplicate with same push_id but different id
    e1_dup_push = {
        "id": "push-w6-different-id",
        "type": "PushEvent",
        "created_at": d_w6.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {"push_id": 1001, "size": 3}
    }

    # Event 2: Push event in W4 (18 days ago) where GitHub API omits commits/size
    d_w4 = datetime.now(APP_TIMEZONE) - timedelta(days=18)
    e2 = {
        "id": "push-w4-1",
        "type": "PushEvent",
        "created_at": d_w4.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": {
            "push_id": 1002,
            "ref": "refs/heads/main"
        }
    }

    # Non-push event (should be completely excluded)
    e_watch = {
        "id": "watch-1",
        "type": "WatchEvent",
        "created_at": d_w6.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    events = [e1, e1_dup_id, e1_dup_push, e2, e_watch]
    metrics = calculate_event_metrics(events)

    # 1. Event deduplication: Only 2 unique push events should be counted
    assert metrics["coverage"]["push_events_analyzed"] == 2
    # e1 has 3 commits, e2 omits size so it defaults to 1 commit -> 4 total commits
    assert metrics["total_commits"] == 4

    # 2. Date boundaries: Exactly 6 consecutive weeks covering 42 days
    wa = metrics["weekly_activity"]
    assert len(wa) == 6
    assert wa[0]["week"] == "W1"
    assert wa[5]["week"] == "W6"

    # Verify W6 activity
    assert wa[5]["pushes"] == 3  # Counted based on commit/push payload
    assert wa[5]["status"] == "complete"
    assert wa[5]["metric_type"] == "public_push_events"

    # Verify W5 (7-13 days ago): Zero activity, but within the 18-day coverage horizon
    assert wa[4]["pushes"] == 0
    assert wa[4]["status"] == "verified_zero"

    # Verify W4 (14-20 days ago): Has event e2 (18 days ago)
    assert wa[3]["pushes"] == 1
    assert wa[3]["status"] == "complete"

    # Verify W1, W2, W3: Occur before 18 days ago (the oldest event)
    # Their history is unverified and MUST be marked 'incomplete_history'
    assert wa[0]["status"] == "incomplete_history"
    assert wa[1]["status"] == "incomplete_history"
    assert wa[2]["status"] == "incomplete_history"

    # Coverage metadata
    assert metrics["coverage"]["days_covered"] == 18
    assert metrics["coverage"]["is_truncated"] is False

def test_language_distribution_largest_remainder_method():
    """Verify that language distribution percentages sum to exactly 100% using Largest Remainder Method."""
    from app.services.github_service import calculate_language_distribution

    # Typical multi-language portfolio
    repos = [
        {"languages": {"Python": 50000, "TypeScript": 30000, "JavaScript": 15000}},
        {"languages": {"HTML": 3000, "CSS": 2000, "Go": 500}},
    ]
    dist = calculate_language_distribution(repos)
    assert len(dist) == 6
    total_percentage = sum(item["percentage"] for item in dist)
    assert total_percentage == 100
    assert dist[0]["name"] == "Python"
    assert dist[0]["bytes"] == 50000

    # Edge case: Empty repos
    empty_dist = calculate_language_distribution([])
    assert empty_dist == []

    # Edge case: Zero bytes
    zero_dist = calculate_language_distribution([{"languages": {"Python": 0}}])
    assert zero_dist == []


def test_activity_streak_zero_when_older_push():
    """Verify that when last push is > 1 day ago in Asia/Kolkata, active_streak is 0 while longest_streak is preserved."""
    from app.services.github_service import calculate_event_metrics

    # Simulate 4 consecutive push events 15-18 days ago
    # 2026-09-22 to 2026-09-25 (assuming current date is 2026-10-10)
    events = [
        {"type": "PushEvent", "created_at": "2026-09-25T10:00:00Z", "payload": {"size": 2, "commits": [{}, {}]}},
        {"type": "PushEvent", "created_at": "2026-09-24T12:00:00Z", "payload": {"size": 1, "commits": [{}]}},
        {"type": "PushEvent", "created_at": "2026-09-23T08:00:00Z", "payload": {"size": 3, "commits": [{}, {}, {}]}},
        {"type": "PushEvent", "created_at": "2026-09-22T14:00:00Z", "payload": {"size": 1, "commits": [{}]}},
    ]
    metrics = calculate_event_metrics(events)
    # Active streak must be 0 because no push today or yesterday
    assert metrics["active_streak"] == 0
    # Longest streak preserves the 4-day run
    assert metrics["longest_streak"] == 4
    assert metrics["total_commits"] == 7
    # 6-week activity array exists and has length 6
    assert len(metrics["weekly_activity"]) == 6
    # Most recent weeks (week index 5 and 4) have 0 commits
    assert metrics["weekly_activity"][-1]["commits"] == 0
    assert metrics["weekly_activity"][-2]["commits"] == 0
    assert metrics["weekly_activity"][-1]["status"] == "verified_zero"
    assert "start_date" in metrics["weekly_activity"][0]
    assert "end_date" in metrics["weekly_activity"][0]


def test_event_deduplication_and_boundary_integrity():
    """Verify that duplicate push events are ignored, week buckets are non-overlapping, and history coverage is marked."""
    from app.services.github_service import calculate_event_metrics

    # Duplicate push events with identical push_id or id
    events = [
        {"id": "evt-1", "type": "PushEvent", "created_at": "2026-10-09T10:00:00Z", "payload": {"push_id": 999, "size": 3}},
        {"id": "evt-1", "type": "PushEvent", "created_at": "2026-10-09T10:00:00Z", "payload": {"push_id": 999, "size": 3}}, # duplicate event
        {"id": "evt-2", "type": "PushEvent", "created_at": "2026-10-09T10:00:00Z", "payload": {"push_id": 999, "size": 3}}, # duplicate push_id
        {"id": "evt-3", "type": "PushEvent", "created_at": "2026-10-08T10:00:00Z", "payload": {"push_id": 888, "size": 2}},
    ]
    metrics = calculate_event_metrics(events)
    # Only 2 unique pushes (size 3 and size 2) -> 5 commits
    assert metrics["total_commits"] == 5

    # Check that 6 weeks have consecutive non-overlapping date boundaries
    wa = metrics["weekly_activity"]
    assert len(wa) == 6
    for i in range(5):
        # End date of W(i) is immediately before start date of W(i+1)
        curr_end = wa[i]["end_date"]
        next_start = wa[i + 1]["start_date"]
        from datetime import date, timedelta
        d_end = date.fromisoformat(curr_end)
        d_next = date.fromisoformat(next_start)
        assert d_next == d_end + timedelta(days=1)


def test_missing_payload_graceful_handling():
    """Verify that when GitHub API omits payload.size and payload.commits, each push event counts as 1 commit."""
    from app.services.github_service import calculate_event_metrics

    # GitHub public event payload format (omits size and commits)
    events = [
        {
            "id": "p-1",
            "type": "PushEvent",
            "created_at": "2026-10-09T12:00:00Z",
            "payload": {
                "repository_id": 12345,
                "push_id": 11111,
                "ref": "refs/heads/main",
                "head": "abc",
                "before": "xyz"
            }
        }
    ]
    metrics = calculate_event_metrics(events)
    assert metrics["total_commits"] == 1
    assert metrics["weekly_activity"][-1]["commits"] == 1
    assert metrics["weekly_activity"][-1]["status"] == "complete"



def test_impact_score_repo_quality_consistency():
    """Verify that repo_quality_score matches the repository_quality breakdown score identically."""
    from app.services.github_service import calculate_impact_and_quality

    repos = [
        {
            "name": "project-one",
            "description": "Full-stack application",
            "has_readme": True,
            "is_fork": False,
            "pushed_at": "2026-10-01T00:00:00Z",
            "stars": 10,
            "forks": 2,
            "size": 3000,
            "languages": {"Python": 10000, "TypeScript": 5000}
        },
        {
            "name": "project-two",
            "description": "Utility script",
            "has_readme": False,
            "is_fork": False,
            "pushed_at": "2026-09-01T00:00:00Z",
            "stars": 1,
            "forks": 0,
            "size": 500,
            "languages": {"Python": 2000}
        }
    ]
    event_metrics = {
        "total_commits": 20,
        "commits_30d": 15,
        "active_streak": 0,
        "longest_streak": 3,
        "last_active_date": "2026-10-01",
        "weekly_activity": [{"week": f"W{i}", "commits": 3} for i in range(1, 7)]
    }

    score, breakdown, avg_q, strengths, improvements = calculate_impact_and_quality(repos, event_metrics)

    # Repository Quality Index must exactly equal breakdown["repository_quality"]["score"]
    assert avg_q == breakdown["repository_quality"]["score"]
    # All dimension scores must be within [0, 100]
    for dim_key in ["repository_quality", "activity_freshness", "language_breadth", "community_engagement"]:
        dim_score = breakdown[dim_key]["score"]
        assert 0 <= dim_score <= 100

    # Impact score must match the weighted formula: round(0.35 * Q + 0.25 * A + 0.20 * L + 0.20 * C)
    expected_impact = round(
        0.35 * breakdown["repository_quality"]["score"]
        + 0.25 * breakdown["activity_freshness"]["score"]
        + 0.20 * breakdown["language_breadth"]["score"]
        + 0.20 * breakdown["community_engagement"]["score"]
    )
    assert score == expected_impact



