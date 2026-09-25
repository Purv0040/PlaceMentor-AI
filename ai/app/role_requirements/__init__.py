"""
Role requirements registry for the Skill Gap Engine.
Loads static role definitions — no LLM, no DB, pure Python.
"""
from typing import Dict, List

from app.schemas.skill_gap import RoleRequirement


# Map from URL-safe role key -> human display name
ROLE_DISPLAY_NAMES: Dict[str, str] = {
    "ai_ml_engineer": "AI / ML Engineer",
    "backend_developer": "Backend Developer",
    "full_stack_developer": "Full Stack Developer",
    "data_scientist": "Data Scientist",
    "data_analyst": "Data Analyst",
    "data_engineer": "Data Engineer",
}


def _load_role(role_key: str) -> List[RoleRequirement]:
    """Lazy-imports the role module and returns its REQUIREMENTS list."""
    if role_key == "ai_ml_engineer":
        from app.role_requirements.ai_ml_engineer import REQUIREMENTS
    elif role_key == "backend_developer":
        from app.role_requirements.backend_developer import REQUIREMENTS
    elif role_key == "full_stack_developer":
        from app.role_requirements.full_stack_developer import REQUIREMENTS
    elif role_key == "data_scientist":
        from app.role_requirements.data_scientist import REQUIREMENTS
    elif role_key == "data_analyst":
        from app.role_requirements.data_analyst import REQUIREMENTS
    elif role_key == "data_engineer":
        from app.role_requirements.data_engineer import REQUIREMENTS
    else:
        raise ValueError(
            f"Unknown role '{role_key}'. Valid roles: {list(ROLE_DISPLAY_NAMES.keys())}"
        )
    return REQUIREMENTS


def get_role_requirements(role_key: str) -> List[RoleRequirement]:
    """
    Public API: return the list of RoleRequirement objects for a given role key.
    Raises ValueError for unknown roles.
    """
    normalized_key = role_key.strip().lower().replace(" ", "_").replace("-", "_")
    return _load_role(normalized_key)


def get_role_display_name(role_key: str) -> str:
    """Return human-readable display name for a role key."""
    normalized_key = role_key.strip().lower().replace(" ", "_").replace("-", "_")
    return ROLE_DISPLAY_NAMES.get(normalized_key, role_key)


def list_supported_roles() -> List[str]:
    """Return all supported role keys."""
    return list(ROLE_DISPLAY_NAMES.keys())
