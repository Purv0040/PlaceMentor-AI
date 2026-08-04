"""Unit tests for Module 6: Suggestion Engine Service."""

from services.suggestion_engine import suggestion_engine_service
from services.ats_scorer import ats_scorer_service
from models.resume import SectionDetail, SkillsSummary, ContactInfo


def test_generate_suggestions_missing_sections():
    """Test generating suggestions when Experience and Projects are missing."""
    empty_sections = {
        "Education": SectionDetail(present=True, text="B.Tech CS", word_count=2),
        "Experience": SectionDetail(present=False, text="", word_count=0),
        "Projects": SectionDetail(present=False, text="", word_count=0)
    }
    empty_skills = SkillsSummary()
    no_contact = ContactInfo()
    ats_breakdown = ats_scorer_service.calculate_score(
        empty_sections, empty_skills, no_contact, 50, "B.Tech CS"
    )

    suggestions = suggestion_engine_service.generate_suggestions(
        sections=empty_sections,
        skills_summary=empty_skills,
        contact_info=no_contact,
        ats_breakdown=ats_breakdown,
        total_word_count=50,
        full_text="B.Tech CS"
    )

    assert len(suggestions) > 0
    categories = {s.category for s in suggestions}
    assert "Experience" in categories
    assert "Projects" in categories
    assert suggestions[0].priority == "HIGH"
