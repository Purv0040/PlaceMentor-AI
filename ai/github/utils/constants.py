"""Constants and scoring weights for GitHub Analyzer."""

# Maximum component weights (Total 100)
WEIGHT_REPOSITORY_QUALITY: float = 30.0
WEIGHT_ACTIVITY: float = 25.0
WEIGHT_DOCUMENTATION: float = 20.0
WEIGHT_TECH_DIVERSITY: float = 15.0
WEIGHT_PROFILE_COMPLETENESS: float = 10.0

# GitHub API URLs
GITHUB_API_BASE_URL: str = "https://api.github.com"

# README section detection patterns
README_SECTION_KEYWORDS = {
    "description": ["description", "about", "overview", "introduction"],
    "installation": ["installation", "setup", "getting started", "install", "requirements"],
    "usage": ["usage", "how to use", "quick start", "example", "running"],
    "features": ["features", "highlights", "key features", "functionality"],
    "technologies": ["technologies", "tech stack", "built with", "stack", "tools used"],
    "screenshots": ["screenshot", "screenshots", "demo", "preview", ".png", ".jpg", ".gif", "<img", "!["],
    "api_docs": ["api", "endpoints", "route", "swagger", "postman", "graphql"],
    "license": ["license", "mit", "apache", "gpl", "bsd"]
}
