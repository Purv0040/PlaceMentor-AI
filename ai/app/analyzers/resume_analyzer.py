import logging
from app.services.llm_service import LLMService
from app.services.parser_service import ParserService
from app.schemas.resume import LLMResumeExtraction, ResumeAnalysis
from app.engines.profile_engine import ProfileEngine
from app.prompts.resume_prompts import RESUME_EXTRACTION_PROMPT
from app.schemas.resume import ScoreDetail

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """Orchestrates the resume analysis pipeline."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.engine = ProfileEngine()
        
    def analyze_pdf(self, pdf_bytes: bytes) -> ResumeAnalysis:
        """Extracts text from PDF and analyzes it."""
        logger.info("Extracting text from PDF...")
        text = ParserService.extract_text_from_pdf(pdf_bytes)
        return self.analyze_text(text)
        
    def analyze_text(self, text: str) -> ResumeAnalysis:
        """Analyzes extracted text using LLM and deterministic scoring."""
        logger.info("Generating structured extraction via LLM...")
        
        prompt = RESUME_EXTRACTION_PROMPT.format(resume_text=text)
        
        # We allow up to 3 retries for this complex extraction
        llm_extraction = self.llm_service.generate_structured(
            prompt=prompt,
            response_model=LLMResumeExtraction,
            max_retries=3
        )
        
        logger.info("Calculating deterministic scores...")
        
        # Deterministic Scoring
        projects_score = self.engine.calculate_projects_score(llm_extraction)
        skills_score = self.engine.calculate_skills_score(llm_extraction)
        experience_score = self.engine.calculate_experience_score(llm_extraction)
        impact_score = self.engine.calculate_impact_score(llm_extraction)
        formatting_score = self.engine.calculate_formatting_score(llm_extraction)
        
        overall_score = self.engine.calculate_overall_ats_score(llm_extraction)
        
        # A simple internal ATS score (overall score wrapped in ScoreDetail)
        ats_score = ScoreDetail(
            score=overall_score,
            reason="Internal assessment based on weighted average of Experience, Projects, Skills, Impact, and Formatting."
        )
        
        # Generate high-level suggestions based on scores and missing items
        suggestions = []
        if llm_extraction.missing_sections:
            suggestions.append(f"Add missing sections: {', '.join(llm_extraction.missing_sections)}.")
        if llm_extraction.keyword_gaps:
            suggestions.append(f"Consider adding these expected keywords if you have experience with them: {', '.join(llm_extraction.keyword_gaps)}.")
        if impact_score.score < 80:
            suggestions.append("Improve bullet points by adding quantifiable metrics and avoiding generic phrases.")
        if len(suggestions) == 0:
            suggestions.append("Keep your resume updated with your latest achievements!")

        # Construct final analysis
        analysis = ResumeAnalysis(
            ats_score=ats_score,
            skills_score=skills_score,
            projects_score=projects_score,
            experience_score=experience_score,
            formatting_score=formatting_score,
            impact_score=impact_score,
            overall_score=overall_score,
            suggestions=suggestions,
            extracted_skills=llm_extraction.skills,
            education=llm_extraction.education,
            experience=llm_extraction.experience,
            projects=llm_extraction.projects,
            certifications=llm_extraction.certifications,
            achievements=llm_extraction.achievements,
            missing_sections=llm_extraction.missing_sections,
            weak_bullets=llm_extraction.weak_bullets,
            repeated_words=llm_extraction.repeated_words,
            generic_phrases=llm_extraction.generic_phrases,
            keyword_gaps=llm_extraction.keyword_gaps
        )
        
        logger.info("Resume analysis complete.")
        return analysis
