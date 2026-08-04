"""Pytest fixtures for unit testing the AI Resume Analyzer services."""

import io
import fitz  # PyMuPDF
import pytest
from models.resume import SectionDetail, SkillsSummary, SkillItem, ContactInfo, ATSBreakdown


@pytest.fixture
def sample_resume_text() -> str:
    """Return a standard sample resume text string for testing."""
    return """
    JOHN DOE
    Email: john.doe@example.com | Phone: +91 9876543210
    LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

    Education
    Bachelor of Technology in Computer Science
    ABC Institute of Technology, CGPA: 8.8 (2020 - 2024)

    Experience
    Software Engineer Intern - Tech Corp (May 2023 - Aug 2023)
    - Architected and deployed microservices using Python, FastAPI, and PostgreSQL.
    - Automated CI/CD deployment pipelines using Docker, Kubernetes, and GitHub Actions.
    - Optimized database queries resulting in a 35% speed improvement.

    Projects
    AI Resume Analyzer
    - Built a high-performance REST API backend with Python, FastAPI, spaCy, and PyMuPDF.
    - Integrated phrase matching for automated technical skill extraction.

    Skills
    Technical Skills: Python, Java, C++, JavaScript, TypeScript, React, Node.js, FastAPI, Django,
    PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS, PyTorch, TensorFlow, Git.

    Certifications
    AWS Certified Solutions Architect Associate (2023)

    Achievements
    Winner of National AI Hackathon 2023 among 500+ competing teams.
    """


@pytest.fixture
def sample_pdf_bytes(sample_resume_text: str) -> bytes:
    """Create an in-memory PDF document using PyMuPDF fitz and return bytes."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), sample_resume_text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def sample_sections() -> dict:
    """Sample parsed sections dictionary."""
    return {
        "Education": SectionDetail(present=True, text="B.Tech Computer Science CGPA 8.8", word_count=5),
        "Experience": SectionDetail(present=True, text="Software Engineer Intern at Tech Corp...", word_count=85),
        "Projects": SectionDetail(present=True, text="AI Resume Analyzer built with FastAPI...", word_count=90),
        "Skills": SectionDetail(present=True, text="Python, FastAPI, Docker, PostgreSQL", word_count=10),
        "Certifications": SectionDetail(present=True, text="AWS Certified", word_count=2),
        "Achievements": SectionDetail(present=True, text="Hackathon Winner", word_count=2)
    }


@pytest.fixture
def sample_skills_summary() -> SkillsSummary:
    """Sample SkillsSummary model."""
    skills = [
        SkillItem(name="Python", category="Programming Languages", source_section="Skills"),
        SkillItem(name="FastAPI", category="Backend", source_section="Skills"),
        SkillItem(name="React", category="Frontend", source_section="Skills"),
        SkillItem(name="PostgreSQL", category="Databases", source_section="Skills"),
        SkillItem(name="Docker", category="DevOps", source_section="Skills"),
        SkillItem(name="AWS", category="Cloud", source_section="Skills"),
    ]
    return SkillsSummary(
        detected_skills=skills,
        skills_by_category={
            "Programming Languages": ["Python"],
            "Backend": ["FastAPI"],
            "Frontend": ["React"],
            "Databases": ["PostgreSQL"],
            "DevOps": ["Docker"],
            "Cloud": ["AWS"]
        },
        total_skills_count=6,
        unique_categories_count=6
    )


@pytest.fixture
def sample_contact_info() -> ContactInfo:
    """Sample ContactInfo model."""
    return ContactInfo(
        email="john.doe@example.com",
        phone="+91 9876543210",
        linkedin="https://linkedin.com/in/johndoe",
        github="https://github.com/johndoe"
    )
