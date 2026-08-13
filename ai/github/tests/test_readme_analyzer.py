"""Unit tests for README Analyzer."""

from services.readme_analyzer import READMEAnalyzer
from models.github import RepositorySummary


def test_analyze_readme_text_full():
    sample_readme = """
    # Project Title
    ## Description
    An awesome AI Placement Copilot application.
    ## Features
    - Automated resume parsing
    - GitHub analysis
    - LeetCode evaluation
    ## Installation
    Run `pip install -r requirements.txt`
    ## Usage
    Run `python main.py`
    ## Technologies
    Built with Python, FastAPI, Pydantic, and OpenCV.
    ## API Documentation
    GET /health and POST /api/v1/github/analyze
    ![Demo Screenshot](screenshot.png)
    ## License
    Licensed under the MIT License.
    """

    check = READMEAnalyzer.analyze_readme_text(sample_readme)

    assert check.has_readme is True
    assert check.has_description is True
    assert check.has_installation is True
    assert check.has_usage is True
    assert check.has_features is True
    assert check.has_technologies is True
    assert check.has_screenshots is True
    assert check.has_api_docs is True
    assert check.has_license is True
    assert check.score == 20.0


def test_analyze_readme_empty():
    check = READMEAnalyzer.analyze_readme_text("")
    assert check.has_readme is False
    assert check.score == 0.0


def test_analyze_documentation_aggregation():
    repo = RepositorySummary(
        name="test-repo",
        full_name="user/test-repo",
        is_fork=False
    )
    readme_map = {"test-repo": "# Overview\nSimple project\n## Usage\nRun main.py"}
    doc_score = READMEAnalyzer.analyze_documentation([repo], readme_map)
    assert doc_score > 0.0
    assert repo.has_readme is True
