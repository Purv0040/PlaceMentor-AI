"""Module 2: Text Cleaning & Normalization Service.

Sanitizes raw extracted resume text by fixing line-wrap hyphenations,
normalizing Unicode, removing non-printable characters, duplicate spaces, and empty lines.
"""

import re
import unicodedata

from utils.logger import log_execution_time


class TextCleanerService:
    """Service to clean and normalize raw resume text extracted from PDFs."""

    @log_execution_time
    def clean_text(self, raw_text: str) -> str:
        """Clean and normalize raw text string.

        Args:
            raw_text: Raw string extracted from PDF.

        Returns:
            Normalized, clean text string.
        """
        if not raw_text:
            return ""

        # 1. Normalize Unicode (NFKC form converts compatibility characters to standard representation)
        text = unicodedata.normalize("NFKC", raw_text)

        # 2. Fix hyphenated broken words across line breaks (e.g. "de- \n velopment" -> "development")
        text = re.sub(r"(\b[a-zA-Z]+)-\s*\n\s*([a-zA-Z]+\b)", r"\1\2", text)

        # 3. Remove control characters / non-printable characters except standard newlines and tabs
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\r", "\t"))

        # 4. Convert tab spaces to standard single space
        text = text.replace("\t", " ")

        # 5. Remove trailing whitespaces on each line
        lines = [line.strip() for line in text.splitlines()]

        # 6. Collapse multiple empty lines into a single blank line
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if not line:
                if not prev_empty:
                    cleaned_lines.append("")
                    prev_empty = True
            else:
                # 7. Replace internal multiple consecutive spaces with a single space
                line_single_space = re.sub(r"[ \t]+", " ", line)
                cleaned_lines.append(line_single_space)
                prev_empty = False

        return "\n".join(cleaned_lines).strip()


# Singleton Service Instance
text_cleaner_service = TextCleanerService()
