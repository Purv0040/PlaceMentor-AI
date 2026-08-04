"""Module 6: Resume Improvement Suggestion Engine Service.

Generates targeted, prioritized actionable feedback based on missing sections,
skill coverage gaps, contact details, action verb usage, and length statistics.
"""

from typing import Dict, List
from models.resume import Suggestion, SectionDetail, SkillsSummary, ContactInfo, ATSBreakdown
from utils.helpers import extract_action_verbs
from utils.logger import log_execution_time


class SuggestionEngineService:
    """Service to analyze resume audit metrics and output prioritized suggestions."""

    @log_execution_time
    def generate_suggestions(
        self,
        sections: Dict[str, SectionDetail],
        skills_summary: SkillsSummary,
        contact_info: ContactInfo,
        ats_breakdown: ATSBreakdown,
        total_word_count: int,
        full_text: str
    ) -> List[Suggestion]:
        """Analyze resume metrics and produce list of actionable suggestions.

        Args:
            sections: Extracted section details.
            skills_summary: Summary of detected technical skills.
            contact_info: Extracted contact information.
            ats_breakdown: ATS score breakdown.
            total_word_count: Total word count.
            full_text: Full clean text string.

        Returns:
            List of Suggestion Pydantic models ordered by priority.
        """
        suggestions: List[Suggestion] = []

        # 1. Check Missing Essential Sections
        if not sections.get("Experience", SectionDetail(present=False)).present:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Experience",
                    message="Missing 'Experience' or 'Work History' section. Adding internship or work experience significantly boosts recruiter response rates.",
                    estimated_impact="+15 pts"
                )
            )

        if not sections.get("Projects", SectionDetail(present=False)).present:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Projects",
                    message="Missing 'Projects' section. Include 2-3 technical projects with GitHub repository links and tech stack highlights.",
                    estimated_impact="+12 pts"
                )
            )

        if not sections.get("Education", SectionDetail(present=False)).present:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Education",
                    message="Missing explicit 'Education' section. Include college degree, university name, graduation year, and CGPA.",
                    estimated_impact="+10 pts"
                )
            )

        if not sections.get("Skills", SectionDetail(present=False)).present:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Skills",
                    message="Missing dedicated 'Skills' section. Group technical competencies into categories like Languages, Frameworks, and Tools.",
                    estimated_impact="+8 pts"
                )
            )

        # 2. Check Contact Details
        if not contact_info.github:
            suggestions.append(
                Suggestion(
                    priority="MEDIUM",
                    category="Contact Info",
                    message="Missing GitHub profile link. Including your active GitHub link is crucial for software engineering applications.",
                    estimated_impact="+5 pts"
                )
            )

        if not contact_info.linkedin:
            suggestions.append(
                Suggestion(
                    priority="MEDIUM",
                    category="Contact Info",
                    message="Missing LinkedIn profile URL. Ensure a clean LinkedIn profile link (e.g. linkedin.com/in/username) is present.",
                    estimated_impact="+5 pts"
                )
            )

        if not contact_info.email or not contact_info.phone:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Contact Info",
                    message="Incomplete contact details. Ensure professional email and phone number are clearly visible at top of resume.",
                    estimated_impact="+6 pts"
                )
            )

        # 3. Check Technical Skills Count & Variety
        if skills_summary.total_skills_count < 5:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Skills",
                    message="Low technical skill count detected. Add specific programming languages, frameworks, and tools you have worked with.",
                    estimated_impact="+10 pts"
                )
            )
        elif skills_summary.unique_categories_count < 3:
            suggestions.append(
                Suggestion(
                    priority="MEDIUM",
                    category="Skills",
                    message="Limited skill category diversity. Diversify your skills across Databases, Cloud/DevOps, or Backend frameworks.",
                    estimated_impact="+5 pts"
                )
            )

        # 4. Action Verbs Impact Check
        action_verbs = extract_action_verbs(full_text)
        if len(action_verbs) < 4:
            suggestions.append(
                Suggestion(
                    priority="MEDIUM",
                    category="Content Impact",
                    message="Weak action verbs detected. Begin bullet points with strong verbs like 'Architected', 'Spearheaded', 'Optimized', or 'Automated'.",
                    estimated_impact="+5 pts"
                )
            )

        # 5. Check Certifications & Achievements
        has_cert = sections.get("Certifications", SectionDetail(present=False)).present
        has_achieve = sections.get("Achievements", SectionDetail(present=False)).present
        if not has_cert and not has_achieve:
            suggestions.append(
                Suggestion(
                    priority="LOW",
                    category="Certifications & Achievements",
                    message="Consider adding relevant certifications (e.g., AWS, Cloud, HackerRank) or competitive coding achievements.",
                    estimated_impact="+4 pts"
                )
            )

        # 6. Word Count & Length Suggestions
        if total_word_count < 250:
            suggestions.append(
                Suggestion(
                    priority="HIGH",
                    category="Formatting & Depth",
                    message="Resume text is too brief (<250 words). Expand project descriptions and outline responsibilities and key achievements.",
                    estimated_impact="+10 pts"
                )
            )
        elif total_word_count > 1200:
            suggestions.append(
                Suggestion(
                    priority="LOW",
                    category="Formatting & Depth",
                    message="Resume is overly verbose (>1200 words). Concise single-page or 2-page formats (400-800 words) perform best in ATS filters.",
                    estimated_impact="+3 pts"
                )
            )

        # Sort priority order: HIGH -> MEDIUM -> LOW
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))

        return suggestions


# Singleton Service Instance
suggestion_engine_service = SuggestionEngineService()
