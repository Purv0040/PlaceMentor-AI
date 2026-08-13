"""Unit tests for LeetCode Suggestions."""

from services.leetcode_pipeline import LeetCodePipeline
from services.dsa_scorer import DSAScorer
from models.leetcode import (
    ProblemStatistics,
    ConsistencyData,
    ContestData,
    WeakTopicItem
)


def test_generate_suggestions():
    pipeline = LeetCodePipeline(client=None)

    prob_stats = ProblemStatistics(
        total_solved=80,
        easy_solved=50,
        medium_solved=25,
        hard_solved=5,
        medium_percentage=31.25
    )

    weak_topics = [
        WeakTopicItem(topic="Dynamic Programming", score=2.0, priority="HIGH"),
        WeakTopicItem(topic="Graphs", score=1.0, priority="HIGH")
    ]

    consistency = ConsistencyData(monthly_activity=3, is_available=True)
    contest = ContestData(attended_contests=0, is_available=False)
    score = DSAScorer.calculate_score(10.0, 10.0, 10.0, 5.0, 0.0, False)
    topic_stats = {"Dynamic Programming": 2, "Graphs": 1}

    suggestions = pipeline.generate_suggestions(
        problem_stats=prob_stats,
        weak_topics=weak_topics,
        consistency=consistency,
        contest_data=contest,
        score=score,
        topic_stats=topic_stats
    )

    assert len(suggestions) > 0
    categories = [s.category for s in suggestions]
    assert "TOPIC" in categories
    assert "DIFFICULTY" in categories
    for s in suggestions:
        assert s.priority in ("HIGH", "MEDIUM", "LOW")
        assert len(s.message) > 0
        assert len(s.impact) > 0
