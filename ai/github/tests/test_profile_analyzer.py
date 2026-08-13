"""Unit tests for Profile Analyzer."""

from services.profile_analyzer import ProfileAnalyzer


def test_analyze_profile_complete():
    raw_data = {
        "login": "testuser",
        "name": "Test User",
        "bio": "Senior Python Backend Developer and AI Engineer",
        "followers": 10,
        "following": 5,
        "public_repos": 12,
        "public_gists": 2,
        "avatar_url": "https://example.com/avatar.jpg",
        "html_url": "https://github.com/testuser",
        "company": "Tech Corp",
        "location": "Bengaluru, India",
        "blog": "https://testuser.dev",
        "email": "test@example.com"
    }

    profile, score = ProfileAnalyzer.analyze_profile(raw_data)

    assert profile.username == "testuser"
    assert profile.name == "Test User"
    assert profile.followers == 10
    assert score == 10.0


def test_analyze_profile_incomplete():
    raw_data = {
        "login": "emptyuser",
        "name": None,
        "bio": None,
        "followers": 0,
        "public_repos": 0
    }

    profile, score = ProfileAnalyzer.analyze_profile(raw_data)

    assert profile.username == "emptyuser"
    assert profile.name is None
    assert score == 0.0
