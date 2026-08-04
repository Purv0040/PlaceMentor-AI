"""Module 4: Technical Skill Extraction Service.

Loads technical skill dataset from skills.csv and matches skills within resume sections
using spaCy PhraseMatcher, token boundary regexes, and alias maps.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import spacy
from spacy.matcher import PhraseMatcher

from config import settings
from models.resume import SkillItem, SkillsSummary, SectionDetail
from utils.exceptions import SkillDatasetError
from utils.logger import logger, log_execution_time


class SkillExtractorService:
    """Service to load skill taxonomy and extract skills using spaCy PhraseMatcher."""

    def __init__(self, dataset_path: Path = settings.SKILLS_CSV_PATH):
        self.dataset_path = dataset_path
        self.nlp = self._init_spacy()
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        self.skill_metadata: Dict[str, Dict[str, str]] = {}  # alias_lower -> {canonical, category}
        self.canonical_skills: Dict[str, str] = {}  # canonical_name -> category
        self.load_dataset()

    def _init_spacy(self):
        """Initialize spaCy English pipeline with fallback to blank model."""
        try:
            return spacy.load(settings.SPACY_MODEL)
        except Exception:
            logger.warning(
                f"spaCy model '{settings.SPACY_MODEL}' not found. Falling back to spacy.blank('en')."
            )
            return spacy.blank("en")

    def load_dataset(self) -> None:
        """Load skills CSV dataset and populate matcher and lookup tables."""
        if not self.dataset_path.exists():
            logger.error(f"Skill dataset not found at path: {self.dataset_path}")
            raise SkillDatasetError(f"Skills dataset missing at {self.dataset_path}")

        try:
            patterns = []
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    canonical_name = row["skill_name"].strip()
                    category = row["category"].strip()
                    aliases_str = row.get("aliases", "")

                    if not canonical_name:
                        continue

                    self.canonical_skills[canonical_name] = category

                    # Register canonical name
                    aliases = [canonical_name]
                    if aliases_str:
                        aliases.extend([a.strip() for a in aliases_str.split("|") if a.strip()])

                    for alias in aliases:
                        alias_lower = alias.lower()
                        self.skill_metadata[alias_lower] = {
                            "canonical": canonical_name,
                            "category": category
                        }
                        patterns.append(self.nlp.make_doc(alias_lower))

            if patterns:
                self.matcher.add("SKILL_MATCHER", patterns)
            logger.info(f"Loaded {len(self.canonical_skills)} skills with {len(self.skill_metadata)} aliases.")

        except Exception as e:
            logger.error(f"Error reading skills dataset: {e}")
            raise SkillDatasetError(f"Failed to parse skill dataset CSV: {e}")

    @log_execution_time
    def extract_skills(
        self,
        full_text: str,
        sections: Dict[str, SectionDetail]
    ) -> SkillsSummary:
        """Extract technical skills across all sections of the resume.

        Args:
            full_text: Complete clean text of the resume.
            sections: Dictionary of extracted section details.

        Returns:
            SkillsSummary model with detected skills and category breakdown.
        """
        detected_dict: Dict[str, SkillItem] = {}

        # 1. Search section-by-section first to record accurate source_section
        for section_name, section_detail in sections.items():
            if section_detail.present and section_detail.text:
                sec_skills = self._search_text(section_detail.text, source_section=section_name)
                for skill_item in sec_skills:
                    existing = detected_dict.get(skill_item.name)
                    if not existing or skill_item.confidence > existing.confidence:
                        detected_dict[skill_item.name] = skill_item

        # 2. Search full text as fallback for any skills not captured in explicit sections
        full_text_skills = self._search_text(full_text, source_section="General")
        for skill_item in full_text_skills:
            existing = detected_dict.get(skill_item.name)
            if not existing or skill_item.confidence > existing.confidence:
                detected_dict[skill_item.name] = skill_item

        detected_items = sorted(detected_dict.values(), key=lambda x: x.name)

        # 3. Build category grouping
        by_category: Dict[str, List[str]] = {}
        for item in detected_items:
            by_category.setdefault(item.category, []).append(item.name)

        # Deduplicate names within categories
        for cat in by_category:
            by_category[cat] = sorted(list(set(by_category[cat])))

        return SkillsSummary(
            detected_skills=detected_items,
            skills_by_category=by_category,
            total_skills_count=len(detected_items),
            unique_categories_count=len(by_category)
        )

    def _search_text(self, text: str, source_section: str) -> List[SkillItem]:
        """Match skill phrases within text segment."""
        results: List[SkillItem] = []
        if not text:
            return results

        doc = self.nlp(text.lower())
        matches = self.matcher(doc)

        seen_in_segment: Set[str] = set()

        for match_id, start, end in matches:
            matched_span = doc[start:end].text.strip()
            meta = self.skill_metadata.get(matched_span)
            if meta:
                canonical = meta["canonical"]
                category = meta["category"]

                # Word boundary check for short aliases (e.g. 'c', 'r', 'js')
                if len(matched_span) <= 2:
                    pattern = rf"\b{re.escape(matched_span)}\b"
                    if not re.search(pattern, text, re.IGNORECASE):
                        continue

                if canonical not in seen_in_segment:
                    seen_in_segment.add(canonical)
                    results.append(
                        SkillItem(
                            name=canonical,
                            category=category,
                            source_section=source_section,
                            confidence=1.0
                        )
                    )

        return results


# Singleton Service Instance
skill_extractor_service = SkillExtractorService()
