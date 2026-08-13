"""Unit tests for GitHub Suggestion Engine."""

from services.github_pipeline import GitHubPipeline
from services.github_scorer import GitHubScorer
from models.github import GitHubProfile, RepositorySummary


def test_generate_suggestions():
    pipeline = GitHubPipeline(client=None)

    profile = GitHubProfile(username="lowscoreuser", name=None, bio="")
    repos = [
        RepositorySummary(name="repo1", full_name="lowscoreuser/repo1", is_fork=False, has_readme=False, description="")
    ]
    score = GitHubScorer.calculate_score(5.0, 5.0, 5.0, 5.0, 3.0)
    languages = {"Python": 1}

    suggestions = pipeline.generate_suggestions(profile, repos, score, languages)

    assert len(suggestions) > 0
    categories = [s.category for s in suggestions]
    assert "PROFILE" in categories or "DOCUMENTATION" in categories or "REPOSITORY" in categories
    for s in suggestions:
        assert s.priority in ("HIGH", "MEDIUM", "LOW")
        assert len(s.message) > 0
        assert len(s.impact) > 0
