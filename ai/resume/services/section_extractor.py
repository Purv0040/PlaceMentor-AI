"""Module 3: Resume Section Extractor Service.

Parses cleaned resume text and detects standard sections (Education, Experience, Projects,
Skills, Certifications, Achievements, Summary, Languages) using Regex header matching.
"""

import re
from typing import Dict, List
from models.resume import SectionDetail
from utils.constants import SECTION_PATTERNS
from utils.helpers import count_words
from utils.logger import log_execution_time


class SectionExtractorService:
    """Service to parse and categorize resume text into standard sections."""

    def __init__(self):
        self.section_compiled_patterns = self._build_compiled_patterns()

    def _build_compiled_patterns(self) -> Dict[str, re.Pattern]:
        compiled = {}
        for canonical_name, aliases in SECTION_PATTERNS.items():
            pattern_str = r"^(?:[#*•\-\s]*)(?:" + "|".join(re.escape(a) for a in aliases) + r")(?:\s*[:|-]|\s*$)"
            compiled[canonical_name] = re.compile(pattern_str, re.IGNORECASE | re.MULTILINE)
        return compiled

    @log_execution_time
    def extract_sections(self, clean_text: str) -> Dict[str, SectionDetail]:
        """Detect and extract standard sections from clean resume text.

        Args:
            clean_text: Clean normalized resume text.

        Returns:
            Dictionary mapping canonical section name to SectionDetail model.
        """
        lines = clean_text.splitlines()
        header_positions = []

        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str or len(line_str) > 60:
                continue

            for canonical_name, pattern in self.section_compiled_patterns.items():
                if pattern.match(line_str):
                    header_positions.append((idx, canonical_name))
                    break

        sections_result: Dict[str, SectionDetail] = {
            sec: SectionDetail(present=False, text="", word_count=0)
            for sec in SECTION_PATTERNS.keys()
        }

        if not header_positions:
            sections_result["Experience"] = SectionDetail(
                present=False,
                text=clean_text,
                word_count=count_words(clean_text)
            )
            return sections_result

        for i in range(len(header_positions)):
            start_line_idx, section_name = header_positions[i]
            end_line_idx = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(lines)

            content_lines = lines[start_line_idx + 1: end_line_idx]
            section_text = "\n".join(content_lines).strip()

            existing = sections_result[section_name]
            combined_text = (existing.text + "\n" + section_text).strip() if existing.present else section_text

            sections_result[section_name] = SectionDetail(
                present=True,
                text=combined_text,
                word_count=count_words(combined_text)
            )

        return sections_result

    def detect_missing_sections(self, sections: Dict[str, SectionDetail]) -> List[str]:
        """Identify missing key sections from the extracted sections dictionary.

        Args:
            sections: Dictionary mapping section name to SectionDetail.

        Returns:
            List of missing section names (e.g. ['Certifications', 'Summary', 'Achievements']).
        """
        essential_list = ["Experience", "Projects", "Education", "Skills", "Certifications", "Achievements", "Summary", "Languages"]
        missing = []
        for name in essential_list:
            detail = sections.get(name)
            if not detail or not detail.present:
                missing.append(name)
        return missing


# Singleton Service Instance
section_extractor_service = SectionExtractorService()
