"""Module 5: ATS Scoring Engine Service.

Evaluates resume content across dimensions (Essential Sections, Technical Skills,
Projects & Experience, Contact Info, Structure & Quality) to calculate overall and
section-wise ATS scores out of 100.
"""

from typing import Dict, Tuple
from config import settings
from models.resume import ATSBreakdown, SectionATSScore, SectionDetail, SkillsSummary, ContactInfo
from utils.helpers import extract_action_verbs
from utils.logger import log_execution_time


class ATSScorerService:
    """Service to compute section-wise and overall ATS scores out of 100."""

    @log_execution_time
    def calculate_score(
        self,
        sections: Dict[str, SectionDetail],
        skills_summary: SkillsSummary,
        contact_info: ContactInfo,
        total_word_count: int,
        full_text: str
    ) -> Tuple[SectionATSScore, ATSBreakdown]:
        """Calculate section-wise ATS scores and legacy breakdown.

        Args:
            sections: Extracted section details dictionary.
            skills_summary: Summary of extracted skills.
            contact_info: Extracted contact information.
            total_word_count: Overall word count of clean text.
            full_text: Full clean text string.

        Returns:
            Tuple of (SectionATSScore, ATSBreakdown).
        """
        # --- Section-wise 0-100 Scores ---

        # 1. Contact Information Score (100 max)
        contact_pts = 0
        if contact_info.email:
            contact_pts += 20
        if contact_info.phone:
            contact_pts += 20
        if contact_info.linkedin:
            contact_pts += 20
        if contact_info.github:
            contact_pts += 20
        if contact_info.portfolio:
            contact_pts += 20
        contact_section_score = min(contact_pts, 100)

        # 2. Education Section Score (100 max)
        edu_detail = sections.get("Education", SectionDetail(present=False))
        edu_score = 100 if edu_detail.present and edu_detail.word_count >= 5 else (50 if edu_detail.present else 0)

        # 3. Skills Section Score (100 max)
        skill_qty_pts = min(skills_summary.total_skills_count * 5, 60)
        skill_div_pts = min(skills_summary.unique_categories_count * 10, 40)
        skills_section_score = min(skill_qty_pts + skill_div_pts, 100)

        # 4. Projects Section Score (100 max)
        proj_detail = sections.get("Projects", SectionDetail(present=False))
        if proj_detail.present:
            proj_score = 100 if proj_detail.word_count >= 80 else (60 if proj_detail.word_count >= 30 else 30)
        else:
            proj_score = 0

        # 5. Experience Section Score (100 max)
        exp_detail = sections.get("Experience", SectionDetail(present=False))
        if exp_detail.present:
            exp_score = 100 if exp_detail.word_count >= 80 else (60 if exp_detail.word_count >= 30 else 30)
        else:
            exp_score = 0

        # 6. Certifications Section Score (100 max)
        cert_detail = sections.get("Certifications", SectionDetail(present=False))
        cert_score = 100 if cert_detail.present and cert_detail.word_count >= 3 else 0

        # 7. Achievements Section Score (100 max)
        achieve_detail = sections.get("Achievements", SectionDetail(present=False))
        achieve_score = 100 if achieve_detail.present and achieve_detail.word_count >= 3 else 0

        # --- Weighted Legacy Scores for Overall Score Computation ---
        essential_score = (edu_score * 0.08) + (exp_score * 0.08) + (proj_score * 0.08) + ((100 if sections.get("Skills", SectionDetail(present=False)).present else 0) * 0.06)
        essential_score = min(essential_score, 30.0)

        skills_score = (skills_section_score / 100.0) * 30.0
        projects_exp_score = ((proj_score + exp_score) / 200.0) * 20.0
        contact_score = (contact_section_score / 100.0) * 10.0

        struct_score = 0.0
        if 300 <= total_word_count <= 1200:
            struct_score += 4.0
        elif 150 <= total_word_count < 300 or 1200 < total_word_count <= 1800:
            struct_score += 2.0

        action_verbs = extract_action_verbs(full_text)
        if len(action_verbs) >= 5:
            struct_score += 3.0
        elif len(action_verbs) >= 2:
            struct_score += 1.5

        if cert_detail.present or achieve_detail.present:
            struct_score += 3.0
        structure_score = min(struct_score, 10.0)

        overall = int(round(essential_score + skills_score + projects_exp_score + contact_score + structure_score))
        overall = max(min(overall, 100), 0)

        section_ats_score = SectionATSScore(
            overall=overall,
            contact=contact_section_score,
            education=edu_score,
            skills=skills_section_score,
            projects=proj_score,
            experience=exp_score,
            certifications=cert_score,
            achievements=achieve_score
        )

        legacy_breakdown = ATSBreakdown(
            total_score=overall,
            essential_sections_score=round(essential_score, 1),
            technical_skills_score=round(skills_score, 1),
            projects_experience_score=round(projects_exp_score, 1),
            contact_info_score=round(contact_score, 1),
            structure_score=round(structure_score, 1)
        )

        return section_ats_score, legacy_breakdown


# Singleton Service Instance
ats_scorer_service = ATSScorerService()
