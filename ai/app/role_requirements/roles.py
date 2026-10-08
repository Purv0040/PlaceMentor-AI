"""
Structured role requirements definitions for AI Placement Copilot.
Defines required skills, proficiency levels, importance ratings, and prerequisites for target roles.
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

    # 7. Cybersecurity Analyst & Engineer / Cybersecurity Analyst
    "Cybersecurity Analyst & Engineer": [
        RoleSkillRequirement(skill="Networking", required_level="Advanced", importance="critical", category="Networking"),
        RoleSkillRequirement(skill="Linux", required_level="Advanced", importance="critical", category="OS & Scripting"),
        RoleSkillRequirement(skill="Security Fundamentals", required_level="Advanced", importance="critical", category="Security"),
        RoleSkillRequirement(skill="SIEM", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Threat Detection", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Incident Response", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Vulnerability Management", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="OWASP", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Python", required_level="Intermediate", importance="high", category="Programming"),
        RoleSkillRequirement(skill="Log Analysis", required_level="Intermediate", importance="medium", category="Security"),
        RoleSkillRequirement(skill="MITRE ATT&CK", required_level="Intermediate", importance="high", category="Security"),
    ],
    "Cybersecurity Analyst": [
        RoleSkillRequirement(skill="Networking", required_level="Advanced", importance="critical", category="Networking"),
        RoleSkillRequirement(skill="Linux", required_level="Advanced", importance="critical", category="OS & Scripting"),
        RoleSkillRequirement(skill="Security Fundamentals", required_level="Advanced", importance="critical", category="Security"),
        RoleSkillRequirement(skill="SIEM", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Threat Detection", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Incident Response", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Vulnerability Management", required_level="Intermediate", importance="high", category="Security"),
        RoleSkillRequirement(skill="Python", required_level="Intermediate", importance="high", category="Programming"),
        RoleSkillRequirement(skill="Log Analysis", required_level="Intermediate", importance="medium", category="Security"),
    ],

    # 8. Frontend Developer
    "Frontend Developer": [
        RoleSkillRequirement(skill="HTML/CSS", required_level="Advanced", importance="critical", category="Frontend"),
        RoleSkillRequirement(skill="JavaScript", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="React", required_level="Advanced", importance="critical", category="Frontend"),
        RoleSkillRequirement(skill="TypeScript", required_level="Intermediate", importance="high", category="Programming"),
        RoleSkillRequirement(skill="State Management", required_level="Intermediate", importance="high", category="Frontend"),
        RoleSkillRequirement(skill="REST API", required_level="Intermediate", importance="high", category="Backend"),
    ],

    # 9. DevOps Engineer
    "DevOps Engineer": [
        RoleSkillRequirement(skill="Linux", required_level="Advanced", importance="critical", category="OS & Scripting"),
        RoleSkillRequirement(skill="Docker", required_level="Advanced", importance="critical", category="DevOps"),
        RoleSkillRequirement(skill="CI/CD", required_level="Advanced", importance="critical", category="DevOps"),
        RoleSkillRequirement(skill="Kubernetes", required_level="Intermediate", importance="high", category="DevOps"),
        RoleSkillRequirement(skill="Infrastructure as Code", required_level="Intermediate", importance="high", category="DevOps"),
        RoleSkillRequirement(skill="Cloud Platforms", required_level="Intermediate", importance="high", category="Cloud"),
    ],

    # 10. Cloud Engineer
    "Cloud Engineer": [
        RoleSkillRequirement(skill="Cloud Platforms", required_level="Advanced", importance="critical", category="Cloud"),
        RoleSkillRequirement(skill="Linux", required_level="Intermediate", importance="high", category="OS & Scripting"),
        RoleSkillRequirement(skill="Docker", required_level="Advanced", importance="critical", category="DevOps"),
        RoleSkillRequirement(skill="Kubernetes", required_level="Intermediate", importance="high", category="DevOps"),
        RoleSkillRequirement(skill="Networking", required_level="Intermediate", importance="high", category="Networking"),
    ],

    # 11. Software Engineer
    "Software Engineer": [
        RoleSkillRequirement(skill="Data Structures & Algorithms", required_level="Advanced", importance="critical", category="DSA"),
        RoleSkillRequirement(skill="Object-Oriented Programming", required_level="Advanced", importance="critical", category="CS Fundamentals"),
        RoleSkillRequirement(skill="Python", required_level="Intermediate", importance="high", category="Programming"),
        RoleSkillRequirement(skill="System Design", required_level="Intermediate", importance="high", category="CS Fundamentals"),
        RoleSkillRequirement(skill="REST API", required_level="Intermediate", importance="high", category="Backend"),
        RoleSkillRequirement(skill="SQL", required_level="Intermediate", importance="high", category="Databases"),
    ],

    # 12. QA / Test Engineer
    "QA / Test Engineer": [
        RoleSkillRequirement(skill="Testing Fundamentals", required_level="Advanced", importance="critical", category="Testing"),
        RoleSkillRequirement(skill="Test Case Design", required_level="Advanced", importance="critical", category="Testing"),
        RoleSkillRequirement(skill="Automation Testing", required_level="Intermediate", importance="high", category="Testing"),
        RoleSkillRequirement(skill="Selenium", required_level="Intermediate", importance="high", category="Testing"),
        RoleSkillRequirement(skill="REST API", required_level="Intermediate", importance="high", category="Backend"),
    ],

    # 13. Mobile App Developer
    "Mobile App Developer": [
        RoleSkillRequirement(skill="JavaScript", required_level="Advanced", importance="critical", category="Programming"),
        RoleSkillRequirement(skill="React Native", required_level="Intermediate", importance="critical", category="Mobile"),
        RoleSkillRequirement(skill="Mobile UI Design", required_level="Intermediate", importance="high", category="Mobile"),
        RoleSkillRequirement(skill="REST API", required_level="Intermediate", importance="high", category="Backend"),
    ],

    # 14. Database Engineer
    "Database Engineer": [
        RoleSkillRequirement(skill="SQL", required_level="Advanced", importance="critical", category="Databases"),
        RoleSkillRequirement(skill="Database Design", required_level="Advanced", importance="critical", category="Databases"),
        RoleSkillRequirement(skill="PostgreSQL", required_level="Advanced", importance="high", category="Databases"),
        RoleSkillRequirement(skill="Query Optimization", required_level="Advanced", importance="high", category="Databases"),
    ],
}

# Canonical role definitions
CANONICAL_ROLES: List[str] = [
    "AI/ML Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Data Scientist",
    "Data Engineer",
    "DevOps Engineer",
    "Cybersecurity Analyst & Engineer",
    "Cybersecurity Analyst",
    "Software Engineer",
    "Cloud Engineer",
    "Mobile App Developer",
    "QA / Test Engineer",
    "Database Engineer",
    "Business Analyst",
    "Product Manager",
    "Data Analyst",
]

CANONICAL_ROLE_MAP: Dict[str, str] = {r.lower(): r for r in CANONICAL_ROLES}

# Alias map for user inputs (lowercase -> canonical role name)
ROLE_ALIASES: Dict[str, str] = {
    **CANONICAL_ROLE_MAP,
    "ai/ml": "AI/ML Engineer",
    "ai engineer": "AI/ML Engineer",
    "ai ml engineer": "AI/ML Engineer",
    "ml engineer": "AI/ML Engineer",
    "machine learning engineer": "AI/ML Engineer",
    "backend developer": "Backend Developer",
    "backend engineer": "Backend Developer",
    "backend dev": "Backend Developer",
    "backend": "Backend Developer",
    "sde 1 backend": "Backend Developer",
    "frontend developer": "Frontend Developer",
    "frontend engineer": "Frontend Developer",
    "frontend dev": "Frontend Developer",
    "frontend": "Frontend Developer",
    "full stack developer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "full stack engineer": "Full Stack Developer",
    "fullstack engineer": "Full Stack Developer",
    "fullstack": "Full Stack Developer",
    "data scientist": "Data Scientist",
    "ds": "Data Scientist",
    "data analyst": "Data Analyst",
    "da": "Data Analyst",
    "data engineer": "Data Engineer",
    "de": "Data Engineer",
    "devops engineer": "DevOps Engineer",
    "devops": "DevOps Engineer",
    "cybersecurity analyst & engineer": "Cybersecurity Analyst & Engineer",
    "cybersecurity analyst and engineer": "Cybersecurity Analyst & Engineer",
    "cyber security analyst & engineer": "Cybersecurity Analyst & Engineer",
    "cyber security analyst and engineer": "Cybersecurity Analyst & Engineer",
    "cybersecurity engineer": "Cybersecurity Analyst & Engineer",
    "cyber security engineer": "Cybersecurity Analyst & Engineer",
    "security engineer": "Cybersecurity Analyst & Engineer",
    "cybersecurity analyst": "Cybersecurity Analyst",
    "cyber security analyst": "Cybersecurity Analyst",
    "cybersecurity": "Cybersecurity Analyst",
    "security analyst": "Cybersecurity Analyst",
    "software engineer": "Software Engineer",
    "sde": "Software Engineer",
    "swe": "Software Engineer",
    "software developer": "Software Engineer",
    "cloud engineer": "Cloud Engineer",
    "cloud architect": "Cloud Engineer",
    "mobile app developer": "Mobile App Developer",
    "mobile developer": "Mobile App Developer",
    "android developer": "Mobile App Developer",
    "ios developer": "Mobile App Developer",
    "qa / test engineer": "QA / Test Engineer",
    "qa engineer": "QA / Test Engineer",
    "test engineer": "QA / Test Engineer",
    "qa": "QA / Test Engineer",
    "quality assurance": "QA / Test Engineer",
    "database engineer": "Database Engineer",
    "database administrator": "Database Engineer",
    "dba": "Database Engineer",
    "business analyst": "Business Analyst",
    "ba": "Business Analyst",
    "product manager": "Product Manager",
    "pm": "Product Manager",
}


def get_canonical_role_name(target_role: str) -> str:
    """Resolves raw target role string to canonical role name."""
    if not target_role:
        return "Software Engineer"
    clean = target_role.strip().lower()
    if clean in ROLE_ALIASES:
        return ROLE_ALIASES[clean]
    return target_role.strip()


def get_role_requirements(target_role: str) -> List[RoleSkillRequirement]:
    """Retrieves skill requirements for a given target role, resolving aliases."""
    canonical = get_canonical_role_name(target_role)
    if canonical in ROLE_REQUIREMENTS_REGISTRY:
        return ROLE_REQUIREMENTS_REGISTRY[canonical]
    
    # Fallback to Backend Developer if unknown role is requested
    return ROLE_REQUIREMENTS_REGISTRY["Backend Developer"]
