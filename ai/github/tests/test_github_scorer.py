"""Unit tests for GitHub Scorer."""

from services.github_scorer import GitHubScorer


def test_github_scorer_perfect():
    breakdown = GitHubScorer.calculate_score(
        repo_quality_score=30.0,
        activity_score=25.0,
        documentation_score=20.0,
        tech_diversity_score=15.0,
        profile_completeness_score=10.0
    )

    assert breakdown.total_score == 100.0
    assert breakdown.repository_quality == 30.0
    assert breakdown.activity == 25.0
    assert breakdown.documentation == 20.0
    assert breakdown.technology_diversity == 15.0
    assert breakdown.profile_completeness == 10.0


def test_github_scorer_caps():
    breakdown = GitHubScorer.calculate_score(
        repo_quality_score=50.0,
        activity_score=40.0,
        documentation_score=30.0,
        tech_diversity_score=20.0,
        profile_completeness_score=15.0
    )

    assert breakdown.total_score == 100.0
    assert breakdown.repository_quality == 30.0
    assert breakdown.activity == 25.0
