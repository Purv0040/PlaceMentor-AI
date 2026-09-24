import pytest
import fitz
from fastapi.testclient import TestClient
from app.main import app
from app.analyzers.resume_analyzer import ResumeAnalyzer
from app.schemas.resume import LLMResumeExtraction, ExtractedSkills, Education, Experience, Project, WeakBullet
from app.services.parser_service import PDFExtractionError, ParserService

client = TestClient(app)

# Helper to create a dummy PDF in memory
def create_dummy_pdf_bytes(text: str = "Dummy PDF Content") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), text)
    return doc.write()

# --- FIXTURES FOR LLM MOCKS ---

@pytest.fixture
def mock_llm_strong_resume(monkeypatch):
    """Mocks the LLM generating a perfect resume extraction."""
    def mock_generate_structured(*args, **kwargs):
        return LLMResumeExtraction(
            skills=ExtractedSkills(languages=["Python"], frameworks=["FastAPI"], tools=["Git"], other=[]),
            education=[Education(institution="MIT", degree="B.S. CS")],
            experience=[
                Experience(company="Google", role="SWE", bullets=["Optimized backend API reducing latency by 40%"]),
                Experience(company="Startup Inc", role="Intern", bullets=["Built frontend using React"])
            ],
            projects=[
                Project(name="AI Bot", technologies=["Python", "LLM"], bullets=["Built a chatbot scaling to 10k MAU"], has_metrics=True),
                Project(name="E-Commerce API", technologies=["Node.js", "MongoDB"], bullets=["Processed $1M in transactions"], has_metrics=True)
            ],
            certifications=[],
            achievements=[],
            missing_sections=[],
            weak_bullets=[],
            repeated_words=[],
            generic_phrases=[],
            keyword_gaps=[]
        )
    monkeypatch.setattr("app.services.llm_service.LLMService.generate_structured", mock_generate_structured)

@pytest.fixture
def mock_llm_weak_resume(monkeypatch):
    """Mocks the LLM generating a weak resume with missing metrics and sections."""
    def mock_generate_structured(*args, **kwargs):
        return LLMResumeExtraction(
            skills=ExtractedSkills(languages=["HTML"], frameworks=[], tools=[], other=[]),
            education=[],  # Missing
            experience=[Experience(company="Startup", role="Dev", bullets=["Did some coding", "Helped the team"])],
            projects=[], # Missing
            certifications=[],
            achievements=[],
            missing_sections=["Education", "Projects"],
            weak_bullets=[
                WeakBullet(
                    original_bullet="Did some coding",
                    issues=["Vague", "No impact"],
                    suggestion="Developed web features using HTML.",
                    evidence_used=["HTML skill"]
                )
            ],
            repeated_words=["helped", "team"],
            generic_phrases=["team player"],
            keyword_gaps=["JavaScript", "CSS"]
        )
    monkeypatch.setattr("app.services.llm_service.LLMService.generate_structured", mock_generate_structured)

# --- TESTS ---

def test_pdf_extraction_valid():
    """Test PDF text extraction works on valid PDFs."""
    pdf_bytes = create_dummy_pdf_bytes("Hello World")
    text = ParserService.extract_text_from_pdf(pdf_bytes)
    assert "Hello World" in text

def test_pdf_extraction_empty():
    """Test PDF extraction raises error on empty bytes."""
    with pytest.raises(PDFExtractionError):
        ParserService.extract_text_from_pdf(b"")

def test_analyze_strong_resume(mock_llm_strong_resume):
    """Test that a strong resume gets high scores."""
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze_text("Dummy Text")
    
    assert result.impact_score.score == 100
    assert result.formatting_score.score == 100
    assert result.projects_score.score >= 50
    assert len(result.suggestions) == 1 # "Keep your resume updated..."
    assert result.overall_score >= 80

def test_analyze_weak_resume(mock_llm_weak_resume):
    """Test that a weak resume gets lower scores and proper suggestions."""
    analyzer = ResumeAnalyzer()
    result = analyzer.analyze_text("Dummy Text")
    
    assert result.impact_score.score < 100
    assert result.formatting_score.score < 100
    assert result.projects_score.score == 0
    assert len(result.suggestions) > 1
    assert "Add missing sections: Education, Projects" in result.suggestions[0]

def test_api_analyze_text(mock_llm_strong_resume):
    """Test the /api/ai/resume/analyze-text endpoint."""
    response = client.post("/api/ai/resume/analyze-text", json={"text": "Here is my resume..."})
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] >= 80
    assert len(data["extracted_skills"]["languages"]) == 1

def test_api_analyze_text_empty():
    """Test the /api/ai/resume/analyze-text endpoint with empty text."""
    response = client.post("/api/ai/resume/analyze-text", json={"text": "   "})
    assert response.status_code == 400

def test_api_analyze_pdf(mock_llm_strong_resume):
    """Test the /api/ai/resume/analyze endpoint with file upload."""
    pdf_bytes = create_dummy_pdf_bytes("My Resume Text")
    
    files = {"file": ("resume.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/ai/resume/analyze", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] >= 80

def test_api_analyze_pdf_invalid_type():
    """Test the /api/ai/resume/analyze endpoint with wrong file type."""
    files = {"file": ("resume.txt", b"Just text", "text/plain")}
    response = client.post("/api/ai/resume/analyze", files=files)
    assert response.status_code == 400
