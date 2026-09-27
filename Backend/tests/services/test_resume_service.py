import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.resume_service import ResumeService

@pytest.mark.asyncio
async def test_upload_resume_invalid_file(mock_db):
    service = ResumeService(mock_db)

    # Invalid extension
    with pytest.raises(HTTPException) as exc_info:
        await service.upload_resume(
            user_id="u123",
            file_bytes=b"invalid content",
            original_filename="document.docx",
            content_type="application/word"
        )
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_upload_resume_oversized(mock_db):
    service = ResumeService(mock_db)
    huge_bytes = b"x" * (6 * 1024 * 1024) # 6MB

    with pytest.raises(HTTPException) as exc_info:
        await service.upload_resume(
            user_id="u123",
            file_bytes=huge_bytes,
            original_filename="huge.pdf",
            content_type="application/pdf"
        )
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_upload_and_activate_resume(mock_db):
    service = ResumeService(mock_db)
    valid_pdf_bytes = b"%PDF-1.4 sample content"

    r1 = await service.upload_resume(
        user_id="u123",
        file_bytes=valid_pdf_bytes,
        original_filename="resume_v1.pdf"
    )
    assert r1["is_active"] is True

    r2 = await service.upload_resume(
        user_id="u123",
        file_bytes=valid_pdf_bytes,
        original_filename="resume_v2.pdf"
    )
    assert r2["is_active"] is False

    # Activate r2
    activated = await service.activate_resume(r2["id"], "u123")
    assert activated["is_active"] is True

    # r1 should now be inactive
    r1_updated = await service.get_resume_by_id(r1["id"], "u123")
    assert r1_updated["is_active"] is False
