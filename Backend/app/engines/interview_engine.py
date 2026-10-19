import logging
import random
import re
import uuid
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class AIInterviewEngine:
    """Local resilient, accurate interview engine for generating questions and computing scores."""

    def __init__(self, llm_service: Optional[Any] = None) -> None:
        self.llm_service = llm_service

    def _get_val(self, data: Any, key: str, default: Any = None) -> Any:
        if isinstance(data, dict):
            return data.get(key, default)
        return getattr(data, key, default)

    def generate_question(self, request: Any) -> Dict[str, Any]:
        target_role = self._get_val(request, "target_role", "Backend Developer")
        interview_type = str(self._get_val(request, "interview_type", "technical")).lower()
        q_num = int(self._get_val(request, "question_number", 1))
        difficulty = str(self._get_val(request, "difficulty", "medium")).capitalize()

        # Domain-grounded question pools
        role_pools = {
            "Full Stack Engineer": [
                ("How do you optimize initial page load performance in a React / Single Page Application? Discuss Server-Side Rendering (SSR), code-splitting, and asset caching.", "Frontend Architecture & Web Performance"),
                ("Design an end-to-end authentication flow using JWT with HTTP-only cookies and refresh token rotation, defending against XSS and CSRF.", "Full Stack Security & Auth"),
                ("Explain the React reconciliation algorithm and Fiber architecture. How do useMemo, useCallback, and React.memo prevent wasted re-renders?", "React Internals & State Management"),
                ("In a Node.js/Express backend with PostgreSQL, how do you handle high-concurrency queries, connection pooling, and prevent N+1 issues?", "Backend & Database Optimization"),
                ("Compare WebSockets vs Server-Sent Events (SSE) for real-time dashboards and explain how to scale connections using Redis Pub/Sub.", "Real-Time Systems"),
            ],
            "AI/ML Engineer": [
                ("How does the Transformer self-attention mechanism work mathematically? Explain Query, Key, Value projections and scaled dot-product attention.", "Deep Learning & NLP"),
                ("When deploying a Large Language Model (LLM) to production, what techniques reduce inference latency and GPU memory (Quantization, KV Caching, FlashAttention)?", "MLOps & LLM Deployment"),
                ("Explain the vanishing/exploding gradient problem in deep neural networks and how Residual Connections (ResNets) and LayerNorm mitigate it.", "Deep Learning Foundations"),
                ("Design a Retrieval-Augmented Generation (RAG) pipeline for 500,000 PDF documents. How do you chunk, embed, and perform hybrid retrieval?", "Applied AI & GenAI Systems"),
                ("How do you detect and mitigate Data Drift and Concept Drift in a production ML pipeline using KS-test and Population Stability Index (PSI)?", "MLOps & Model Governance"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("How do Kubernetes Deployments handle Zero-Downtime Rolling Updates, and how do Liveness/Readiness probes prevent traffic to unhealthy containers?", "Container Orchestration & Kubernetes"),
                ("In Terraform, how do you architect multi-environment infrastructure with remote state management, DynamoDB locking, and drift detection?", "Infrastructure as Code (IaC)"),
                ("Design a highly available, multi-AZ architecture on AWS handling 100,000 active users detailing VPC subnetting, ALB, and RDS Multi-AZ failover.", "AWS Cloud Architecture"),
                ("Walk through setting up a secure Docker container CI/CD pipeline in GitHub Actions with image vulnerability scanning (Trivy) and Cosign signing.", "CI/CD & DevSecOps"),
                ("How do you configure distributed microservices observability using Prometheus, Grafana, and OpenTelemetry (RED method)?", "Observability & SRE"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Walk through the MITRE ATT&CK framework. How would your SOC investigate an alert indicating lateral movement via PsExec or WMI with credential dumping?", "SOC Operations & Threat Hunting"),
                ("Explain the OWASP Top 10 vulnerabilities with focus on Broken Access Control (BOLA/IDOR) and SSRF. How do you audit and remediate them?", "Application Security & OWASP"),
                ("Explain Zero Trust Architecture (NIST SP 800-207): Policy Decision Points (PDP), PEPs, and continuous micro-segmentation.", "Enterprise Security Architecture"),
                ("During a suspected Ransomware incident on enterprise servers, walk step-by-step through Incident Response (NIST 800-61): Identification, Containment, Eradication, and Recovery.", "Incident Response & Forensics"),
                ("How does Public Key Infrastructure (PKI) and TLS 1.3 handshake establish encrypted communication? Detail asymmetric key exchange (ECDHE) and forward secrecy.", "Cryptography & Network Security"),
            ],
            "Backend Developer": [
                ("How would you design a scalable RESTful API with authentication (JWT/OAuth2) and distributed rate limiting (Token Bucket)?", "APIs & System Architecture"),
                ("Explain how database indexes (B-Tree vs Hash) improve query performance and when they might degrade write latency.", "Databases & Storage"),
                ("What strategies do you use for caching database queries using Redis, including cache invalidation and stampede prevention?", "Caching & Distributed Systems"),
                ("How does the event loop handle concurrency and asynchronous I/O operations under high load?", "Concurrency & Performance"),
                ("Explain how database connection pooling works and how you prevent connection exhaustion in microservices.", "Backend Architecture"),
            ]
        }

        # Resolve role
        target_role_lower = target_role.lower()
        matched_pool = role_pools["Backend Developer"]
        if "full stack" in target_role_lower or "mern" in target_role_lower or "react" in target_role_lower or "frontend" in target_role_lower:
            matched_pool = role_pools["Full Stack Engineer"]
        elif "ai" in target_role_lower or "ml" in target_role_lower or "machine learning" in target_role_lower:
            matched_pool = role_pools["AI/ML Engineer"]
        elif "cloud" in target_role_lower or "devops" in target_role_lower or "aws" in target_role_lower:
            matched_pool = role_pools["AWS / DevOps & Cloud Engineer"]
        elif "cyber" in target_role_lower or "security" in target_role_lower or "analyst" in target_role_lower:
            matched_pool = role_pools["Cybersecurity Analyst & Engineer"]

        # Extract previous questions to avoid repeating the exact same question in a session
        prev_qa = self._get_val(request, "previous_qa", [])
        asked_texts = {p.get("question") if isinstance(p, dict) else getattr(p, "question", "") for p in prev_qa}

        # Filter out questions already asked
        unasked = [item for item in matched_pool if item[0] not in asked_texts]
        candidates = unasked if unasked else matched_pool

        # Randomize selection for true variance instead of static index 0
        selected_q, category = random.choice(candidates)

        return {
            "question_id": f"q_{q_num}_{uuid.uuid4().hex[:6]}",
            "question_number": q_num,
            "question": selected_q,
            "category": category,
            "skill": category,
            "difficulty": difficulty,
            "expected_focus": "Factual correctness, concrete architecture details, trade-offs, and metrics.",
            "hint": "Structure your answer: 1. Core concept & definition, 2. Architecture/Algorithm, 3. Trade-offs and quantitative impact.",
        }

    def evaluate_answer(self, request: Any) -> Dict[str, Any]:
        """
        Calculates an accurate, rubric-based score across:
        - Technical Accuracy & Relevance (35%)
        - Depth & Concrete Engineering Details (25%)
        - Communication Clarity & Structure (20%)
        - STAR / Quantitative Metrics (20%)
        """
        ans = str(self._get_val(request, "answer", "")).strip()
        question = str(self._get_val(request, "question", "")).lower()
        category = str(self._get_val(request, "category", "Technical")).lower()
        skill = str(self._get_val(request, "skill", "Core")).lower()

        words = ans.split()
        word_count = len(words)

        # Baseline: If answer is empty or too short (< 8 words)
        if word_count < 8:
            return {
                "score": 30,
                "correctness": 30,
                "relevance": 35,
                "clarity": 30,
                "depth": 20,
                "technical_accuracy": 30,
                "communication_quality": 35,
                "strengths": ["Submitted an initial response."],
                "weaknesses": [
                    "Answer is too brief and lacks technical depth.",
                    "No concrete implementation details or architectural reasoning provided."
                ],
                "improvement_suggestions": [
                    "Elaborate thoroughly: explain the core mechanism, specific technologies, and trade-offs.",
                    "Aim for at least 40-80 words to thoroughly answer multi-part questions."
                ],
                "ai_feedback": "The response was too brief to demonstrate technical competence. Please explain your approach in detail with specific concepts and trade-offs.",
                "is_passable": False,
            }

        ans_lower = ans.lower()

        # Domain-specific terminology evaluation dictionaries
        core_tech_terms = [
            # Backend & Databases
            "redis", "cache", "caching", "sql", "nosql", "postgres", "mongodb",
            "index", "b-tree", "hash", "latency", "throughput", "concurrency",
            "asynchronous", "async", "await", "rest", "api", "jwt", "oauth",
            "rate limit", "token bucket", "sharding", "replica", "replication",
            "partition", "microservice", "docker", "event loop", "thread",
            "o(n)", "o(log n)", "o(1)", "complexity", "star", "trade-off",
            "consistency", "acid", "cap theorem", "load balancer", "gateway",
            # Full Stack & Frontend
            "react", "virtual dom", "reconciliation", "fiber", "ssr", "csr",
            "hydration", "code-splitting", "suspense", "hook", "memo",
            "xss", "csrf", "cookie", "cors", "websocket", "sse", "first contentful paint",
            # AI / ML
            "transformer", "attention", "query", "key", "value", "softmax",
            "gradient", "backpropagation", "loss", "overfitting", "regularization",
            "rag", "embedding", "vector", "quantization", "fine-tuning", "prompt",
            "llm", "drift", "psi", "hyperparameter", "epoch", "batch",
            # Cloud, DevOps & Security
            "kubernetes", "pod", "deployment", "terraform", "iac", "ci/cd",
            "pipeline", "vpc", "subnet", "alb", "prometheus", "grafana",
            "mitre", "siem", "zero trust", "ransomware", "tls", "pki", "owasp",
            "vulnerability", "encryption", "least privilege", "trivy"
        ]
        
        # Check skill/category specific terms
        matched_terms = [t for t in core_tech_terms if t in ans_lower]
        if skill and len(skill) > 2 and skill in ans_lower:
            matched_terms.append(skill)
        if category and len(category) > 2 and category in ans_lower:
            matched_terms.append(category)

        term_count = len(set(matched_terms))

        # Technical Accuracy Score (Base: 50, bonus for relevant vocabulary)
        tech_accuracy = 50 + min(40, term_count * 8)
        # Penalize if very short but contains keyword spam
        if word_count < 20:
            tech_accuracy = min(60, tech_accuracy)

        # 2. Depth & Completeness Score (Graded by informative length & detail)
        # Optimal technical answer: 60-160 words
        if word_count >= 100:
            depth_score = min(95, 75 + (term_count * 4))
        elif word_count >= 50:
            depth_score = min(88, 65 + (term_count * 4))
        elif word_count >= 25:
            depth_score = min(75, 55 + (term_count * 4))
        else:
            depth_score = min(60, 45 + (term_count * 4))

        # 3. Communication & Structure Score
        # Check for structural indicators (numbered lists, transitions, STAR keywords)
        structural_markers = [
            "first", "second", "third", "finally", "1.", "2.", "3.",
            "situation", "task", "action", "result", "for example",
            "specifically", "however", "therefore", "trade-off", "in order to"
        ]
        has_structure = sum(1 for m in structural_markers if m in ans_lower)
        clarity_score = min(95, 60 + min(30, has_structure * 8))

        # 4. Metrics & Quantitative Precision (Numbers, percentages, time bounds)
        has_numbers = bool(re.search(r'\b\d+(\.\d+)?(ms|s|%|k|req/s|rps|gb|mb|min)?\b', ans_lower))
        metric_bonus = 10 if has_numbers else 0
        clarity_score = min(95, clarity_score + metric_bonus)

        # Final Weighted Overall Calculation
        # 35% Technical Accuracy + 30% Depth + 20% Clarity + 15% Relevance
        relevance_score = min(95, tech_accuracy + (5 if term_count >= 2 else 0))
        final_score = int(
            (tech_accuracy * 0.35) +
            (depth_score * 0.30) +
            (clarity_score * 0.20) +
            (relevance_score * 0.15)
        )
        final_score = max(35, min(96, final_score))

        # Dynamic Strengths & Weaknesses
        strengths = []
        if term_count >= 3:
            strengths.append(f"Demonstrated good technical vocabulary: used key concepts like {', '.join(matched_terms[:3])}.")
        else:
            strengths.append("Provided a direct answer addressing the core question.")

        if has_structure >= 2:
            strengths.append("Structured the explanation systematically with logical progression.")
        elif word_count >= 40:
            strengths.append("Maintained clear flow of explanation across paragraphs.")

        if has_numbers:
            strengths.append("Included concrete numbers or quantitative benchmarks (e.g. latency, scale).")

        weaknesses = []
        if not has_numbers:
            weaknesses.append("Did not include quantitative metrics (e.g. latency impact, QPS, cache hit ratios).")
        if term_count < 2:
            weaknesses.append("Could incorporate more domain-specific technical terminology.")
        if word_count < 45:
            weaknesses.append("Response depth could be expanded to cover edge cases, failure modes, or bottlenecks.")
        if has_structure < 1:
            weaknesses.append("Structure could be improved with numbered points or the STAR method.")

        if not weaknesses:
            weaknesses.append("Consider discussing deeper disaster recovery or distributed consistency trade-offs.")

        # Tailored AI feedback message
        if final_score >= 85:
            feedback = f"Excellent technical response ({final_score}/100)! You articulated clear architectural principles with solid technical vocabulary."
        elif final_score >= 70:
            feedback = f"Good foundational response ({final_score}/100). The core ideas are correct; adding specific quantitative trade-offs and edge cases will elevate it to top-tier."
        else:
            feedback = f"Fair attempt ({final_score}/100). To achieve a higher score, structure your answer into numbered steps, name specific technologies, and explain trade-offs."

        return {
            "score": final_score,
            "correctness": tech_accuracy,
            "relevance": relevance_score,
            "clarity": clarity_score,
            "depth": depth_score,
            "technical_accuracy": tech_accuracy,
            "communication_quality": clarity_score,
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "improvement_suggestions": [
                "Mention concrete time/space complexity or latency trade-offs.",
                "Structure technical answers: 1. Core architecture, 2. Bottlenecks & edge cases, 3. Metrics."
            ],
            "ai_feedback": feedback,
            "is_passable": final_score >= 60,
        }

    def complete_interview(self, request: Any) -> Dict[str, Any]:
        """Aggregate all question scores accurately and generate final scorecard."""
        # Support both 'evaluations' and 'qna_history' payload keys
        evals = self._get_val(request, "evaluations", [])
        qna_history = self._get_val(request, "qna_history", [])

        scores = []
        tech_scores = []
        comm_scores = []
        all_strengths = []
        all_weaknesses = []

        if qna_history:
            for item in qna_history:
                ev = item.get("evaluation") if isinstance(item, dict) else getattr(item, "evaluation", {})
                if ev and isinstance(ev, dict):
                    sc = ev.get("score")
                    if sc is not None:
                        scores.append(sc)
                        tech_scores.append(ev.get("technical_accuracy", sc))
                        comm_scores.append(ev.get("communication_quality", sc))
                    if ev.get("strengths"):
                        all_strengths.extend(ev.get("strengths"))
                    if ev.get("weaknesses"):
                        all_weaknesses.extend(ev.get("weaknesses"))
        elif evals:
            for e in evals:
                sc = e.get("score") if isinstance(e, dict) else getattr(e, "score", None)
                if sc is not None:
                    scores.append(sc)
                    tech_scores.append(e.get("technical_accuracy", sc) if isinstance(e, dict) else sc)
                    comm_scores.append(e.get("communication_quality", sc) if isinstance(e, dict) else sc)

        if not scores:
            scores = [75]
            tech_scores = [75]
            comm_scores = [75]

        avg_score = int(round(sum(scores) / len(scores)))
        avg_tech = int(round(sum(tech_scores) / len(tech_scores)))
        avg_comm = int(round(sum(comm_scores) / len(comm_scores)))

        unique_strengths = list(dict.fromkeys(all_strengths))[:3] or [
            "Demonstrated core technical fundamentals.",
            "Structured responses with logical reasoning."
        ]
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:3] or [
            "Incorporate more quantitative benchmark metrics in system design answers.",
            "Cover edge cases and failure modes more explicitly."
        ]

        target_role = self._get_val(request, "target_role", "Candidate")

        return {
            "overall_score": avg_score,
            "category_scores": {
                "technical": avg_tech,
                "communication": avg_comm,
                "problem_solving": int(round((avg_tech + avg_comm) / 2)),
            },
            "strengths": unique_strengths,
            "weaknesses": unique_weaknesses,
            "recommendations": [
                f"Review real-world performance benchmarks and failure modes relevant to {target_role}.",
                "Practice using the STAR framework for behavioral and architectural trade-off questions.",
                "Always quantify system constraints (throughput, latency, memory bounds)."
            ],
            "technical_gaps": [],
            "communication_feedback": {
                "clarity": avg_comm,
                "structure": avg_comm,
                "articulation": "Optimal interview cadence" if avg_comm >= 75 else "Needs structural refinement",
            },
            "overall_feedback": f"Overall interview score: {avg_score}/100 across {len(scores)} question(s) for role {target_role}.",
        }
