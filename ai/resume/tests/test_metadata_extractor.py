"""Unit tests for Metadata Extractor Service."""

from services.metadata_extractor import metadata_extractor_service


def test_extract_metadata_full(sample_resume_text: str):
    """Test extracting full candidate metadata from resume text."""
    meta = metadata_extractor_service.extract_metadata(sample_resume_text)

    assert meta.full_name is not None
    assert "John Doe" in meta.full_name

    assert meta.email == "john.doe@example.com"

    assert meta.phone_number is not None

    assert meta.linkedin_url == "https://linkedin.com/in/johndoe"

    assert meta.github_url == "https://github.com/johndoe"


def test_extract_metadata_missing():
    """Test metadata extraction when fields are missing."""
    text = "Just some text without contact info or name."
    meta = metadata_extractor_service.extract_metadata(text)

    assert meta.email is None
    assert meta.linkedin_url is None
