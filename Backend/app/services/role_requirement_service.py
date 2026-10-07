"""
RoleRequirementService - Centralized, extensible role requirement provider for Skill Gap Analysis.

Key responsibilities:
- Normalize any role input (typos, casing, hyphens, aliases) to a canonical role name.
- Provide validated, role-specific skill requirements for 15+ canonical roles.
- Never use the role name itself as a skill.
- Extend dynamically for unknown roles without falling back to AI/ML Engineer.
- Provide a validation step to remove the target role name from the skill list.
"""
import logging
import re
from difflib import get_close_matches
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Proficiency level mappings
# ---------------------------------------------------------------------------
LEVEL_NUMERIC: Dict[str, int] = {
    "untested": 0,
    "not detected": 0,
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}

NUMERIC_TO_LEVEL: Dict[int, str] = {
    0: "Untested",
    1: "Beginner",
    2: "Intermediate",
    3: "Advanced",
    4: "Expert",
}

VALID_IMPORTANCE = {"critical", "high", "medium", "low"}


class RoleSkillRequirementSchema(BaseModel):
    """Validated, schema-enforced role skill requirement."""
    skill: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    required_level: str = Field(default="Intermediate")
    required_level_num: int = Field(default=2)
    importance: str = Field(default="high")
    weight: float = Field(default=0.8, ge=0.1, le=1.5)

    @field_validator("required_level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        clean = v.strip().title()
        if clean.lower() not in LEVEL_NUMERIC:
            return "Intermediate"
        return clean

    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v: str) -> str:
        clean = v.strip().lower()
        return clean if clean in VALID_IMPORTANCE else "medium"


# ---------------------------------------------------------------------------
# Centralized Role Requirements Registry — 15 canonical roles + extras
# ---------------------------------------------------------------------------
ROLE_REQUIREMENTS_REGISTRY: Dict[str, List[Dict[str, Any]]] = {

    # -------------------------------------------------------------------------
    "AI/ML Engineer": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "Mathematics",                 "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Mathematics",       "weight": 0.9},
        {"skill": "Statistics",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.9},
        {"skill": "Machine Learning",            "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Machine Learning",  "weight": 1.0},
        {"skill": "Deep Learning",               "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "NumPy",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Pandas",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Scikit-learn",                "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "PyTorch",                     "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Databases",         "weight": 0.7},
        {"skill": "MLOps",                       "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Backend Developer": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "Data Structures & Algorithms","required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "DSA",               "weight": 1.0},
        {"skill": "REST API",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Backend",           "weight": 1.0},
        {"skill": "System Design",               "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "CS Fundamentals",   "weight": 0.9},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "PostgreSQL",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "FastAPI",                     "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.8},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.8},
        {"skill": "Redis",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Databases",         "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Frontend Developer": [
        {"skill": "HTML/CSS",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Frontend",          "weight": 1.0},
        {"skill": "JavaScript",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "React",                       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Frontend",          "weight": 1.0},
        {"skill": "TypeScript",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Programming",       "weight": 0.9},
        {"skill": "State Management",            "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Frontend",          "weight": 0.8},
        {"skill": "REST API",                    "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.8},
        {"skill": "Responsive Design",           "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Frontend",          "weight": 0.8},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
        {"skill": "Web Performance",             "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Frontend",          "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Full Stack Developer": [
        {"skill": "JavaScript",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "HTML/CSS",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Frontend",          "weight": 1.0},
        {"skill": "React",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Frontend",          "weight": 0.9},
        {"skill": "Node.js",                     "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.9},
        {"skill": "REST API",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Backend",           "weight": 1.0},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "PostgreSQL",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "System Design",               "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "CS Fundamentals",   "weight": 0.8},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Data Scientist": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "Statistics",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Data Science",      "weight": 1.0},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "Pandas",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Data Science",      "weight": 1.0},
        {"skill": "NumPy",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Machine Learning",            "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "Scikit-learn",                "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "Data Visualization",          "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Feature Engineering",         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Exploratory Data Analysis",   "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Data Science",      "weight": 0.9},
    ],

    # -------------------------------------------------------------------------
    "Data Engineer": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "SQL",                         "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Databases",         "weight": 1.0},
        {"skill": "ETL Pipelines",               "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Data Engineering",  "weight": 1.0},
        {"skill": "PostgreSQL",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "Apache Spark",                "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Engineering",  "weight": 0.9},
        {"skill": "Kafka",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Engineering",  "weight": 0.8},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.8},
        {"skill": "Cloud Platforms",             "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Cloud",             "weight": 0.7},
        {"skill": "Data Structures & Algorithms","required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DSA",               "weight": 0.8},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "DevOps Engineer": [
        {"skill": "Linux",                       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "OS & Scripting",    "weight": 1.0},
        {"skill": "Docker",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "DevOps",            "weight": 1.0},
        {"skill": "CI/CD",                       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "DevOps",            "weight": 1.0},
        {"skill": "Kubernetes",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.9},
        {"skill": "Infrastructure as Code",      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.9},
        {"skill": "Monitoring & Alerting",       "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.8},
        {"skill": "Cloud Platforms",             "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Cloud",             "weight": 0.9},
        {"skill": "Python",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Programming",       "weight": 0.8},
        {"skill": "Networking",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Networking",        "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
    ],

    # -------------------------------------------------------------------------
    "Cybersecurity Analyst": [
        {"skill": "Networking",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Networking",        "weight": 1.0},
        {"skill": "Linux",                       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "OS & Scripting",    "weight": 1.0},
        {"skill": "Security Fundamentals",       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Security",          "weight": 1.0},
        {"skill": "SIEM",                        "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Security",          "weight": 0.9},
        {"skill": "Threat Detection",            "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Security",          "weight": 0.9},
        {"skill": "Incident Response",           "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Security",          "weight": 0.9},
        {"skill": "Vulnerability Management",    "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Security",          "weight": 0.8},
        {"skill": "Python",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Programming",       "weight": 0.8},
        {"skill": "Log Analysis",                "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Security",          "weight": 0.7},
        {"skill": "Operating Systems",           "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "CS Fundamentals",   "weight": 0.8},
    ],

    # -------------------------------------------------------------------------
    "Software Engineer": [
        {"skill": "Data Structures & Algorithms","required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "DSA",               "weight": 1.0},
        {"skill": "Object-Oriented Programming", "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "CS Fundamentals",   "weight": 1.0},
        {"skill": "Python",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Programming",       "weight": 0.9},
        {"skill": "System Design",               "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "CS Fundamentals",   "weight": 0.9},
        {"skill": "REST API",                    "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.8},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "Testing",                     "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Testing",           "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
        {"skill": "Operating Systems",           "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "CS Fundamentals",   "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Cloud Engineer": [
        {"skill": "Cloud Platforms",             "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Cloud",             "weight": 1.0},
        {"skill": "Linux",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "OS & Scripting",    "weight": 0.9},
        {"skill": "Docker",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "DevOps",            "weight": 1.0},
        {"skill": "Kubernetes",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.9},
        {"skill": "Infrastructure as Code",      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.9},
        {"skill": "Networking",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Networking",        "weight": 0.8},
        {"skill": "Security Fundamentals",       "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Security",          "weight": 0.7},
        {"skill": "Monitoring & Alerting",       "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Mobile App Developer": [
        {"skill": "JavaScript",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "React Native",                "required_level": "Intermediate",  "required_level_num": 2, "importance": "critical", "category": "Mobile",            "weight": 1.0},
        {"skill": "Mobile UI Design",            "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Mobile",            "weight": 0.9},
        {"skill": "REST API",                    "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.8},
        {"skill": "State Management",            "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Mobile",            "weight": 0.8},
        {"skill": "Local Storage & Caching",     "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Mobile",            "weight": 0.7},
        {"skill": "Testing",                     "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Testing",           "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "QA / Test Engineer": [
        {"skill": "Testing Fundamentals",        "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Testing",           "weight": 1.0},
        {"skill": "Test Case Design",            "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Testing",           "weight": 1.0},
        {"skill": "Automation Testing",          "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Testing",           "weight": 0.9},
        {"skill": "Selenium",                    "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Testing",           "weight": 0.9},
        {"skill": "REST API",                    "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.8},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "Python",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Programming",       "weight": 0.8},
        {"skill": "CI/CD",                       "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
        {"skill": "Bug Tracking",                "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Testing",           "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Database Engineer": [
        {"skill": "SQL",                         "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Databases",         "weight": 1.0},
        {"skill": "Database Design",             "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Databases",         "weight": 1.0},
        {"skill": "Query Optimization",          "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Databases",         "weight": 1.0},
        {"skill": "PostgreSQL",                  "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "MySQL",                       "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "Data Modeling",               "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "Indexing & Performance",      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "NoSQL Databases",             "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "Backup & Recovery",           "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Databases",         "weight": 0.7},
        {"skill": "Python",                      "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Programming",       "weight": 0.6},
    ],

    # -------------------------------------------------------------------------
    "Business Analyst": [
        {"skill": "Requirements Analysis",       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Business Analysis", "weight": 1.0},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.9},
        {"skill": "Data Analysis",               "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.9},
        {"skill": "Data Visualization",          "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Process Modeling",            "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Business Analysis", "weight": 0.8},
        {"skill": "Stakeholder Management",      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Business Analysis", "weight": 1.0},
        {"skill": "Documentation",               "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Business Analysis", "weight": 0.9},
        {"skill": "Agile Methodologies",         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Business Analysis", "weight": 0.7},
        {"skill": "Excel Modeling",              "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Data Science",      "weight": 0.7},
    ],

    # -------------------------------------------------------------------------
    "Product Manager": [
        {"skill": "Product Strategy",            "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Product Management","weight": 1.0},
        {"skill": "Requirements Analysis",       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Product Management","weight": 1.0},
        {"skill": "User Research",               "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Product Management","weight": 1.0},
        {"skill": "Product Analytics",           "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Product Management","weight": 0.9},
        {"skill": "Roadmapping",                 "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Product Management","weight": 0.9},
        {"skill": "Stakeholder Management",      "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Product Management","weight": 0.9},
        {"skill": "Agile Methodologies",         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Product Management","weight": 0.8},
        {"skill": "SQL",                         "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Databases",         "weight": 0.6},
        {"skill": "Data Visualization",          "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Data Science",      "weight": 0.7},
    ],

    # -------------------------------------------------------------------------
    # Additional specialist roles kept from previous version
    # -------------------------------------------------------------------------
    "ML Engineer": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "Machine Learning",            "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Machine Learning",  "weight": 1.0},
        {"skill": "Scikit-learn",                "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "PyTorch",                     "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.9},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DevOps",            "weight": 0.8},
        {"skill": "Data Structures & Algorithms","required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DSA",               "weight": 0.8},
        {"skill": "REST API",                    "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Backend",           "weight": 0.7},
    ],

    "Deep Learning Engineer": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "Deep Learning",               "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Machine Learning",  "weight": 1.0},
        {"skill": "PyTorch",                     "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Machine Learning",  "weight": 1.0},
        {"skill": "TensorFlow",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Machine Learning",  "weight": 0.8},
        {"skill": "Mathematics",                 "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Mathematics",       "weight": 0.9},
        {"skill": "Statistics",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    "Java Developer": [
        {"skill": "Java",                        "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "REST API",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Backend",           "weight": 0.9},
        {"skill": "Data Structures & Algorithms","required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "DSA",               "weight": 0.9},
        {"skill": "Spring Boot",                 "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Backend",           "weight": 0.9},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "System Design",               "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "CS Fundamentals",   "weight": 0.8},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    "Python Developer": [
        {"skill": "Python",                      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Programming",       "weight": 1.0},
        {"skill": "FastAPI",                     "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Backend",           "weight": 0.9},
        {"skill": "REST API",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Backend",           "weight": 0.9},
        {"skill": "Data Structures & Algorithms","required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "DSA",               "weight": 0.8},
        {"skill": "SQL",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "PostgreSQL",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Databases",         "weight": 0.8},
        {"skill": "Docker",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.7},
        {"skill": "Git",                         "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "DevOps",            "weight": 0.6},
    ],

    "Data Analyst": [
        {"skill": "SQL",                         "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Databases",         "weight": 1.0},
        {"skill": "Python",                      "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Programming",       "weight": 0.8},
        {"skill": "Data Visualization",          "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Data Science",      "weight": 0.9},
        {"skill": "Tableau",                     "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.8},
        {"skill": "Exploratory Data Analysis",   "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Data Science",      "weight": 0.9},
        {"skill": "Statistics",                  "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Data Science",      "weight": 0.7},
        {"skill": "Excel Modeling",              "required_level": "Intermediate",  "required_level_num": 2, "importance": "medium",   "category": "Data Science",      "weight": 0.7},
    ],

    "UI/UX Designer": [
        {"skill": "HTML/CSS",                    "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Frontend",          "weight": 1.0},
        {"skill": "Figma",                       "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Design",            "weight": 1.0},
        {"skill": "User Research",               "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Design",            "weight": 1.0},
        {"skill": "Wireframing & Prototyping",   "required_level": "Advanced",      "required_level_num": 3, "importance": "high",     "category": "Design",            "weight": 0.9},
        {"skill": "Design Systems",              "required_level": "Intermediate",  "required_level_num": 2, "importance": "high",     "category": "Design",            "weight": 0.9},
        {"skill": "JavaScript",                  "required_level": "Beginner",      "required_level_num": 1, "importance": "medium",   "category": "Programming",       "weight": 0.6},
        {"skill": "User Experience Design",      "required_level": "Advanced",      "required_level_num": 3, "importance": "critical", "category": "Design",            "weight": 1.0},
    ],
}


# ---------------------------------------------------------------------------
# Centralized Role Alias Registry — exact → canonical
# ---------------------------------------------------------------------------
ROLE_ALIASES: Dict[str, str] = {
    # AI / ML
    "ai/ml engineer":            "AI/ML Engineer",
    "ai ml engineer":            "AI/ML Engineer",
    "aiml engineer":             "AI/ML Engineer",
    "ai/ml":                     "AI/ML Engineer",
    "ai ml":                     "AI/ML Engineer",
    "ai engineer":               "AI/ML Engineer",
    "machine learning engineer": "ML Engineer",
    "ml engineer":               "ML Engineer",
    "ml":                        "ML Engineer",
    "deep learning engineer":    "Deep Learning Engineer",
    "dl engineer":               "Deep Learning Engineer",

    # Backend
    "backend developer":         "Backend Developer",
    "backend engineer":          "Backend Developer",
    "backend dev":               "Backend Developer",
    "back end developer":        "Backend Developer",
    "back-end developer":        "Backend Developer",
    "backend":                   "Backend Developer",
    "sde backend":               "Backend Developer",
    "java developer":            "Java Developer",
    "java engineer":             "Java Developer",
    "python developer":          "Python Developer",
    "python engineer":           "Python Developer",

    # Frontend
    "frontend developer":        "Frontend Developer",
    "frontend engineer":         "Frontend Developer",
    "frontend dev":              "Frontend Developer",
    "front end developer":       "Frontend Developer",
    "front-end developer":       "Frontend Developer",
    "frontend":                  "Frontend Developer",
    "ui developer":              "Frontend Developer",
    "react developer":           "Frontend Developer",

    # Full Stack
    "full stack developer":      "Full Stack Developer",
    "fullstack developer":       "Full Stack Developer",
    "full stack engineer":       "Full Stack Developer",
    "fullstack engineer":        "Full Stack Developer",
    "full stack dev":            "Full Stack Developer",
    "full-stack developer":      "Full Stack Developer",
    "full stack":                "Full Stack Developer",
    "fullstack":                 "Full Stack Developer",

    # Software Engineer
    "software engineer":         "Software Engineer",
    "software developer":        "Software Engineer",
    "sde":                       "Software Engineer",
    "swe":                       "Software Engineer",
    "sde 1":                     "Software Engineer",
    "sde1":                      "Software Engineer",

    # Data
    "data scientist":            "Data Scientist",
    "ds":                        "Data Scientist",
    "data analyst":              "Data Analyst",
    "da":                        "Data Analyst",
    "data engineer":             "Data Engineer",
    "de":                        "Data Engineer",
    "database engineer":         "Database Engineer",
    "database administrator":    "Database Engineer",
    "dba":                       "Database Engineer",

    # Infra / DevOps / Cloud / Security
    "devops engineer":           "DevOps Engineer",
    "devops":                    "DevOps Engineer",
    "dev ops engineer":          "DevOps Engineer",
    "cloud engineer":            "Cloud Engineer",
    "cloud architect":           "Cloud Engineer",
    "cloud developer":           "Cloud Engineer",
    "cybersecurity analyst":     "Cybersecurity Analyst",
    "cyber security analyst":    "Cybersecurity Analyst",
    "cybersecurity":             "Cybersecurity Analyst",
    "cyber security":            "Cybersecurity Analyst",
    "security analyst":          "Cybersecurity Analyst",
    "infosec analyst":           "Cybersecurity Analyst",

    # Testing
    "qa engineer":               "QA / Test Engineer",
    "qa":                        "QA / Test Engineer",
    "test engineer":             "QA / Test Engineer",
    "qa test engineer":          "QA / Test Engineer",
    "quality assurance engineer":"QA / Test Engineer",
    "quality assurance":         "QA / Test Engineer",
    "automation test engineer":  "QA / Test Engineer",
    "sdet":                      "QA / Test Engineer",

    # Product / Business / Design / Mobile
    "mobile app developer":      "Mobile App Developer",
    "mobile developer":          "Mobile App Developer",
    "android developer":         "Mobile App Developer",
    "ios developer":             "Mobile App Developer",
    "business analyst":          "Business Analyst",
    "ba":                        "Business Analyst",
    "product manager":           "Product Manager",
    "pm":                        "Product Manager",
    "ui/ux designer":            "UI/UX Designer",
    "ux designer":               "UI/UX Designer",
    "ui ux designer":            "UI/UX Designer",
    "product designer":          "UI/UX Designer",
    "ui designer":               "UI/UX Designer",
}


# ---------------------------------------------------------------------------
# Typo / phonetic correction dictionary — maps common misspellings to normalized keys
# ---------------------------------------------------------------------------
TYPO_CORRECTIONS: Dict[str, str] = {
    # Backend
    "backend develpoer":         "backend developer",
    "backend develper":          "backend developer",
    "backend devloper":          "backend developer",
    "backend develpoper":        "backend developer",
    "backend developr":          "backend developer",
    "backand developer":         "backend developer",
    "backen developer":          "backend developer",
    "backedn developer":         "backend developer",
    # Frontend
    "frontend develpoer":        "frontend developer",
    "frontend develper":         "frontend developer",
    "frontend devloper":         "frontend developer",
    "fronend developer":         "frontend developer",
    "forntend developer":        "frontend developer",
    # Full Stack
    "fullstak developer":        "full stack developer",
    "full stak developer":       "full stack developer",
    # Data
    "data sceintist":            "data scientist",
    "data scintist":             "data scientist",
    "data scientest":            "data scientist",
    "data analayst":             "data analyst",
    "data enigneer":             "data engineer",
    # DevOps
    "devops enigneer":           "devops engineer",
    "deovps engineer":           "devops engineer",
    # Cybersecurity
    "cybersecuity analyst":      "cybersecurity analyst",
    "cybersecrurity analyst":    "cybersecurity analyst",
    "cyberscurity analyst":      "cybersecurity analyst",
    # Software
    "softwre engineer":          "software engineer",
    "sofware engineer":          "software engineer",
    # AI/ML
    "ai ml enigneer":            "ai/ml engineer",
    "machine leraning engineer": "machine learning engineer",
}


class RoleNormalizationService:
    """
    Centralized service for normalizing arbitrary role input to a canonical form.

    Normalization pipeline (in order):
    1. Strip whitespace
    2. Lowercase + collapse hyphens/underscores/slashes to spaces
    3. Apply typo correction dictionary
    4. Exact alias match
    5. Registry direct match (after title-casing)
    6. Fuzzy match against alias keys
    7. Return cleaned title-cased version (unknown role, NOT a fallback to AI/ML)
    """

    @staticmethod
    def _normalize_for_lookup(raw: str) -> str:
        """Reduce raw role string to a normalized lookup key."""
        if not raw:
            return ""
        cleaned = raw.strip().lower()
        # Replace hyphens, underscores, slashes with space
        cleaned = re.sub(r"[-_/]+", " ", cleaned)
        # Collapse multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def normalize(cls, raw_role: str) -> str:
        """
        Resolve any role string to a canonical role name.
        Never silently falls back to a different role; returns the clean title
        of the input if no match is found.
        """
        if not raw_role or not raw_role.strip():
            return "Software Engineer"

        norm = cls._normalize_for_lookup(raw_role)

        # 1. Typo correction
        if norm in TYPO_CORRECTIONS:
            norm = TYPO_CORRECTIONS[norm]

        # 2. Exact alias match
        if norm in ROLE_ALIASES:
            return ROLE_ALIASES[norm]

        # 3. Direct registry match (after title-casing)
        title_cased = raw_role.strip().title()
        if title_cased in ROLE_REQUIREMENTS_REGISTRY:
            return title_cased

        # 4. Fuzzy match against alias keys using difflib
        alias_keys = list(ROLE_ALIASES.keys())
        close = get_close_matches(norm, alias_keys, n=1, cutoff=0.75)
        if close:
            matched_alias = close[0]
            canonical = ROLE_ALIASES[matched_alias]
            logger.info("Fuzzy role match: '%s' → '%s' (via '%s')", raw_role, canonical, matched_alias)
            return canonical

        # 5. Registry key fuzzy match
        registry_keys = list(ROLE_REQUIREMENTS_REGISTRY.keys())
        registry_norm = [k.lower() for k in registry_keys]
        close2 = get_close_matches(norm, registry_norm, n=1, cutoff=0.75)
        if close2:
            idx = registry_norm.index(close2[0])
            canonical = registry_keys[idx]
            logger.info("Fuzzy registry match: '%s' → '%s'", raw_role, canonical)
            return canonical

        # 6. Unknown role — return clean title-cased version, NOT a hardcoded role
        canonical_unknown = re.sub(r"[-_/]+", " ", raw_role.strip()).title()
        logger.info("Unknown role '%s' normalized to '%s' (no registry match).", raw_role, canonical_unknown)
        return canonical_unknown


class RoleRequirementService:
    """
    Centralized service providing dynamic, validated skill requirements for target roles.

    Order of resolution:
    1. Exact registry key match
    2. Normalized alias lookup
    3. Fuzzy match via RoleNormalizationService
    4. In-memory cache (for previously resolved dynamic roles)
    5. AI-service generation (if available)
    6. Deterministic dynamic generation for unknown roles
       — NEVER uses the role name itself as a skill
       — NEVER falls back to AI/ML Engineer requirements
    """

    def __init__(self, ai_client: Optional[Any] = None) -> None:
        self.ai_client = ai_client
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._normalizer = RoleNormalizationService()

    def normalize_role_key(self, raw_role: str) -> str:
        """Normalize for cache keying."""
        return RoleNormalizationService._normalize_for_lookup(raw_role)

    def get_canonical_role(self, raw_role: str) -> str:
        """Resolve any role string to its canonical registry name."""
        return RoleNormalizationService.normalize(raw_role)

    def get_requirements(self, target_role: str) -> List[Dict[str, Any]]:
        """
        Synchronously retrieve requirements for target_role.
        """
        canonical = self.get_canonical_role(target_role)
        norm_key = self.normalize_role_key(target_role)

        # 1. Configured registry (canonical)
        if canonical in ROLE_REQUIREMENTS_REGISTRY:
            return [dict(req) for req in ROLE_REQUIREMENTS_REGISTRY[canonical]]

        # 2. In-memory cache
        if norm_key in self._cache:
            return [dict(req) for req in self._cache[norm_key]]

        # 3. Dynamic generation for unlisted/custom roles
        dynamic_reqs = self._generate_dynamic_requirements(canonical)
        self._cache[norm_key] = dynamic_reqs
        return dynamic_reqs

    async def get_requirements_async(self, target_role: str) -> List[Dict[str, Any]]:
        """
        Asynchronously retrieve requirements, with optional AI-service augmentation for unknown roles.
        """
        canonical = self.get_canonical_role(target_role)
        norm_key = self.normalize_role_key(target_role)

        # 1. Check registry
        if canonical in ROLE_REQUIREMENTS_REGISTRY:
            return [dict(req) for req in ROLE_REQUIREMENTS_REGISTRY[canonical]]

        # 2. Cache
        if norm_key in self._cache:
            return [dict(req) for req in self._cache[norm_key]]

        # 3. Try AI service (with static-fallback guard)
        if self.ai_client:
            try:
                ai_reqs = await self._fetch_ai_role_requirements(canonical)
                if ai_reqs:
                    self._cache[norm_key] = ai_reqs
                    return ai_reqs
            except Exception as e:
                logger.warning("AI role requirement generation fallback for '%s': %s", canonical, e)

        # 4. Deterministic dynamic generation
        dynamic_reqs = self._generate_dynamic_requirements(canonical)
        self._cache[norm_key] = dynamic_reqs
        return dynamic_reqs

    def _generate_dynamic_requirements(self, role_title: str) -> List[Dict[str, Any]]:
        """
        Generate structured, validated requirements for any custom/unlisted role.

        CRITICAL: The role name itself is NEVER used as a skill name here.
        Generic engineer competencies are used instead.
        """
        # Universal competencies that apply to virtually all engineering roles
        raw_items = [
            {
                "skill": "Data Structures & Algorithms",
                "category": "DSA",
                "required_level": "Intermediate",
                "required_level_num": 2,
                "importance": "high",
                "weight": 0.9,
            },
            {
                "skill": "System Design",
                "category": "CS Fundamentals",
                "required_level": "Intermediate",
                "required_level_num": 2,
                "importance": "high",
                "weight": 0.8,
            },
            {
                "skill": "Python",
                "category": "Programming",
                "required_level": "Intermediate",
                "required_level_num": 2,
                "importance": "high",
                "weight": 0.8,
            },
            {
                "skill": "REST API",
                "category": "Backend",
                "required_level": "Intermediate",
                "required_level_num": 2,
                "importance": "medium",
                "weight": 0.7,
            },
            {
                "skill": "Git",
                "category": "DevOps",
                "required_level": "Intermediate",
                "required_level_num": 2,
                "importance": "medium",
                "weight": 0.6,
            },
            {
                "skill": "SQL",
                "category": "Databases",
                "required_level": "Beginner",
                "required_level_num": 1,
                "importance": "medium",
                "weight": 0.6,
            },
        ]

        validated: List[Dict[str, Any]] = []
        for item in raw_items:
            try:
                model = RoleSkillRequirementSchema.model_validate(item)
                validated.append(model.model_dump())
            except Exception:
                continue

        return validated

    async def _fetch_ai_role_requirements(self, role_title: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch AI-generated role requirements with static-fallback rejection guard."""
        if not hasattr(self.ai_client, "analyze_skill_gaps"):
            return None

        payload = {"target_role": role_title, "profile": {}}
        res = await self.ai_client.analyze_skill_gaps(payload)
        if not res or not isinstance(res, dict) or "skills" not in res:
            return None

        raw_skills = {item.get("skill", "") for item in res.get("skills", []) if isinstance(item, dict)}

        # Guard against known static fallbacks from the AI microservice
        _known_static_sets = [
            {"Python", "Data Structures & Algorithms", "REST API", "FastAPI", "PostgreSQL", "Docker", "System Design", "Redis", "Git"},
            {"Python", "PyTorch", "Scikit-learn", "Data Structures & Algorithms", "Deep Learning", "Statistics", "Docker", "REST API", "TensorFlow"},
        ]
        for fallback_set in _known_static_sets:
            if raw_skills == fallback_set:
                logger.info("AI microservice returned static fallback for '%s'; using dynamic generation.", role_title)
                return None

        validated: List[Dict[str, Any]] = []
        for item in res.get("skills", []):
            if not isinstance(item, dict):
                continue
            skill_name = item.get("skill", "").strip()
            if not skill_name:
                continue
            req_lvl = item.get("required_level", "Intermediate")
            req_lvl_num = LEVEL_NUMERIC.get(req_lvl.lower(), 2)
            req_obj = {
                "skill": skill_name,
                "category": item.get("category", "General Engineering"),
                "required_level": req_lvl,
                "required_level_num": req_lvl_num,
                "importance": item.get("importance", "high"),
                "weight": float(item.get("weight", 0.8)),
            }
            try:
                schema_model = RoleSkillRequirementSchema.model_validate(req_obj)
                validated.append(schema_model.model_dump())
            except Exception:
                continue

        return validated if len(validated) >= 3 else None
