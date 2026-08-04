"""Integration tests for FastAPI REST API endpoints using TestClient."""

import io
import fitz
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert "version" in json_data


def test_analyze_resume_success(sample_pdf_bytes: bytes):
    """Test POST /api/v1/resume/analyze with valid PDF upload."""
    files = {
        "file": ("resume.pdf", sample_pdf_bytes, "application/pdf")
    }
    response = client.post("/api/v1/resume/analyze", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["version"] == "1.0.0"
    assert "resume_metadata" in data
    assert "statistics" in data
    assert "ats_score" in data
    assert isinstance(data["sections"], list)
    assert isinstance(data["skills"], list)
    assert isinstance(data["suggestions"], list)


def test_analyze_resume_invalid_extension():
    """Test POST /api/v1/resume/analyze with non-PDF file."""
    files = {
        "file": ("document.docx", b"dummy content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    response = client.post("/api/v1/resume/analyze", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["message"]


def test_analyze_resume_corrupt_pdf():
    """Test POST /api/v1/resume/analyze with corrupted PDF payload."""
    files = {
        "file": ("corrupt.pdf", b"Not a pdf file", "application/pdf")
    }
    response = client.post("/api/v1/resume/analyze", files=files)
    assert response.status_code in [400, 422]

def test_api_upload_large_file():
    """Test POST /api/v1/resume/analyze with file larger than 5MB."""
    from config import settings
    large_content = b"0" * (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 10)
    files = {
        "file": ("large.pdf", large_content, "application/pdf")
    }
    response = client.post("/api/v1/resume/analyze", files=files)
    assert response.status_code == 413
    assert "exceeds" in response.json()["message"]

def test_api_upload_empty_file():
    """Test POST /api/v1/resume/analyze with empty file."""
    files = {
        "file": ("empty.pdf", b"", "application/pdf")
    }
    response = client.post("/api/v1/resume/analyze", files=files)
    assert response.status_code == 422
    assert "empty" in response.json()["message"]
