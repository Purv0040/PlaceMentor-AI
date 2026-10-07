import pytest
from app.schemas.project import ProjectAnalyzeRequest
from app.engines.project_engine import ProjectIntelligenceEngine, classify_project_type, perform_ast_code_audit


def test_classify_project_type():
    data_frontend = {
        "title": "Simple Student Portfolio Website",
        "description": "Personal website displaying resume and projects",
        "technologies": ["HTML", "CSS", "JavaScript"]
    }
    assert classify_project_type(data_frontend) == "frontend"

    data_ml = {
        "title": "Machine Learning House Price Prediction",
        "description": "Predicting residential property prices using regression models",
        "technologies": ["Python", "Pandas", "NumPy", "Scikit-learn", "Matplotlib"]
    }
    assert classify_project_type(data_ml) == "machine_learning"

    data_fullstack = {
        "title": "PlaceMentor AI — SDE Placement Copilot",
        "description": "Full-stack AI placement mentoring platform featuring AST code audit.",
        "category": "Full Stack / AI",
        "technologies": ["React", "FastAPI", "Python", "MongoDB", "Redis"]
    }
    assert classify_project_type(data_fullstack) in ["fullstack", "ai_llm"]


def test_project_engine_test_a_frontend():
    engine = ProjectIntelligenceEngine()
    req = ProjectAnalyzeRequest(
        title="Simple Student Portfolio Website",
        description="Personal student portfolio website built using vanilla web tech.",
        technologies=["HTML", "CSS", "JavaScript"]
    )
    result = engine.analyze(req)

    assert result.project_type == "frontend"
    assert result.score <= 75
    assert result.score_badge in ["Good Evidence", "Foundational"]
    assert "code_audit" in (result.model_dump() if hasattr(result, "model_dump") else result.dict())
    assert result.code_audit["status"] == "not_available"

    # Check evidence contains no fake backend claims
    combined_text = " ".join(result.evidence_bullets + result.strengths + result.weaknesses + result.recommendations).lower()
    assert "sub-200ms" not in combined_text
    assert "load testing" not in combined_text
    assert "docker" not in combined_text
    assert "microservices" not in combined_text


def test_project_engine_test_b_machine_learning():
    engine = ProjectIntelligenceEngine()
    req = ProjectAnalyzeRequest(
        title="Machine Learning House Price Prediction",
        description="Regression model pipeline predicting housing prices based on dataset features.",
        technologies=["Python", "Pandas", "NumPy", "Scikit-learn", "Matplotlib"]
    )
    result = engine.analyze(req)

    assert result.project_type == "machine_learning"

    combined_rec = " ".join(result.recommendations).lower()
    assert any(term in combined_rec for term in ["cross-validation", "k-fold"])
    assert any(term in combined_rec for term in ["compare", "algorithm", "model"])
    assert any(term in combined_rec for term in ["hyperparameter", "gridsearch", "optuna"])
    assert any(term in combined_rec for term in ["feature importance", "metric", "evaluation"])

    # Ensure no fake claims
    all_text = " ".join(result.evidence_bullets + result.strengths).lower()
    assert "sub-200ms" not in all_text
    assert "api response throughput" not in all_text
    assert "docker containerization" not in all_text


def test_project_engine_test_c_fullstack_ai():
    engine = ProjectIntelligenceEngine()
    req = ProjectAnalyzeRequest(
        title="PlaceMentor AI — SDE Placement Copilot",
        description="Full-stack AI placement mentoring platform featuring AST code audit.",
        category="Full Stack / AI",
        technologies=["React", "FastAPI", "Python", "MongoDB", "Redis"],
        features=["ATS Resume Scanner", "AST Code Auditor"],
        achievements=["Handled 1,000+ API queries with sub-200ms response time"],
        architectureTags=["Microservices", "REST API", "JWT Auth"],
        github_url="https://github.com/Purv0040/PlaceMentor-AI"
    )
    result = engine.analyze(req)

    assert result.project_type in ["fullstack", "ai_llm"]
    assert result.score >= 80

    # Achievements explicitly passed by user can be in evidence
    combined_bullets = " ".join(result.evidence_bullets)
    assert "1,000+ API queries" in combined_bullets or "sub-200ms" in combined_bullets or "React" in combined_bullets


def test_ast_code_audit_no_repo():
    audit = perform_ast_code_audit(None)
    assert audit["status"] == "not_available"
    assert audit["reason"] == "No accessible source repository was provided."
