"""Unit tests for Module 3: Section Extractor Service."""

from services.section_extractor import section_extractor_service


def test_extract_sections_all_present(sample_resume_text: str):
    """Test detecting standard sections in sample resume text."""
    sections = section_extractor_service.extract_sections(sample_resume_text)

    assert sections["Education"].present is True
    assert "Computer Science" in sections["Education"].text

    assert sections["Experience"].present is True
    assert "Tech Corp" in sections["Experience"].text

    assert sections["Projects"].present is True
    assert "AI Resume Analyzer" in sections["Projects"].text

    assert sections["Skills"].present is True
    assert "Python" in sections["Skills"].text

    assert sections["Certifications"].present is True
    assert sections["Achievements"].present is True


def test_extract_sections_missing_sections():
    """Test text with only Education section."""
    text = "Education\nB.Tech in IT"
    sections = section_extractor_service.extract_sections(text)
    assert sections["Education"].present is True
    assert sections["Projects"].present is False
    assert sections["Experience"].present is False

    missing = section_extractor_service.detect_missing_sections(sections)
    assert "Projects" in missing
    assert "Experience" in missing
    assert "Certifications" in missing
