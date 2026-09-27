"""Centralized configuration for target roles and categories across the system."""

from typing import List, Dict

ALLOWED_TARGET_ROLES: List[str] = [
    "Backend Developer",
    "Full Stack Engineer",
    "AI/ML Engineer",
    "Frontend Engineer",
    "DevOps & Cloud Engineer",
    "Data Engineer",
    "Data Scientist",
    "Data Analyst",
    "Software Engineer",
]

DEFAULT_TARGET_ROLE: str = "Backend Developer"

ROLE_CATEGORIES: Dict[str, str] = {
    "Backend Developer": "Software Engineering",
    "Full Stack Engineer": "Software Engineering",
    "AI/ML Engineer": "AI & Data",
    "Frontend Engineer": "Software Engineering",
    "DevOps & Cloud Engineer": "Infrastructure",
    "Data Engineer": "AI & Data",
    "Data Scientist": "AI & Data",
    "Data Analyst": "AI & Data",
    "Software Engineer": "Software Engineering",
}
