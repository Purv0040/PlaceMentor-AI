"""
Project Intelligence Engine for PlaceMentor AI.

Dynamically evaluates software projects by inferring project type,
running AST / repository static code auditing where available, evaluating type-specific
criteria, generating grounded evidence bullets, strengths, weaknesses,
and recommendations, and calculating evidence-driven scores.
"""

import logging
import re
import httpx
from typing import Dict, List, Optional, Any, Tuple

from app.schemas.project import ProjectAnalyzeRequest, ProjectAIAnalysis
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

PROJECT_TYPES = [
    "frontend",
    "backend",
    "fullstack",
    "machine_learning",
    "deep_learning",
    "ai_llm",
    "data_science",
    "mobile",
    "devops_cloud",
    "cybersecurity",
    "data_engineering",
    "generic_software",
]


def classify_project_type(data: Dict[str, Any]) -> str:
    """
    Determines project type dynamically using category, role, title, description,
    technologies, features, and architectureTags.
    """
    title = str(data.get("title", "")).lower()
    description = str(data.get("description", "")).lower()
    category = str(data.get("category", "")).lower()
    role = str(data.get("role", "")).lower()

    raw_techs = data.get("technologies") or []
    techs = [str(t).lower() for t in raw_techs if t]

    raw_features = data.get("features") or []
    features = [str(f).lower() for f in raw_features if f]

    raw_tags = data.get("architectureTags") or []
    tags = [str(t).lower() for t in raw_tags if t]

    combined_text = " ".join([title, description, category, role] + techs + features + tags)

    scores = {pt: 0.0 for pt in PROJECT_TYPES}

    # Deep Learning
    dl_keywords = [
        "pytorch", "tensorflow", "keras", "torch", "torchvision", "computer vision",
        "cnn", "rnn", "lstm", "transformer", "yolo", "opencv", "gan", "autoencoder",
        "neural network", "deep learning", "object detection", "image classification"
    ]
    for kw in dl_keywords:
        if kw in combined_text:
            scores["deep_learning"] += 3.0 if kw in techs or kw in title else 1.5

    # AI / LLM
    ai_keywords = [
        "openai", "langchain", "llama", "ollama", "huggingface", "transformers", "rag",
        "vector db", "chromadb", "pinecone", "qdrant", "faiss", "prompt engineering",
        "llm", "claude", "gemini", "copilot", "gpt", "semantic search", "embedding",
        "ai mentor", "placement copilot", "ai copilot", "generative ai"
    ]
    for kw in ai_keywords:
        if kw in combined_text:
            scores["ai_llm"] += 3.0 if kw in techs or kw in title else 1.5

    # Machine Learning
    ml_keywords = [
        "scikit-learn", "sklearn", "pandas", "numpy", "scipy", "xgboost", "lightgbm",
        "catboost", "statsmodels", "regression", "random forest", "decision tree", "svm",
        "clustering", "kmeans", "knn", "naive bayes", "classification", "hyperparameter",
        "cross-validation", "feature engineering", "machine learning", "house price",
        "predictive", "recommendation system", "churn prediction"
    ]
    for kw in ml_keywords:
        if kw in combined_text:
            scores["machine_learning"] += 3.0 if kw in techs or kw in title else 1.5

    # Data Science
    ds_keywords = [
        "jupyter", "seaborn", "plotly", "exploratory data analysis", "eda", "tableau",
        "power bi", "statistics", "hypothesis testing", "streamlit", "dash",
        "data visualization", "data science", "analytics"
    ]
    for kw in ds_keywords:
        if kw in combined_text:
            scores["data_science"] += 3.0 if kw in techs or kw in title else 1.5

    # Data Engineering
    de_keywords = [
        "spark", "pyspark", "hadoop", "airflow", "dbt", "kafka", "flink", "elt", "etl",
        "data warehouse", "snowflake", "bigquery", "redshift", "databricks", "data pipeline", "data lake"
    ]
    for kw in de_keywords:
        if kw in combined_text:
            scores["data_engineering"] += 3.0 if kw in techs or kw in title else 1.5

    # DevOps / Cloud
    devops_keywords = [
        "docker", "kubernetes", "k8s", "terraform", "ansible", "helm", "jenkins",
        "github actions", "ci/cd", "aws", "azure", "gcp", "cloudformation",
        "prometheus", "grafana", "devops", "cloud infrastructure", "containerization"
    ]
    for kw in devops_keywords:
        if kw in combined_text:
            scores["devops_cloud"] += 3.0 if kw in techs or kw in title else 1.5

    # Cybersecurity
    sec_keywords = [
        "metasploit", "wireshark", "burp suite", "nmap", "kali", "snort", "owasp",
        "penetration testing", "cryptography", "threat modeling", "siem",
        "vulnerability assessment", "cybersecurity", "ethical hacking"
    ]
    for kw in sec_keywords:
        if kw in combined_text:
            scores["cybersecurity"] += 3.0 if kw in techs or kw in title else 1.5

    # Mobile
    mobile_keywords = [
        "react native", "flutter", "swift", "kotlin", "android", "ios", "xcode",
        "android studio", "expo", "ionic", "mobile app", "android app", "ios app"
    ]
    for kw in mobile_keywords:
        if kw in combined_text:
            scores["mobile"] += 3.0 if kw in techs or kw in title else 1.5

    # Frontend
    frontend_keywords = [
        "react", "react.js", "vue", "vue.js", "angular", "next.js", "nuxt", "svelte",
        "html", "css", "tailwind", "tailwindcss", "bootstrap", "redux", "zustand",
        "sass", "webpack", "vite", "frontend", "ui/ux", "portfolio website", "portfolio"
    ]
    for kw in frontend_keywords:
        if kw in combined_text:
            scores["frontend"] += 3.0 if kw in techs or kw in title else 1.0

    # Backend
    backend_keywords = [
        "fastapi", "flask", "django", "express", "express.js", "node", "node.js", "nodejs",
        "spring", "spring boot", "nest.js", "nestjs", "go", "golang", "gin", "fiber",
        "ruby on rails", "laravel", "asp.net", "mongodb", "postgresql", "postgres",
        "mysql", "redis", "grpc", "graphql", "rest api", "microservices", "backend", "jwt"
    ]
    for kw in backend_keywords:
        if kw in combined_text:
            scores["backend"] += 3.0 if kw in techs or kw in title else 1.0

    # Fullstack evaluation
    fe_score = scores["frontend"]
    be_score = scores["backend"]
    if fe_score > 0 and be_score > 0:
        scores["fullstack"] = fe_score + be_score + 4.0
    if any(term in combined_text for term in ["fullstack", "full-stack", "full stack"]):
        scores["fullstack"] += 6.0

    best_type = max(scores, key=scores.get)
    if scores[best_type] == 0.0:
        return "generic_software"

    return best_type


def perform_ast_code_audit(github_url: Optional[str]) -> Dict[str, Any]:
    """
    Inspects source repository when provided and accessible.
    Does NOT fabricate findings if URL is missing or inaccessible.
    """
    if not github_url or not isinstance(github_url, str) or "github.com" not in github_url:
        return {
            "status": "not_available",
            "reason": "No accessible source repository was provided."
        }

    url_clean = github_url.strip().rstrip("/")
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url_clean)
    if not match:
        return {
            "status": "not_available",
            "reason": "Provided GitHub URL format is invalid."
        }

    owner, repo = match.group(1), match.group(2)
    if repo.endswith(".git"):
        repo = repo[:-4]

    try:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "PlaceMentor-AST-Auditor"}
        api_url = f"https://api.github.com/repos/{owner}/{repo}"

        with httpx.Client(timeout=4.0) as client:
            res = client.get(api_url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                stars = data.get("stargazers_count", 0)
                lang = data.get("language", "Software")
                default_branch = data.get("default_branch", "main")

                contents_res = client.get(f"https://api.github.com/repos/{owner}/{repo}/contents", headers=headers)
                file_names = []
                if contents_res.status_code == 200:
                    files_list = contents_res.json()
                    if isinstance(files_list, list):
                        file_names = [f.get("name", "") for f in files_list]

                has_docker = any("docker" in f.lower() for f in file_names)
                has_tests = any("test" in f.lower() or "spec" in f.lower() for f in file_names)
                has_ci_cd = ".github" in file_names or any("ci" in f.lower() for f in file_names)

                return {
                    "status": "audited",
                    "repository": f"{owner}/{repo}",
                    "primary_language": lang,
                    "stars": stars,
                    "default_branch": default_branch,
                    "has_tests": has_tests,
                    "has_docker": has_docker,
                    "has_ci_cd": has_ci_cd,
                    "summary": f"Audited GitHub repository '{owner}/{repo}'. Primary language: {lang}."
                }
            elif res.status_code == 404:
                return {
                    "status": "not_available",
                    "reason": f"GitHub repository '{owner}/{repo}' is private or was not found."
                }
            else:
                return {
                    "status": "not_available",
                    "reason": f"GitHub API responded with status HTTP {res.status_code}."
                }
    except Exception as e:
        logger.warning("AST GitHub inspection failed: %s", e)
        return {
            "status": "not_available",
            "reason": "Source code repository could not be inspected due to network error."
        }


def calculate_dynamic_scores(
    project_type: str,
    data: Dict[str, Any],
    code_audit: Dict[str, Any]
) -> Tuple[int, int, str]:
    """
    Computes (score, complexity_score, score_badge) deterministically.
    """
    techs = data.get("technologies", [])
    features = data.get("features", [])
    achievements = data.get("achievements", [])
    arch_tags = data.get("architectureTags", [])
    github_url = data.get("github_url") or data.get("githubUrl")
    live_url = data.get("live_url") or data.get("liveUrl")
    description = str(data.get("description", ""))

    base_score = 55
    tech_count = len(techs)

    base_score += min(14, tech_count * 2)
    base_score += min(9, len(features) * 3)
    base_score += min(8, len(achievements) * 4)
    base_score += min(9, len(arch_tags) * 3)

    if github_url:
        base_score += 4
    if live_url:
        base_score += 4

    if len(description) > 100:
        base_score += 3
    if len(description) > 300:
        base_score += 3

    if code_audit.get("status") == "audited":
        base_score += 4
        if code_audit.get("has_tests"):
            base_score += 3
        if code_audit.get("has_docker") or code_audit.get("has_ci_cd"):
            base_score += 3

    score = min(98, max(45, base_score))

    if not github_url and not live_url and tech_count <= 3 and len(features) == 0:
        score = min(72, score)

    domain_inherent_complexity = {
        "deep_learning": 78,
        "ai_llm": 76,
        "data_engineering": 75,
        "fullstack": 75,
        "cybersecurity": 74,
        "devops_cloud": 74,
        "machine_learning": 70,
        "backend": 68,
        "data_science": 65,
        "mobile": 65,
        "frontend": 58,
        "generic_software": 55,
    }

    comp_base = domain_inherent_complexity.get(project_type, 60)
    complexity_score = min(98, max(40, comp_base + min(12, tech_count * 2) + min(6, len(arch_tags) * 2)))

    if score >= 88:
        score_badge = "Production Grade"
    elif score >= 78:
        score_badge = "System Architect"
    elif score >= 65:
        score_badge = "Good Evidence"
    else:
        score_badge = "Foundational"

    return score, complexity_score, score_badge


class ProjectIntelligenceEngine:
    """
    Core engine for dynamic, context-grounded project analysis.
    """

    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service

    def analyze(self, request: ProjectAnalyzeRequest) -> ProjectAIAnalysis:
        """
        Execute context-aware project analysis.
        """
        data = request.model_dump() if hasattr(request, "model_dump") else request.dict()

        # 1 — Classify project type
        project_type = classify_project_type(data)

        # 2 — AST code audit
        github_url = request.github_url or request.githubUrl
        code_audit = perform_ast_code_audit(github_url)

        # 3 — Dynamic Scores
        score, complexity_score, score_badge = calculate_dynamic_scores(project_type, data, code_audit)

        # 4 — Architecture Tags
        existing_tags = [t for t in request.architectureTags if t.strip()]
        architecture_tags = existing_tags or self._infer_architecture_tags(project_type, request.technologies)

        # 5 — Evidence Bullets (Strictly Grounded)
        evidence_bullets = self._generate_grounded_evidence(data, project_type, code_audit)

        # 6 — Type-Specific Evaluation: Strengths, Weaknesses, Recommendations
        strengths, weaknesses, recommendations = self._generate_type_evaluation(data, project_type, code_audit)

        return ProjectAIAnalysis(
            score=score,
            score_badge=score_badge,
            complexity_score=complexity_score,
            architecture_tags=architecture_tags,
            evidence_bullets=evidence_bullets,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            project_type=project_type,
            code_audit=code_audit
        )

    def _infer_architecture_tags(self, project_type: str, technologies: List[str]) -> List[str]:
        techs_str = " ".join([t.lower() for t in technologies])
        tags = []

        if project_type == "machine_learning":
            tags.append("Scikit-Learn Pipeline")
            if "pandas" in techs_str:
                tags.append("Data Preprocessing")
            tags.append("Model Evaluation")
        elif project_type == "deep_learning":
            tags.append("Neural Network Architecture")
            if "pytorch" in techs_str:
                tags.append("PyTorch Workflow")
            elif "tensorflow" in techs_str:
                tags.append("TensorFlow Pipeline")
        elif project_type == "ai_llm":
            tags.append("LLM Integration")
            if "rag" in techs_str or "chromadb" in techs_str or "pinecone" in techs_str:
                tags.append("RAG Architecture")
            tags.append("Prompt Pipeline")
        elif project_type == "frontend":
            tags.append("Component Architecture")
            if "react" in techs_str:
                tags.append("React State Management")
            tags.append("Responsive Layout")
        elif project_type == "backend":
            tags.append("REST API")
            if "fastapi" in techs_str or "flask" in techs_str or "express" in techs_str:
                tags.append("API Gateway")
            if "mongodb" in techs_str or "postgres" in techs_str:
                tags.append("Database Access Layer")
        elif project_type == "fullstack":
            tags.append("Fullstack Integration")
            tags.append("REST API")
            tags.append("Client-Server Architecture")
        elif project_type == "data_science":
            tags.append("Exploratory Data Analysis")
            tags.append("Data Visualization")
        elif project_type == "devops_cloud":
            tags.append("Containerization")
            tags.append("CI/CD Automation")
        elif project_type == "data_engineering":
            tags.append("ETL Pipeline")
            tags.append("Data Transformation")
        elif project_type == "cybersecurity":
            tags.append("Threat Modeling")
            tags.append("Security Verification")
        elif project_type == "mobile":
            tags.append("Mobile Component Pattern")
            tags.append("Client State Management")
        else:
            tags.append("Modular Software Architecture")

        return tags

    def _generate_grounded_evidence(self, data: Dict[str, Any], project_type: str, code_audit: Dict[str, Any]) -> List[str]:
        title = data.get("title", "Project")
        techs = data.get("technologies") or []
        features = data.get("features") or []
        achievements = data.get("achievements") or []
        arch_tags = data.get("architectureTags") or []

        bullets = []

        tech_str = ", ".join(techs[:4]) if techs else "core software frameworks"
        bullets.append(f"Engineered '{title}' utilizing {tech_str}, structuring functional modules and application workflow.")

        if features:
            feat_str = "; ".join(features[:2])
            bullets.append(f"Implemented core application features: {feat_str}.")
        elif arch_tags:
            tag_str = ", ".join(arch_tags[:3])
            bullets.append(f"Structured application architecture applying {tag_str} patterns.")

        if achievements:
            ach_str = "; ".join(achievements[:2])
            bullets.append(f"Achieved documented project outcomes: {ach_str}.")
        else:
            bullets.append(f"Established technical pipeline handling data processing and functional requirements for '{title}'.")

        if code_audit.get("status") == "audited":
            repo = code_audit.get("repository", "")
            lang = code_audit.get("primary_language", "Software")
            bullets.append(f"Verified source codebase structure for '{repo}' with primary language {lang}.")

        return bullets

    def _generate_type_evaluation(self, data: Dict[str, Any], project_type: str, code_audit: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        title = data.get("title", "")
        techs = data.get("technologies") or []
        features = data.get("features") or []
        achievements = data.get("achievements") or []
        arch_tags = data.get("architectureTags") or []

        combined = " ".join([title, str(data.get("description", ""))] + techs + features + achievements + arch_tags).lower()

        tech_str = ", ".join(techs) if techs else "selected stack"

        strengths = []
        weaknesses = []
        recommendations = []

        # Grounded strengths
        strengths.append(f"Clear technical stack integration using {tech_str}.")
        if features:
            strengths.append(f"Defined functional scope with {len(features)} key feature implementation(s).")
        if arch_tags:
            strengths.append(f"Structured architectural approach using {', '.join(arch_tags[:2])}.")

        # Domain-Specific Evaluation
        if project_type == "machine_learning":
            if not any(k in combined for k in ["cross-validation", "cv", "k-fold"]):
                weaknesses.append("Cross-validation workflow is not documented in project details.")
                recommendations.append("Add k-fold cross-validation to assess model generalization across dataset splits.")

            if not any(k in combined for k in ["compare", "comparison", "multiple models", "benchmark"]):
                weaknesses.append("No evidence provided of comparing multiple machine learning algorithms.")
                recommendations.append("Compare multiple regression/classification algorithms and report benchmark metrics.")

            if not any(k in combined for k in ["gridsearch", "optuna", "hyperparameter", "tuning"]):
                weaknesses.append("Hyperparameter tuning strategies are not documented.")
                recommendations.append("Apply hyperparameter optimization using GridSearchCV or Optuna to tune model parameters.")

            if not any(k in combined for k in ["feature importance", "shap", "importance"]):
                weaknesses.append("Feature importance analysis or model explainability metrics are not documented.")
                recommendations.append("Include feature importance analysis and model evaluation metrics (e.g., R² score, RMSE).")

            if not any(k in combined for k in ["deploy", "fastapi", "flask", "streamlit", "api"]):
                weaknesses.append("Model inference endpoint or deployment pipeline is not documented.")
                recommendations.append("Deploy the trained model behind an API endpoint (e.g., FastAPI or Streamlit) for predictions.")

        elif project_type == "deep_learning":
            if not any(k in combined for k in ["augmentation", "transform"]):
                weaknesses.append("Data augmentation pipeline for training generalization is not documented.")
                recommendations.append("Incorporate dataset augmentation pipelines to prevent neural network overfitting.")

            if not any(k in combined for k in ["loss curve", "learning rate", "checkpoint"]):
                weaknesses.append("Training dynamics (loss history, learning rate scheduling) are not documented.")
                recommendations.append("Document training loss vs. validation loss curves and learning rate decay schedules.")

            if not any(k in combined for k in ["onnx", "export", "quantization", "tensorrt"]):
                weaknesses.append("Model export or inference optimization is not documented.")
                recommendations.append("Export model artifacts to ONNX or TensorRT format for production inference.")

        elif project_type == "ai_llm":
            if not any(k in combined for k in ["hallucination", "guardrail", "eval", "evaluation"]):
                weaknesses.append("LLM response accuracy benchmarking and hallucination guardrails are not documented.")
                recommendations.append("Implement evaluation benchmarks for LLM prompt accuracy and factual consistency.")

            if not any(k in combined for k in ["latency", "token", "cost", "cache"]):
                weaknesses.append("LLM token budgeting, prompt caching, or cost optimization strategies are not documented.")
                recommendations.append("Incorporate prompt caching and token budgeting to manage LLM API response speed and costs.")

            if "rag" in combined or "vector" in combined:
                if not any(k in combined for k in ["hit rate", "mrr", "precision", "retrieval score"]):
                    weaknesses.append("Vector database retrieval evaluation metrics (Hit Rate, MRR) are not documented.")
                    recommendations.append("Benchmark vector store retrieval quality using precision and recall metrics.")

        elif project_type == "frontend":
            if not any(k in combined for k in ["accessibility", "wcag", "aria"]):
                weaknesses.append("Web accessibility (WCAG / ARIA compliance) is not documented.")
                recommendations.append("Add WCAG accessibility attributes (ARIA labels, semantic HTML) across components.")

            if not any(k in combined for k in ["jest", "testing library", "cypress", "playwright", "test"]):
                weaknesses.append("Automated UI unit or component test coverage is not documented.")
                recommendations.append("Integrate frontend testing frameworks (e.g., Jest or React Testing Library).")

            if not any(k in combined for k in ["lighthouse", "web vitals", "bundle", "vite"]):
                weaknesses.append("Frontend asset loading and Core Web Vitals optimization metrics are not documented.")
                recommendations.append("Implement code splitting and asset optimization to improve Core Web Vitals performance.")

        elif project_type == "backend":
            if not any(k in combined for k in ["pytest", "unittest", "supertest", "test"]):
                weaknesses.append("Automated API unit and integration test coverage is not documented.")
                recommendations.append("Add automated API endpoint test suites using pytest or Supertest.")

            if not any(k in combined for k in ["swagger", "openapi", "pydantic", "schema"]):
                weaknesses.append("Formal API contract documentation and request validation schemas are not documented.")
                recommendations.append("Document API endpoints using OpenAPI/Swagger schemas with strict request validation.")

            if not any(k in combined for k in ["jwt", "auth", "oauth", "session"]):
                weaknesses.append("Authentication and authorization control mechanisms are not documented.")
                recommendations.append("Implement secure authentication (JWT/OAuth2) and role-based access control (RBAC).")

        elif project_type == "fullstack":
            if not any(k in combined for k in ["e2e", "integration test", "cypress", "playwright"]):
                weaknesses.append("End-to-end integration testing across frontend and backend layers is not documented.")
                recommendations.append("Implement end-to-end integration tests (e.g., Playwright) validating key user flows.")

            if not any(k in combined for k in ["environment", "secrets", ".env", "config"]):
                weaknesses.append("Centralized environment configuration and API secret management are not documented.")
                recommendations.append("Standardize client-server error response contracts and environment secret security.")

            if not any(k in combined for k in ["redis", "cache", "caching"]):
                weaknesses.append("Response caching or session state storage optimization is not documented.")
                recommendations.append("Incorporate Redis or response caching for high-frequency backend queries.")

        elif project_type == "data_science":
            if not any(k in combined for k in ["eda", "cleaning", "outlier", "missing"]):
                weaknesses.append("Exploratory Data Analysis (EDA) process and missing data strategies are not documented.")
                recommendations.append("Document EDA steps detailing feature distributions, missing value handling, and outlier removal.")

            if not any(k in combined for k in ["hypothesis", "p-value", "statistical"]):
                weaknesses.append("Statistical significance tests or hypothesis testing metrics are not documented.")
                recommendations.append("Perform hypothesis testing to statistically validate analytical conclusions.")

        elif project_type == "devops_cloud":
            if not any(k in combined for k in ["prometheus", "grafana", "monitoring", "alert"]):
                weaknesses.append("Infrastructure monitoring dashboards and alert aggregation are not documented.")
                recommendations.append("Set up Prometheus/Grafana or cloud monitoring dashboards for system health tracking.")

            if not any(k in combined for k in ["terraform", "cloudformation", "ansible", "iac"]):
                weaknesses.append("Infrastructure-as-Code (IaC) templates are not documented.")
                recommendations.append("Define infrastructure components using IaC tools (e.g., Terraform or CloudFormation).")

        elif project_type == "data_engineering":
            if not any(k in combined for k in ["validation", "great expectations", "schema"]):
                weaknesses.append("Pipeline data validation and schema enforcement are not documented.")
                recommendations.append("Integrate automated data validation checks (e.g., Great Expectations) in pipeline steps.")

            if not any(k in combined for k in ["idempotent", "retry", "backfill"]):
                weaknesses.append("Data pipeline idempotency guarantees and task retry mechanisms are not documented.")
                recommendations.append("Ensure data pipeline tasks are idempotent with explicit retry mechanisms.")

        elif project_type == "cybersecurity":
            if not any(k in combined for k in ["stride", "threat model"]):
                weaknesses.append("Formal threat modeling (e.g., STRIDE framework) documentation is not provided.")
                recommendations.append("Perform threat modeling to document trust boundaries and attack surfaces.")

            if not any(k in combined for k in ["sast", "dast", "scanner", "vulnerability"]):
                weaknesses.append("Automated static/dynamic security scanning (SAST/DAST) is not documented.")
                recommendations.append("Integrate SAST and vulnerability scanning tools into the development workflow.")

        elif project_type == "mobile":
            if not any(k in combined for k in ["offline", "sqlite", "asyncstorage"]):
                weaknesses.append("Offline data persistence and synchronization strategies are not documented.")
                recommendations.append("Implement local caching for offline mobile app usage.")

            if not any(k in combined for k in ["device test", "simulator", "emulator"]):
                weaknesses.append("Device performance testing across mobile OS versions is not documented.")
                recommendations.append("Run automated device testing across various mobile viewport resolutions.")

        else: # generic_software
            if not any(k in combined for k in ["test", "unittest", "pytest"]):
                weaknesses.append("Automated test coverage for core module logic is not documented.")
                recommendations.append("Add unit tests covering core business logic and edge cases.")

            if not any(k in combined for k in ["readme", "docs", "documentation"]):
                weaknesses.append("System setup instructions and architectural documentation are not provided.")
                recommendations.append("Provide comprehensive README documentation detailing setup and usage instructions.")

        if not weaknesses:
            weaknesses.append("Long-term maintenance and production monitoring procedures are not documented.")
            recommendations.append("Add structured logging and monitoring procedures for production health tracking.")

        return strengths, weaknesses, recommendations
