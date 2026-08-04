"""Unit tests for Module 4: Skill Extractor Service."""

from services.skill_extractor import skill_extractor_service
from services.section_extractor import section_extractor_service


def test_extract_skills_from_sample_text(sample_resume_text: str):
    """Test skill extraction from full sample resume text."""
    sections = section_extractor_service.extract_sections(sample_resume_text)
    summary = skill_extractor_service.extract_skills(sample_resume_text, sections)

    assert summary.total_skills_count > 5
    assert summary.unique_categories_count >= 3

    detected_names = {s.name for s in summary.detected_skills}
    assert "Python" in detected_names
    assert "FastAPI" in detected_names
    assert "Docker" in detected_names
    assert "PostgreSQL" in detected_names


def test_extract_skills_aliases():
    """Test alias resolution e.g. ReactJS -> React, JS -> JavaScript."""
    text = "Proficient in ReactJS, nodejs, postgresql, and JS."
    sections = section_extractor_service.extract_sections(text)
    summary = skill_extractor_service.extract_skills(text, sections)

    detected_names = {s.name for s in summary.detected_skills}
    assert "React" in detected_names
    assert "Node.js" in detected_names
    assert "PostgreSQL" in detected_names
    assert "JavaScript" in detected_names
