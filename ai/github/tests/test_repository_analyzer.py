"""Unit tests for Repository Analyzer."""

from services.repository_analyzer import RepositoryAnalyzer


def test_repository_analyzer():
    raw_repos = [
        {
            "name": "project1",
            "full_name": "user/project1",
            "description": "Full stack placement copilot backend application",
            "fork": False,
            "stargazers_count": 10,
            "forks_count": 2,
            "language": "Python",
            "topics": ["fastapi", "ai", "machine-learning"],
            "license": {"name": "MIT License"},
            "size": 500
        },
        {
            "name": "project2",
            "full_name": "user/project2",
            "description": "React dashboard frontend application",
            "fork": False,
            "stargazers_count": 5,
            "forks_count": 1,
            "language": "TypeScript",
            "topics": ["react", "dashboard"],
            "license": {"name": "MIT License"},
            "size": 300
        },
        {
            "name": "forked-repo",
            "full_name": "user/forked-repo",
            "description": "Forked project",
            "fork": True,
            "stargazers_count": 0,
            "forks_count": 0,
            "language": "JavaScript",
            "topics": []
        }
    ]

    summaries, stats, languages, repo_quality_score, tech_diversity_score = (
        RepositoryAnalyzer.analyze_repositories(raw_repos)
    )

    assert len(summaries) == 3
    assert stats.total_repos == 3
    assert stats.non_fork_repos == 2
    assert stats.fork_repos == 1
    assert stats.total_stars == 15
    assert languages["Python"] == 1
    assert languages["TypeScript"] == 1
    assert repo_quality_score > 0.0
    assert tech_diversity_score > 0.0
