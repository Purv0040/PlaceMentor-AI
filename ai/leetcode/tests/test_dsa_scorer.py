"""Unit tests for DSA Scorer."""

from services.dsa_scorer import DSAScorer


def test_dsa_scorer_full():
    breakdown = DSAScorer.calculate_score(
        problems_solved_score=25.0,
        difficulty_distribution_score=20.0,
        topic_coverage_score=30.0,
        consistency_score=15.0,
        contest_performance_score=10.0,
        contest_available=True
    )

    assert breakdown.total_score == 100.0
    assert breakdown.problems_solved_score == 25.0
    assert breakdown.difficulty_distribution_score == 20.0
    assert breakdown.topic_coverage_score == 30.0
    assert breakdown.consistency_score == 15.0
    assert breakdown.contest_performance_score == 10.0
    assert breakdown.contest_available is True


def test_dsa_scorer_contest_unavailable():
    breakdown = DSAScorer.calculate_score(
        problems_solved_score=20.0,
        difficulty_distribution_score=18.0,
        topic_coverage_score=25.0,
        consistency_score=12.0,
        contest_performance_score=10.0,
        contest_available=False
    )

    assert breakdown.contest_performance_score == 0.0
    assert breakdown.total_score == 75.0
    assert breakdown.contest_available is False
