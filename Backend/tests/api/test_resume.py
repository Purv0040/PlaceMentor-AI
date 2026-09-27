import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

def test_resume_upload_and_list_endpoints(client: TestClient, auth_headers: dict):
    # 1. Upload valid PDF
    pdf_content = b"%PDF-1.4 test resume pdf content"
    files = {"file": ("test_resume.pdf", pdf_content, "application/pdf")}
    res = client.post("/api/v1/resume/upload", files=files, headers=auth_headers)
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["filename"] == "test_resume.pdf"
    resume_id = body["data"]["id"]

    # 2. List resumes
    res_list = client.get("/api/v1/resume", headers=auth_headers)
    assert res_list.status_code == 200
    list_body = res_list.json()
    assert list_body["success"] is True
    assert list_body["data"]["total"] >= 1

    # 3. Get resume detail
    res_detail = client.get(f"/api/v1/resume/{resume_id}", headers=auth_headers)
    assert res_detail.status_code == 200
    detail_body = res_detail.json()
    assert detail_body["data"]["id"] == resume_id

    # 4. Download file
    res_file = client.get(f"/api/v1/resume/{resume_id}/file", headers=auth_headers)
    assert res_file.status_code == 200
    assert res_file.content == pdf_content

    # 5. Analyze resume with mocked AIClient response
    mock_ai_output = {
        "overall_score": 88,
        "ats_score": {"score": 88, "reason": "High benchmark compliance"},
        "skills_score": {"score": 90, "reason": "Strong skill set"},
        "projects_score": {"score": 85, "reason": "Good engineering scale"},
        "experience_score": {"score": 80, "reason": "STAR formatted"},
        "formatting_score": {"score": 95, "reason": "Clean layout"},
        "impact_score": {"score": 82, "reason": "Quantified bullets"},
        "suggestions": ["Add Redis distributed caching pattern evidence."],
        "extracted_skills": {"languages": ["Python", "TypeScript"], "frameworks": ["FastAPI", "React"]},
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "missing_sections": [],
        "weak_bullets": [],
        "repeated_words": [],
        "generic_phrases": [],
        "keyword_gaps": ["Redis", "Kafka"]
    }

    with patch("app.integrations.ai_client.AIClient.analyze_resume_pdf", new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = mock_ai_output
        res_analyze = client.post(f"/api/v1/resume/{resume_id}/analyze", headers=auth_headers)
        assert res_analyze.status_code == 200
        analyze_body = res_analyze.json()
        assert analyze_body["success"] is True
        assert analyze_body["data"]["analysis"]["overall_score"] == 88

    # 6. Delete resume
    res_del = client.delete(f"/api/v1/resume/{resume_id}", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["data"]["deleted"] is True
