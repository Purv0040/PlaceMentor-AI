"""Unit tests for Problem Analyzer."""

from services.problem_analyzer import ProblemAnalyzer


def test_problem_analyzer_balanced():
    raw_ac = [
        {"difficulty": "All", "count": 300},
        {"difficulty": "Easy", "count": 100},
        {"difficulty": "Medium", "count": 160},
        {"difficulty": "Hard", "count": 40}
    ]

    stats, problems_score, diff_score = ProblemAnalyzer.analyze_problems(raw_ac)

    assert stats.total_solved == 300
    assert stats.easy_solved == 100
    assert stats.medium_solved == 160
    assert stats.hard_solved == 40
    assert stats.medium_percentage > 50.0
    assert problems_score > 15.0
    assert diff_score == 20.0


def test_problem_analyzer_zero():
    stats, problems_score, diff_score = ProblemAnalyzer.analyze_problems([])
    assert stats.total_solved == 0
    assert problems_score == 0.0
    assert diff_score == 0.0
