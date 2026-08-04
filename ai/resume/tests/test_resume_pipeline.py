"""Unit tests for Module 7: Resume Pipeline Service."""

from services.resume_pipeline import resume_pipeline


def test_process_resume_end_to_end(sample_pdf_bytes: bytes):
    """Test full end-to-end processing pipeline using in-memory PDF."""
    response = resume_pipeline.process_resume(sample_pdf_bytes, filename="test_resume.pdf")

    assert response.success is True
    assert response.version == "1.0.0"
    assert "seconds" in response.processing_time

    # Section-wise ATS score check
    assert 0 <= response.ats_score.overall <= 100
    assert 0 <= response.ats_score.contact <= 100

    # Metadata check
    assert response.resume_metadata.email == "john.doe@example.com"

    # Statistics check
    assert response.statistics.total_pages >= 1
    assert response.statistics.total_words > 0
    assert response.statistics.total_characters > 0
    assert response.statistics.number_of_skills_found > 0

    # Sections & Missing sections check
    assert any(s["name"] == "Education" for s in response.sections)
    assert isinstance(response.missing_sections, list)

    # Skills check
    assert len(response.skills) > 0
    assert any("Programming Languages" in s.get("category", "") for s in response.skills)

    # Suggestions check
    assert isinstance(response.suggestions, list)
