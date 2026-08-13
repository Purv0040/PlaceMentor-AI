"""Unit tests for Contest Analyzer."""

from services.contest_analyzer import ContestAnalyzer


def test_contest_analyzer_available():
    raw_contest = {
        "attendedContestsCount": 12,
        "rating": 1750.4,
        "globalRanking": 8500,
        "totalParticipants": 150000,
        "topPercentage": 5.6
    }

    data, score = ContestAnalyzer.analyze_contest(raw_contest)

    assert data.is_available is True
    assert data.attended_contests == 12
    assert data.rating == 1750.4
    assert data.global_ranking == 8500
    assert score > 0.0


def test_contest_analyzer_unavailable():
    data, score = ContestAnalyzer.analyze_contest(None)

    assert data.is_available is False
    assert data.attended_contests == 0
    assert data.rating is None
    assert score == 0.0
