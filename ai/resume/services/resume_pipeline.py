"""Module 7: Orchestrator Resume Processing Pipeline Service.

Coordinates text extraction, cleaning, metadata extraction, section parsing,
skill matching, ATS scoring, missing section detection, and suggestion generation.
"""

import io
import time
from typing import Union
from config import settings
from models.resume import (
    ResumeAnalysisResponse,
    ResumeStatistics,
    ContactInfo
)
from services.pdf_parser import pdf_parser_service
from services.text_cleaner import text_cleaner_service
from services.section_extractor import section_extractor_service
from services.skill_extractor import skill_extractor_service
from services.metadata_extractor import metadata_extractor_service
from services.ats_scorer import ats_scorer_service
from services.suggestion_engine import suggestion_engine_service
from utils.helpers import extract_contact_info, count_words
from utils.logger import logger, log_execution_time


class ResumePipeline:
    """Orchestrating pipeline service executing all analysis stages for an uploaded resume."""

    @log_execution_time
    def process_resume(
        self,
        pdf_input: Union[bytes, str, io.BytesIO],
        filename: str
    ) -> ResumeAnalysisResponse:
        """Run complete end-to-end analysis on PDF resume file.

        Args:
            pdf_input: Raw bytes or stream of PDF.
            filename: Original file name.

        Returns:
            Structured ResumeAnalysisResponse Pydantic model.
        """
        start_time = time.perf_counter()
        logger.info(f"Starting analysis pipeline for resume file: {filename}")

        # Step 1: Extract Text & Page Count
        parse_start = time.perf_counter()
        raw_text, pages_count = pdf_parser_service.extract_text_and_page_count(pdf_input)
        parse_end = time.perf_counter()
        parsing_time = f"{(parse_end - parse_start):.2f} sec"
        logger.info(f"Step 1 Complete: Extracted {len(raw_text)} raw characters across {pages_count} page(s) in {parsing_time}.")

        # Step 2: Clean Text
        clean_text = text_cleaner_service.clean_text(raw_text)
        total_word_count = count_words(clean_text)
        logger.info(f"Step 2 Complete: Cleaned text word count = {total_word_count}.")

        # Step 3: Metadata Extraction
        resume_metadata = metadata_extractor_service.extract_metadata(clean_text)
        logger.info("Step 3 Complete: Candidate metadata extracted.")

        # Step 4: Extract Sections & Missing Sections
        sections = section_extractor_service.extract_sections(clean_text)
        detected_sections_count = sum(1 for s in sections.values() if s.present)
        missing_sections = section_extractor_service.detect_missing_sections(sections)
        logger.info(f"Step 4 Complete: Detected {detected_sections_count} sections, {len(missing_sections)} missing.")

        # Step 5: Extract Technical Skills
        skills_summary = skill_extractor_service.extract_skills(clean_text, sections)
        logger.info(
            f"Step 5 Complete: Extracted {skills_summary.total_skills_count} unique skills "
            f"across {skills_summary.unique_categories_count} categories."
        )

        # Step 6: Contact Info Helper
        contact_dict = extract_contact_info(clean_text)
        contact_info = ContactInfo(**contact_dict)

        # Step 7: Section-wise and Overall ATS Score
        section_ats_score, ats_breakdown = ats_scorer_service.calculate_score(
            sections=sections,
            skills_summary=skills_summary,
            contact_info=contact_info,
            total_word_count=total_word_count,
            full_text=clean_text
        )
        logger.info(f"Step 6 & 7 Complete: Calculated overall ATS score = {section_ats_score.overall}/100.")

        # Step 8: Generate Improvement Suggestions
        suggestions = suggestion_engine_service.generate_suggestions(
            sections=sections,
            skills_summary=skills_summary,
            contact_info=contact_info,
            ats_breakdown=ats_breakdown,
            total_word_count=total_word_count,
            full_text=clean_text
        )
        logger.info(f"Step 8 Complete: Generated {len(suggestions)} improvement suggestions.")

        # Step 9: Measure processing time
        elapsed_seconds = time.perf_counter() - start_time
        processing_time_str = f"{elapsed_seconds:.2f} seconds"

        # Step 10: Build and return structured response
        statistics = ResumeStatistics(
            total_pages=pages_count,
            total_words=total_word_count,
            total_characters=len(clean_text),
            number_of_skills_found=skills_summary.total_skills_count,
            number_of_sections_found=detected_sections_count,
            has_contact_info={
                "email": bool(contact_info.email),
                "phone": bool(contact_info.phone),
                "linkedin": bool(contact_info.linkedin),
                "github": bool(contact_info.github),
                "portfolio": bool(contact_info.portfolio)
            }
        )

        formatted_sections = {
            name: {
                "present": detail.present,
                "text": detail.text,
                "word_count": detail.word_count
            }
            for name, detail in sections.items() if detail.present
        }

        # Deduplicate and sort skills
        unique_skills = {}
        for s in skills_summary.detected_skills:
            if s.name not in unique_skills or s.confidence > unique_skills[s.name].confidence:
                unique_skills[s.name] = s

        formatted_skills = [
            {"skill": s.name, "confidence": s.confidence, "category": s.category}
            for s in sorted(unique_skills.values(), key=lambda x: x.name)
        ]

        formatted_suggestions = [
            {"category": s.category, "message": s.message, "priority": s.priority, "estimated_impact": s.estimated_impact}
            for s in suggestions
        ]

        return ResumeAnalysisResponse(
            success=True,
            version="1.0.0",
            processing_time=processing_time_str,
            resume_metadata=resume_metadata,
            statistics=statistics,
            ats_score=section_ats_score,
            sections=formatted_sections,
            skills=formatted_skills,
            missing_sections=missing_sections,
            suggestions=formatted_suggestions
        )


# Singleton Pipeline Instance
resume_pipeline = ResumePipeline()
