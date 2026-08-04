"""Unit tests for Module 5: ATS Scorer Service."""

from services.ats_scorer import ats_scorer_service


def test_calculate_score(sample_sections, sample_skills_summary, sample_contact_info, sample_resume_text):
    """Test ATS score calculation for a comprehensive resume."""
    word_count = len(sample_resume_text.split())
    section_score, breakdown = ats_scorer_service.calculate_score(
        sections=sample_sections,
        skills_summary=sample_skills_summary,
        contact_info=sample_contact_info,
        total_word_count=word_count,
        full_text=sample_resume_text
    )

    assert 0 <= section_score.overall <= 100
    assert 0 <= section_score.education <= 100
    assert 0 <= section_score.skills <= 100
    assert 0 <= section_score.projects <= 100
    assert 0 <= section_score.contact <= 100

    assert 0 <= breakdown.total_score <= 100
    assert breakdown.essential_sections_score > 0
    assert breakdown.technical_skills_score > 0
    assert breakdown.contact_info_score > 0
