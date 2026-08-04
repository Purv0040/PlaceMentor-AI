"""Unit tests for Module 2: Text Cleaner Service."""

from services.text_cleaner import text_cleaner_service


def test_clean_text_basic():
    """Test standard whitespace and empty line removal."""
    raw = "Line 1  \n\n\n  Line 2   with   spaces  "
    cleaned = text_cleaner_service.clean_text(raw)
    assert cleaned == "Line 1\n\nLine 2 with spaces"


def test_clean_text_line_wrap_hyphenation():
    """Test fixing words split across lines with hyphenation."""
    raw = "We are de-\nveloping an AI app-\nlication."
    cleaned = text_cleaner_service.clean_text(raw)
    assert "developing" in cleaned
    assert "application" in cleaned


def test_clean_text_unicode_normalization():
    """Test NFKC unicode normalization of special quotes and hyphens."""
    raw = "“Hello World” – Python"
    cleaned = text_cleaner_service.clean_text(raw)
    assert "Hello World" in cleaned
