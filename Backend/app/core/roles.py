"""Centralized configuration for target roles and categories across the system."""

from typing import List, Dict, Optional

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

ROLE_COMPETENCIES: Dict[str, List[str]] = {
    "Backend Developer": [
        "Python", "FastAPI", "REST API", "SQL", "PostgreSQL",
        "Databases", "System Design", "Docker", "Data Structures & Algorithms", "Git"
    ],
    "Full Stack Engineer": [
        "JavaScript", "TypeScript", "React", "Node.js", "Express.js",
        "REST API", "HTML/CSS", "PostgreSQL", "MongoDB", "Git", "Data Structures & Algorithms"
    ],
    "Full Stack Developer": [
        "JavaScript", "TypeScript", "React", "Node.js", "Express.js",
        "REST API", "HTML/CSS", "PostgreSQL", "MongoDB", "Git", "Data Structures & Algorithms"
    ],
    "Frontend Engineer": [
        "JavaScript", "TypeScript", "React", "HTML/CSS", "Tailwind CSS",
        "Next.js", "REST API", "Git"
    ],
    "AI/ML Engineer": [
        "Python", "Machine Learning", "Deep Learning", "NumPy", "Pandas",
        "PyTorch", "TensorFlow", "Scikit-learn", "Docker", "REST API", "Data Structures & Algorithms"
    ],
    "Cybersecurity Analyst": [
        "Networking", "Linux", "SIEM", "Threat Detection",
        "Incident Response", "Security Fundamentals", "Python"
    ],
    "Data Engineer": [
        "Python", "SQL", "PostgreSQL", "Docker", "Kafka",
        "ETL", "Data Pipelines", "Data Structures & Algorithms"
    ],
    "Data Scientist": [
        "Python", "Pandas", "SQL", "Scikit-learn", "Exploratory Data Analysis",
        "Statistics", "NumPy", "Data Visualization"
    ],
    "Data Analyst": [
        "SQL", "Python", "Tableau", "Power BI", "Data Visualization",
        "Exploratory Data Analysis", "Statistics"
    ],
    "DevOps & Cloud Engineer": [
        "Docker", "Kubernetes", "CI/CD", "AWS", "Linux",
        "Terraform", "Git", "Python"
    ],
    "Software Engineer": [
        "Data Structures & Algorithms", "System Design",
        "Object-Oriented Programming", "Git", "DBMS", "Operating Systems", "Computer Networks"
    ],
}


def get_role_competencies(role: Optional[str]) -> List[str]:
    """Retrieve normalized required competencies for a given target role."""
    if not role or not isinstance(role, str) or not role.strip():
        return []
    clean = role.strip()
    if clean in ROLE_COMPETENCIES:
        return ROLE_COMPETENCIES[clean]
    # Check case-insensitive match
    for k, v in ROLE_COMPETENCIES.items():
        if k.lower() == clean.lower():
            return v
    # Check partial match
    for k, v in ROLE_COMPETENCIES.items():
        if k.lower() in clean.lower() or clean.lower() in k.lower():
            return v
    # Generic engineering competencies fallback for unlisted custom roles
    return ["Data Structures & Algorithms", "System Design", "Git", "REST API", "DBMS"]

