"""
Role requirements registry for the Skill Gap Engine.
Loads static role definitions — pure Python.
"""
from typing import Dict, List

from app.role_requirements.roles import (
    ROLE_REQUIREMENTS_REGISTRY,
    ROLE_ALIASES,
    get_canonical_role_name,
    get_role_requirements,
)
from app.schemas.skill_gap import RoleSkillRequirement

# Map from URL-safe role key -> human display name
ROLE_DISPLAY_NAMES: Dict[str, str] = {
    "ai_ml_engineer": "AI/ML Engineer",
    "backend_developer": "Backend Developer",
    "full_stack_developer": "Full Stack Developer",
    "data_scientist": "Data Scientist",
    "data_analyst": "Data Analyst",
    "data_engineer": "Data Engineer",
}


def get_role_display_name(role_key: str) -> str:
    """Return human-readable display name for a role key."""
    if not role_key:
        return "Backend Developer"
    normalized_key = role_key.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    if normalized_key in ROLE_DISPLAY_NAMES:
        return ROLE_DISPLAY_NAMES[normalized_key]
    return get_canonical_role_name(role_key)


def list_supported_roles() -> List[str]:
    """Return all supported canonical role names."""
    return list(ROLE_REQUIREMENTS_REGISTRY.keys())


__all__ = [
    "ROLE_REQUIREMENTS_REGISTRY",
    "ROLE_ALIASES",
    "ROLE_DISPLAY_NAMES",
    "get_canonical_role_name",
    "get_role_requirements",
    "get_role_display_name",
    "list_supported_roles",
    "RoleSkillRequirement",
]

