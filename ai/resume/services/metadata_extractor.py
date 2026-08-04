"""Module: Metadata Extractor Service.

Extracts candidate personal metadata (Full Name, Email, Phone, LinkedIn, GitHub, Portfolio URL)
with confidence scores (0.0 to 1.0).
"""

import re
from typing import Optional
import spacy

from config import settings
from models.resume import ResumeMetadata
from utils.constants import EMAIL_REGEX, PHONE_REGEX, LINKEDIN_REGEX, GITHUB_REGEX, PORTFOLIO_REGEX
from utils.logger import logger, log_execution_time


class MetadataExtractorService:
    """Service to extract student metadata from resume text with confidence scores."""

    def __init__(self):
        self.nlp = self._init_spacy()

    def _init_spacy(self):
        try:
            return spacy.load(settings.SPACY_MODEL)
        except Exception:
            return spacy.blank("en")

    @log_execution_time
    def extract_metadata(self, full_text: str) -> ResumeMetadata:
        """Extract full name, email, phone, linkedin, github, and portfolio url.

        Args:
            full_text: Full clean text of the resume.

        Returns:
            ResumeMetadata Pydantic model.
        """
        email_item = self._extract_email(full_text)
        phone_item = self._extract_phone(full_text)
        linkedin_item = self._extract_linkedin(full_text)
        github_item = self._extract_github(full_text)
        portfolio_item = self._extract_portfolio(full_text)
        name_item = self._extract_full_name(full_text)

        return ResumeMetadata(
            full_name=name_item,
            email=email_item,
            phone_number=phone_item,
            linkedin_url=linkedin_item,
            github_url=github_item,
            portfolio_website=portfolio_item,
        )

    def _extract_location(self, text: str) -> MetadataItem:
        """Extract candidate city/location from header text with confidence score."""
        lines = [line.strip() for line in text.splitlines() if line.strip()][:5]
        header_text = "\n".join(lines)
        doc = self.nlp(header_text)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                loc_val = ent.text.strip()
                if len(loc_val) >= 2 and not re.search(r"\d", loc_val):
                    return MetadataItem(value=loc_val.title(), confidence=0.85)

        location_pattern = r"\b(Bangalore|Bengaluru|Mumbai|Delhi|New Delhi|Hyderabad|Pune|Chennai|Kolkata|Noida|Gurgaon|Gurugram|Ahmedabad|Jaipur|Chandigarh|Kochi|Indore|Vadodara|Surat|India)\b"
        match = re.search(location_pattern, header_text, re.IGNORECASE)
        if match:
            return MetadataItem(value=match.group(0).title(), confidence=0.80)
        return MetadataItem(value=None, confidence=0.0)

    def _extract_email(self, text: str) -> Optional[str]:
        match = re.search(EMAIL_REGEX, text)
        if match:
            return match.group(0)
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        match = re.search(PHONE_REGEX, text)
        if match:
            raw_phone = match.group(0).strip()
            # Basic validation check (digits >= 10)
            digits = re.sub(r"\D", "", raw_phone)
            if len(digits) >= 10:
                return raw_phone
        return None

    def _extract_linkedin(self, text: str) -> Optional[str]:
        match = re.search(LINKEDIN_REGEX, text, re.IGNORECASE)
        if match:
            url = f"https://{match.group(0)}"
            return url
        return None

    def _extract_github(self, text: str) -> Optional[str]:
        match = re.search(GITHUB_REGEX, text, re.IGNORECASE)
        if match:
            url = f"https://{match.group(0)}"
            return url
        return None

    def _extract_portfolio(self, text: str) -> Optional[str]:
        match = re.search(PORTFOLIO_REGEX, text, re.IGNORECASE)
        if match:
            url = match.group(0).strip()
            return url
        return None

    def _extract_full_name(self, text: str) -> Optional[str]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return None

        # Look at the top 5 non-empty lines for candidate name
        candidate_lines = lines[:5]

        # 1. spaCy NER entity check on top header section
        header_text = "\n".join(candidate_lines)
        doc = self.nlp(header_text)

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                clean_name = ent.text.strip()
                # Ensure name is 2-4 words, contains only alphabetic characters
                words = clean_name.split()
                if 2 <= len(words) <= 4 and all(w.isalpha() for w in words):
                    return clean_name.title()

        # 2. Heuristic check on line 1 / line 2 (skipping emails/links)
        for line in candidate_lines:
            # Skip lines containing email, github, linkedin, or numbers
            if "@" in line or "github" in line.lower() or "linkedin" in line.lower() or re.search(r"\d", line):
                continue

            words = line.split()
            if 2 <= len(words) <= 4 and all(re.match(r"^[a-zA-Z.'\s]+$", w) for w in words):
                name = " ".join(words).title()
                return name

        # Fallback to line 1 if reasonable word count
        first_line_words = lines[0].split()
        if 1 <= len(first_line_words) <= 4:
            clean_first = re.sub(r"[^a-zA-Z\s]", "", lines[0]).strip()
            if clean_first:
                return clean_first.title()

        return None


# Singleton Service Instance
metadata_extractor_service = MetadataExtractorService()
