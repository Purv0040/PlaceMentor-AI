"""Constants used across the Resume Analyzer services and scoring modules."""

from typing import Dict, List

# Section Header Aliases
SECTION_PATTERNS: Dict[str, List[str]] = {
    "Education": [
        "education", "academic background", "academic qualifications",
        "scholastic achievements", "educational background", "qualification"
    ],
    "Experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "internships", "internship experience"
    ],
    "Projects": [
        "projects", "academic projects", "personal projects",
        "key projects", "capstone project", "software projects"
    ],
    "Skills": [
        "skills", "technical skills", "core skills", "technical expertise",
        "competencies", "key skills", "tech stack", "skills & tools"
    ],
    "Certifications": [
        "certifications", "licenses & certifications", "courses",
        "professional certifications", "certificates"
    ],
    "Achievements": [
        "achievements", "honors", "awards & achievements",
        "accomplishments", "extracurricular achievements", "highlights"
    ],
    "Summary": [
        "summary", "professional summary", "profile", "about me",
        "career objective", "objective", "executive summary"
    ],
    "Languages": [
        "languages", "languages spoken", "known languages", "language proficiency"
    ]
}

# Strong Action Verbs for Resume Impact Check
ACTION_VERBS: List[str] = [
    "accelerated", "achieved", "architected", "automated", "built", "created",
    "designed", "developed", "deployed", "directed", "engineered", "established",
    "implemented", "improved", "increased", "integrated", "launched", "lead",
    "managed", "migrated", "optimized", "orchestrated", "refactored", "reduced",
    "spearheaded", "streamlined", "transformed", "upgraded"
]

# Contact Information & Links Regex Patterns
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REGEX = r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}"
LINKEDIN_REGEX = r"linkedin\.com/in/[a-zA-Z0-9_-]+"
GITHUB_REGEX = r"github\.com/[a-zA-Z0-9_-]+"
PORTFOLIO_REGEX = r"(https?://(?:www\.)?(?!linkedin\.com|github\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?)"

# Category Lists
SKILL_CATEGORIES = [
    "Programming Languages",
    "Frontend",
    "Backend",
    "Databases",
    "Cloud",
    "DevOps",
    "AI/ML",
    "Data Science",
    "Testing",
    "Tools"
]
