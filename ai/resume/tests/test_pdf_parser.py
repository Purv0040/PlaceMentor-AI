"""Unit tests for Module 1: PDF Parser Service."""

import pytest
from services.pdf_parser import pdf_parser_service
from utils.exceptions import InvalidPDFError, EmptyResumeError


def test_extract_text_valid_pdf(sample_pdf_bytes: bytes):
    """Test extracting text from valid PyMuPDF-generated PDF bytes."""
    extracted = pdf_parser_service.extract_text(sample_pdf_bytes)
    assert isinstance(extracted, str)
    assert "JOHN DOE" in extracted
    assert "Education" in extracted
    assert "Python" in extracted


def test_extract_text_empty_input():
    """Test passing empty bytes raises EmptyResumeError or InvalidPDFError."""
    with pytest.raises((InvalidPDFError, EmptyResumeError)):
        pdf_parser_service.extract_text(b"")


def test_extract_text_corrupted_pdf():
    """Test passing invalid non-PDF bytes raises InvalidPDFError."""
    with pytest.raises(InvalidPDFError):
        pdf_parser_service.extract_text(b"Not a real PDF file content")
