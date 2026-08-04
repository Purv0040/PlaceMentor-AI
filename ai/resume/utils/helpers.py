"""Utility helper functions for string, file, and metrics processing."""

import re
from typing import Dict, List, Optional
from utils.constants import EMAIL_REGEX, PHONE_REGEX, LINKEDIN_REGEX, GITHUB_REGEX, ACTION_VERBS


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """Extract email, phone, LinkedIn, and GitHub links from resume text."""
    email_match = re.search(EMAIL_REGEX, text)
    phone_match = re.search(PHONE_REGEX, text)
    linkedin_match = re.search(LINKEDIN_REGEX, text, re.IGNORECASE)
    github_match = re.search(GITHUB_REGEX, text, re.IGNORECASE)

    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": f"https://{linkedin_match.group(0)}" if linkedin_match else None,
        "github": f"https://{github_match.group(0)}" if github_match else None
    }


def count_words(text: str) -> int:
    """Return total word count of non-empty tokens."""
    return len(re.findall(r"\b\w+\b", text))


def extract_action_verbs(text: str) -> List[str]:
    """Find action verbs used in resume text."""
    found_verbs = []
    text_lower = text.lower()
    for verb in ACTION_VERBS:
        if re.search(rf"\b{verb}\b", text_lower):
            found_verbs.append(verb)
    return found_verbs
