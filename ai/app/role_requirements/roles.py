"""
Structured role requirements definitions for AI Placement Copilot.
Defines required skills, proficiency levels, importance ratings, and prerequisites for initial target roles.
"""
from typing import Dict, List, Optional
from app.schemas.skill_gap import RoleSkillRequirement

ROLE_REQUIREMENTS_REGISTRY: Dict[str, List[RoleSkillRequirement]] = {
    # 1. AI/ML Engineer
    "AI/ML Engineer": [
        RoleSkillRequirement(skill="Python", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="PyTorch", required_level="Intermediate", importance="high", category="Machine Learning", prerequisites=["Python"]),
        RoleSkillRequirement(skill="Scikit-learn", required_level="Intermediate", importance="high", category="Machine Learning", prerequisites=["Python"]),
        RoleSkillRequirement(skill="Data Structures & Algorithms", required_level="Intermediate", importance="high", category="DSA"),
        RoleSkillRequirement(skill="Deep Learning", required_level="Intermediate", importance="high", category="Machine Learning", prerequisites=["PyTorch"]),
        RoleSkillRequirement(skill="Statistics", required_level="Intermediate", importance="high", category="Data Science"),
        RoleSkillRequirement(skill="Docker", required_level="Intermediate", importance="medium", category="DevOps"),
        RoleSkillRequirement(skill="REST API", required_level="Intermediate", importance="medium", category="Backend"),
        RoleSkillRequirement(skill="TensorFlow", required_level="Intermediate", importance="medium", category="Machine Learning", prerequisites=["Python"]),
    ],

    # 2. Backend Developer
    "Backend Developer": [
        RoleSkillRequirement(skill="Python", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="Data Structures & Algorithms", required_level="Advanced", importance="critical", category="DSA"),
        RoleSkillRequirement(skill="REST API", required_level="Advanced", importance="critical", category="Backend"),
        RoleSkillRequirement(skill="FastAPI", required_level="Intermediate", importance="high", category="Backend", prerequisites=["Python"]),
        RoleSkillRequirement(skill="PostgreSQL", required_level="Intermediate", importance="high", category="Databases"),
        RoleSkillRequirement(skill="Docker", required_level="Intermediate", importance="high", category="DevOps"),
        RoleSkillRequirement(skill="System Design", required_level="Intermediate", importance="high", category="CS Fundamentals"),
        RoleSkillRequirement(skill="Redis", required_level="Intermediate", importance="medium", category="Databases"),
        RoleSkillRequirement(skill="Git", required_level="Intermediate", importance="medium", category="DevOps"),
    ],

    # 3. Full Stack Developer
    "Full Stack Developer": [
        RoleSkillRequirement(skill="JavaScript", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="React", required_level="Intermediate", importance="high", category="Frontend", prerequisites=["JavaScript"]),
        RoleSkillRequirement(skill="Node.js", required_level="Intermediate", importance="high", category="Backend", prerequisites=["JavaScript"]),
        RoleSkillRequirement(skill="HTML/CSS", required_level="Intermediate", importance="high", category="Frontend"),
        RoleSkillRequirement(skill="REST API", required_level="Advanced", importance="critical", category="Backend"),
        RoleSkillRequirement(skill="PostgreSQL", required_level="Intermediate", importance="high", category="Databases"),
        RoleSkillRequirement(skill="Data Structures & Algorithms", required_level="Intermediate", importance="high", category="DSA"),
        RoleSkillRequirement(skill="Docker", required_level="Intermediate", importance="medium", category="DevOps"),
        RoleSkillRequirement(skill="Git", required_level="Intermediate", importance="medium", category="DevOps"),
    ],

    # 4. Data Scientist
    "Data Scientist": [
        RoleSkillRequirement(skill="Python", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="Pandas", required_level="Advanced", importance="critical", category="Data Science", prerequisites=["Python"]),
        RoleSkillRequirement(skill="SQL", required_level="Intermediate", importance="high", category="Databases"),
        RoleSkillRequirement(skill="Scikit-learn", required_level="Intermediate", importance="high", category="Machine Learning", prerequisites=["Python"]),
        RoleSkillRequirement(skill="Exploratory Data Analysis", required_level="Advanced", importance="high", category="Data Science"),
        RoleSkillRequirement(skill="Statistics", required_level="Intermediate", importance="high", category="Data Science"),
        RoleSkillRequirement(skill="NumPy", required_level="Intermediate", importance="high", category="Data Science", prerequisites=["Python"]),
        RoleSkillRequirement(skill="Data Visualization", required_level="Intermediate", importance="medium", category="Data Science"),
    ],

    # 5. Data Analyst
    "Data Analyst": [
        RoleSkillRequirement(skill="SQL", required_level="Advanced", importance="critical", category="Databases"),
        RoleSkillRequirement(skill="Python", required_level="Intermediate", importance="high", category="Programming"),
        RoleSkillRequirement(skill="Tableau", required_level="Intermediate", importance="high", category="Data Science"),
        RoleSkillRequirement(skill="Data Visualization", required_level="Intermediate", importance="high", category="Data Science"),
        RoleSkillRequirement(skill="Exploratory Data Analysis", required_level="Intermediate", importance="high", category="Data Science"),
        RoleSkillRequirement(skill="Statistics", required_level="Intermediate", importance="medium", category="Data Science"),
    ],

    # 6. Data Engineer
    "Data Engineer": [
        RoleSkillRequirement(skill="Python", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="SQL", required_level="Advanced", importance="critical", category="Databases"),
        RoleSkillRequirement(skill="PostgreSQL", required_level="Advanced", importance="high", category="Databases"),
        RoleSkillRequirement(skill="Docker", required_level="Intermediate", importance="high", category="DevOps"),
        RoleSkillRequirement(skill="Kafka", required_level="Intermediate", importance="medium", category="Backend"),
        RoleSkillRequirement(skill="Data Structures & Algorithms", required_level="Intermediate", importance="high", category="DSA"),
    ],
}

# Alias map for user inputs (lowercase -> canonical role name)
ROLE_ALIASES: Dict[str, str] = {
    "ai/ml engineer": "AI/ML Engineer",
    "ai/ml": "AI/ML Engineer",
    "ml engineer": "AI/ML Engineer",
    "machine learning engineer": "AI/ML Engineer",
    "backend developer": "Backend Developer",
    "backend engineer": "Backend Developer",
    "backend": "Backend Developer",
    "sde 1 backend": "Backend Developer",
    "full stack developer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "full stack engineer": "Full Stack Developer",
    "fullstack": "Full Stack Developer",
    "data scientist": "Data Scientist",
    "ds": "Data Scientist",
    "data analyst": "Data Analyst",
    "da": "Data Analyst",
    "data engineer": "Data Engineer",
    "de": "Data Engineer",
}


def get_canonical_role_name(target_role: str) -> str:
    """Resolves raw target role string to canonical role name."""
    if not target_role:
        return "Backend Developer"
    clean = target_role.strip().lower()
    return ROLE_ALIASES.get(clean, target_role.strip().title())


def get_role_requirements(target_role: str) -> List[RoleSkillRequirement]:
    """Retrieves skill requirements for a given target role, resolving aliases."""
    canonical = get_canonical_role_name(target_role)
    if canonical in ROLE_REQUIREMENTS_REGISTRY:
        return ROLE_REQUIREMENTS_REGISTRY[canonical]
    
    # Fallback to Backend Developer if unknown role is requested
    return ROLE_REQUIREMENTS_REGISTRY["Backend Developer"]
