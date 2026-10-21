import logging
import random
import uuid
from typing import Optional, Dict, Any, List
from app.role_requirements.roles import get_role_requirements, get_canonical_role_name
from app.schemas.interview import (
    AIInterviewQuestionRequest,
    AIInterviewQuestionResponse,
    AIInterviewAnswerEvaluateRequest,
    AIInterviewAnswerEvaluation,
    AIInterviewCompleteRequest,
    AIInterviewSummaryEvaluation,
)
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class AIInterviewEngine:
    def __init__(self, llm_service: Optional[LLMService] = None) -> None:
        self.llm_service = llm_service or LLMService()

    def generate_question(self, request: AIInterviewQuestionRequest) -> AIInterviewQuestionResponse:
        """Generate an interview question grounded in target role and student context."""
        canonical_role = get_canonical_role_name(request.target_role)
        role_reqs = get_role_requirements(canonical_role)
        role_skills = [r.skill for r in role_reqs]

        # Extract student background evidence
        ctx = request.student_context or {}
        projects = ctx.get("projects") or []
        resume_tech = ctx.get("resume", {}).get("skills", {}) if isinstance(ctx.get("resume"), dict) else {}
        github_repos = ctx.get("github", {}).get("top_repositories", []) if isinstance(ctx.get("github"), dict) else []
        skill_gaps = ctx.get("skill_gaps", {}).get("priority_gaps", []) if isinstance(ctx.get("skill_gaps"), dict) else []

        # Determine topic and question based on interview type, modality & previous answers
        q_num = request.question_number
        # Normalize interview modality/category strictly
        raw_itype = f"{getattr(request, 'modality', '') or ''} {getattr(request, 'category', '') or ''} {str(request.interview_type or '')}".lower().strip()
        if "star" in raw_itype or "behavioral" in raw_itype or "hr" in raw_itype:
            itype = "behavioral"
        elif "dsa" in raw_itype or "drill" in raw_itype or "algo" in raw_itype or "coding" in raw_itype or "tech" in raw_itype:
            itype = "dsa"
        elif "combined" in raw_itype or "tier" in raw_itype or "full" in raw_itype:
            stage_types = ["dsa", "system_design", "behavioral"]
            itype = stage_types[(q_num - 1) % 3]
        elif "design" in raw_itype or "architecture" in raw_itype or "system" in raw_itype:
            itype = "system_design"
        else:
            itype = "system_design"

        diff = request.difficulty.capitalize()

        # Check last Q&A performance for adaptive difficulty/topic selection
        last_eval = request.previous_qa[-1].get("evaluation", {}) if request.previous_qa else {}
        last_score = last_eval.get("score", 75) if isinstance(last_eval, dict) else 75
        
        adaptive_skill = None
        if last_score < 60 and request.previous_qa:
            # Clarifying / fundamental question on last topic
            adaptive_skill = request.previous_qa[-1].get("skill")
        elif last_score > 85 and skill_gaps:
            # Challenge on identified skill gap topic
            adaptive_skill = skill_gaps[0].get("skill") if isinstance(skill_gaps[0], dict) else None

        selected_skill = adaptive_skill or (role_skills[(q_num - 1) % len(role_skills)] if role_skills else "General")

        if itype == "project" and projects:
            p = projects[0]
            p_name = p.get("title") or p.get("name") or "Portfolio Project"
            p_tech = ", ".join(p.get("technologies", ["Python"]))
            question_text = f"In your project '{p_name}' using {p_tech}, describe the architectural trade-offs you faced when designing the data flow and how you handled high throughput or errors."
            category = "Project Architecture"
            expected_focus = "System design decisions, error handling, scale bottlenecks"
            hint = f"Focus on how {p_name} manages component separation and performance under load."

        # Role-grounded pools for the AI microservice
        role_pools_sys = {
            "AI/ML Engineer": [
                ("Design an enterprise-scale Retrieval-Augmented Generation (RAG) system serving 10M documents with sub-150ms latency. How do you design chunking, embedding generation pipelines, hybrid BM25 + dense vector search (HNSW), cross-encoder re-ranking, and cache frequently asked semantic queries?", "Applied AI & GenAI Systems", "RAG Architecture & Vector Retrieval"),
                ("Design a high-throughput, low-latency Real-Time Feature Store and Inference Engine for a fraud detection or recommendation system handling 50,000 req/sec. Walk through streaming ingestion (Kafka/Flink), low-latency key-value store (Redis/Feast), and model fallback strategies.", "MLOps & Real-time Systems", "Feature Store & Real-Time Serving"),
                ("Architect a distributed training cluster for a 70B parameter Large Language Model. How do you configure Data Parallelism (DDP), Tensor Parallelism (Megatron-LM), and Pipeline Parallelism? Discuss gradient checkpointing and ZeRO stage memory partitioning (DeepSpeed).", "Distributed Deep Learning", "Distributed Training & GPU Clustering"),
                ("Design an end-to-end MLOps deployment pipeline with automated continuous training (CT) and zero-downtime canary deployment. How do you detect Data Drift vs Concept Drift (using KS-Test, Population Stability Index), trigger model shadow testing, and handle automated rollback?", "MLOps & Model Governance", "Model Monitoring & CI/CD Deployment"),
                ("When deploying a Large Language Model (LLM) to production, what techniques reduce inference latency and GPU memory footprint? Compare Quantization (INT8/FP4), KV Caching, and FlashAttention.", "MLOps & LLM Deployment", "Model Optimization & Inference Acceleration"),
            ],
            "Frontend Developer": [
                ("Design a Micro-Frontends architecture for an enterprise web application with independent checkout, catalog, and account teams. Compare Module Federation (Webpack 5/Vite), iframe isolation, and single-spa router. How do you handle shared state and CSS style collisions?", "Micro-Frontends & Modular Architecture", "Micro-Frontends & Module Federation"),
                ("How do you systematically diagnose and optimize Core Web Vitals (Largest Contentful Paint - LCP, Interaction to Next Paint - INP, and Cumulative Layout Shift - CLS) on a high-traffic responsive web application?", "Web Performance & Core Web Vitals", "Core Web Vitals & Runtime Optimization"),
                ("Design an offline-first client architecture for a collaborative task management web app. How do you integrate Service Workers (Workbox), IndexedDB local persistence, background synchronization, and handle optimistic update rollbacks?", "Client Architecture & Offline Systems", "Service Workers & Local Persistence"),
                ("Architect an accessible, scalable multi-brand Design System in React and TypeScript. How do you structure design tokens (CSS custom properties), compound component composition, and keyboard accessibility (WCAG 2.1 AA)?", "Design Systems & Component Architecture", "Design Tokens & Accessible Component Libraries"),
                ("Design a Real-User Monitoring (RUM) and client-side error telemetry system (similar to Sentry). How do you capture unhandled promise rejections, React Error Boundaries, and send batch telemetry with navigator.sendBeacon without degrading UI framerates?", "Client Observability & Telemetry", "Client Monitoring & Error Boundaries"),
            ],
            "Full Stack Engineer": [
                ("How do you optimize initial page load performance in a React / Single Page Application? Discuss Server-Side Rendering (SSR), code-splitting, lazy loading, and asset caching strategies.", "Frontend Architecture & Web Performance", "React Performance & Web Vitals"),
                ("Design an end-to-end authentication flow using JWT with HTTP-only cookies and refresh token rotation. How do you defend against XSS and CSRF simultaneously?", "Full Stack Security & Auth", "Authentication & Security Architecture"),
                ("How do WebSockets and Server-Sent Events (SSE) compare for real-time applications like a collaborative dashboard or chat? Walk through connection scaling with Redis Pub/Sub.", "Real-Time Systems", "WebSockets & Distributed Pub-Sub"),
                ("In a Node.js / Express backend with PostgreSQL, how do you handle high-concurrency database queries? Explain connection pooling, query batching, and preventing N+1 problems.", "Backend & Database Optimization", "Node.js & Database Optimization"),
                ("Design an API Gateway architecture for microservices handling authentication, rate limiting, request validation, and aggregated responses for web and mobile clients.", "API & Gateway Architecture", "API Gateway & Microservices"),
            ],
            "Backend Developer": [
                ("How do you design a high-throughput distributed caching layer using Redis for microservices? How do you prevent Cache Penetration, Cache Breakdown, and Cache Stampede under peak load?", "System Design & Architecture", "Distributed Caching (Redis)"),
                ("Explain PostgreSQL transaction isolation levels (MVCC). What is the difference between Read Committed, Repeatable Read, and Serializable, and how does PostgreSQL prevent deadlocks?", "Database Concurrency", "PostgreSQL Internals & MVCC"),
                ("Design an API Rate Limiter in a distributed environment handling 50,000 req/sec. Compare Token Bucket, Leaky Bucket, and Redis Sliding Window Log algorithms.", "System Design & Scalability", "Distributed Rate Limiting"),
                ("How do you implement database horizontal sharding versus read replicas? How do you manage consistent hashing, shard key selection, and cross-shard queries?", "Distributed Databases", "Sharding & Data Partitioning"),
                ("Design an asynchronous event-driven architecture using Kafka or RabbitMQ for order processing. How do you guarantee exactly-once processing semantics and prevent message loss?", "Message Brokers & Streaming", "Event-Driven Architecture & Kafka"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("Design a highly available, multi-AZ architecture on AWS handling 100,000 active users. Detail VPC subnetting, ALB, Auto Scaling Groups, RDS Multi-AZ failover, and CloudFront caching.", "Cloud Architecture & Scalability", "AWS High Availability Architecture"),
                ("How do Kubernetes Deployments handle Zero-Downtime Rolling Updates? How do Liveness and Readiness probes prevent routing traffic to unhealthy containers?", "Container Orchestration & Kubernetes", "Kubernetes Lifecycle & Health Probes"),
                ("In Terraform, how do you architect multi-environment (dev/stage/prod) infrastructure with remote state management and DynamoDB locking? How do you prevent state drift?", "Infrastructure as Code (IaC)", "Terraform State & CI/CD Automation"),
                ("Walk through setting up a secure, immutable Docker container pipeline in GitHub Actions with image vulnerability scanning (Trivy), SBOMs, and Cosign artifact signing.", "CI/CD & DevSecOps", "Container Security & Pipeline Hardening"),
                ("How do you configure comprehensive Observability in a distributed microservices environment using Prometheus, Grafana, and OpenTelemetry (RED method)?", "Observability & SRE", "Prometheus Monitoring & Tracing"),
            ],
            "Data Scientist & AI Engineer": [
                ("Design an enterprise Data Lakehouse architecture (using Apache Iceberg/Delta Lake, Parquet, and Trino/Spark) supporting batch feature transformation and ad-hoc SQL querying over 50TB of tabular user data.", "Lakehouse Architecture & Big Data", "Data Lakehouse & Spark/Iceberg Architecture"),
                ("Design a real-time streaming analytics pipeline using Apache Kafka, Apache Flink / Spark Streaming, and ClickHouse for financial fraud detection in under 1 second. How do you handle out-of-order events with watermarks?", "Streaming Analytics & Real-Time Data", "Kafka/Flink Streaming & Windowing"),
                ("Architect an enterprise A/B testing and experimentation platform evaluating ML model variants across millions of users. How do you design user randomization (MurmurHash), Sample Ratio Mismatch (SRM) checks, and CUPED variance reduction?", "Experimentation & Statistical Platforms", "A/B Testing Infrastructure & CUPED"),
                ("Design a distributed model training and automated hyperparameter optimization pipeline using Ray Tune or Optuna with MLflow tracking. How do you implement Bayesian Optimization (TPE) and early stopping (ASHA)?", "ML Platforms & Distributed Training", "Hyperparameter Search & Ray/Optuna"),
                ("Design an automated model monitoring and drift detection system tracking classification models in production using Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests.", "Model Monitoring & Drift Detection", "Model Drift Observability & Retraining"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Explain Zero Trust Architecture (NIST SP 800-207). How does it replace traditional perimeter-based security using continuous authentication, micro-segmentation, and least privilege?", "Enterprise Security Architecture", "Zero Trust Principles & Identity"),
                ("Walk through the MITRE ATT&CK framework and Cyber Kill Chain. How would your SOC investigate an alert indicating lateral movement via PsExec or WMI with credential dumping?", "SOC Operations & Threat Hunting", "Threat Detection & MITRE ATT&CK"),
                ("Explain the OWASP Top 10 web application vulnerabilities with focus on Broken Access Control (BOLA/IDOR) and Server-Side Request Forgery (SSRF). How do you audit and remediate them?", "Application Security & OWASP", "Vulnerability Assessment & Code Auditing"),
                ("During a suspected Ransomware incident on enterprise servers, walk step-by-step through Incident Response (NIST 800-61): Identification, Containment, Eradication, and Recovery.", "Incident Response & Forensics", "Incident Response Playbooks"),
                ("How does Public Key Infrastructure (PKI) and TLS 1.3 handshake establish encrypted communication? Detail asymmetric key exchange (ECDHE) and forward secrecy.", "Cryptography & Network Security", "TLS Protocol & Cryptography"),
            ],
        }

        role_pools_dsa = {
            "AI/ML Engineer": [
                ("Explain the mathematical formulation and computational complexity of Transformer Self-Attention: Softmax((Q * K^T) / sqrt(d_k)) * V. Why is naive attention O(N^2) in sequence length, and how does FlashAttention reduce memory overhead?", "Deep Learning Foundations", "Transformers & Attention Mechanisms"),
                ("Given an unsorted collection of 1,000,000 high-dimensional feature vectors (d=768), how do you find the K nearest neighbors efficiently? Compare brute-force search with Approximate Nearest Neighbors (ANN) using HNSW graphs.", "Data Structures & Vector Search", "Approximate Nearest Neighbors & Graph Traversal"),
                ("In deep learning frameworks, how is the computational DAG built and traversed during forward/backward passes? Walk through the Topological Sort algorithm (Kahn's or DFS) used to schedule backward gradient execution.", "Algorithms & Computational Graphs", "Graph Algorithms & Autograd"),
                ("Explain how Byte-Pair Encoding (BPE) tokenization works algorithmically. How would you design an algorithm using Dynamic Programming to find the optimal subword segmentation or sequence edit distance?", "Algorithms & NLP", "Dynamic Programming & String Algorithms"),
                ("How does a 2D Convolution operation work algorithmically over an input image tensor? Walk through sliding window strides, padding calculations, and explain how Im2Col transforms convolution into GEMM matrix multiplication.", "Algorithms & Tensor Computation", "Tensor Operations & Convolution Algorithms"),
            ],
            "Frontend Developer": [
                ("Explain the React Fiber reconciler architecture and concurrent scheduling. Walk through the interruptible Render phase vs synchronous Commit phase, and how keys reduce list diffing complexity from O(N^3) to O(N).", "React Internals & Reconciler", "Fiber Architecture & Virtual DOM Diffing"),
                ("Implement a robust deep clone function in JavaScript that handles nested objects, arrays, Date, RegExp, Map, Set, and circular references without stack overflow.", "JavaScript Algorithms & Data Structures", "Deep Clone & Circular Reference Resolution"),
                ("Design and implement an asynchronous Task Queue / Promise Pool that executes a maximum of K concurrent async operations and returns results in the original request order.", "Async Concurrency & Queues", "Promise Concurrency Pool & Task Scheduling"),
                ("Implement custom debounce and throttle utility functions supporting leading and trailing execution flags, as well as an explicit cancel() method.", "Event Loop & Timing Algorithms", "Debounce, Throttle & Event Loop"),
                ("Given two DOM node references inside a document, write an algorithm to find their Lowest Common Ancestor (LCA) without using node.closest().", "Tree Algorithms & DOM Traversal", "DOM Tree Traversal & Lowest Common Ancestor"),
            ],
            "Full Stack Engineer": [
                ("Design and implement an LRU (Least Recently Used) Cache with O(1) time complexity for both get(key) and put(key, value) operations. Which underlying data structures do you combine and why?", "Data Structures & Memory Design", "LRU Cache & Linked Hash Map"),
                ("Explain the React reconciliation algorithm and Fiber architecture. How does React determine when to re-render, and how do useMemo, useCallback, and React.memo prevent wasted cycles?", "Frontend Core", "React Internals & State Management"),
                ("Given a DOM-like hierarchical tree structure, how would you write an algorithm to find the lowest common ancestor (LCA) of two target nodes? Provide both recursive and iterative approaches.", "Tree Algorithms & DOM", "Tree Traversal & Lowest Common Ancestor"),
                ("Solve the Sliding Window Maximum problem: given an array of integers and a window size k, return the maximum element in each sliding window in O(N) linear time using a Monotonic Deque.", "Algorithms & Double-ended Queues", "Sliding Window & Monotonic Deque"),
                ("Given a list of prerequisite software packages and dependencies, write an algorithm to determine if all packages can be installed without circular dependency deadlock.", "Graph Algorithms", "Topological Sort & Cycle Detection"),
            ],
            "Backend Developer": [
                ("Design a thread-safe, bounded blocking queue in code without race conditions or busy waiting. How do condition variables (wait/signal/notify) prevent deadlocks?", "Concurrency & Data Structures", "Thread-Safe Blocking Queue"),
                ("Given a massive log file of 100 million URL requests, find the Top K most frequently requested endpoints with limited RAM (e.g. 100MB). Walk through your algorithm and space complexity.", "Algorithms & Streaming Data", "Top K Elements & Min-Heap"),
                ("How does the event loop handle asynchronous non-blocking I/O operations under high load? What happens when a synchronous CPU-bound task runs on the main thread?", "Core Runtime Architecture", "Event Loop & Concurrency"),
                ("Implement a Trie (Prefix Tree) data structure supporting insert, search, and startsWith operations. How would you optimize it for memory when storing 10 million words?", "Tree Data Structures", "Trie & Memory Optimization"),
                ("Explain the internal structure of B-Trees and B+ Trees used in relational database indexes. Why are B+ Trees favored over Binary Search Trees or Hash Tables for disk storage?", "Database Internals & Trees", "B+ Tree Index Internals"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("Given a network CIDR block (e.g., 10.0.0.0/16) and a list of required subnet sizes, write an algorithm to allocate non-overlapping subnets using bitwise operations.", "Networking Algorithms & Bitwise", "CIDR Subnet Allocation & Bitwise Ops"),
                ("In Terraform / CloudFormation, how does the engine construct the Dependency DAG for infrastructure resources? Write out the Topological Sort algorithm with cycle detection.", "Graph Algorithms & IaC", "DAG Execution & Cycle Detection"),
                ("Design an algorithm to parse a high-volume live server log stream and alert when error status codes (HTTP 5xx) exceed 5% over any sliding 60-second window in real-time.", "Streaming Algorithms & Queues", "Sliding Window Log Aggregation"),
                ("Implement the Token Bucket rate limiting algorithm for cloud API gateways. How do you handle continuous fractional token refill without floating point drift?", "Algorithms & Rate Limiting", "Token Bucket Algorithm"),
                ("Explain how Linux process memory management and CFS (Completely Fair Scheduler) work. What data structure does CFS use to schedule tasks and why?", "OS Internals & Data Structures", "Linux CFS & Red-Black Trees"),
            ],
            "Data Scientist & AI Engineer": [
                ("Derive the mathematical formulation of Logistic Regression loss (Binary Cross-Entropy) and gradient descent weight updates. Why is Mean Squared Error (MSE) non-convex with sigmoid?", "Machine Learning Math & Optimization", "Logistic Regression Derivation & Regularization"),
                ("Explain the K-Means clustering algorithm (Lloyd's algorithm) and its computational complexity. Why is naive random initialization prone to local minima, and how does K-Means++ solve this?", "Clustering Algorithms & Math", "K-Means & K-Means++ Seeding Algorithm"),
                ("Given a continuous data stream of unknown and potentially infinite length N, write an algorithm using Reservoir Sampling to sample K items uniformly at random in O(1) space.", "Streaming Algorithms & Probability", "Reservoir Sampling Algorithm"),
                ("Explain how Decision Trees select optimal feature split thresholds for classification. Compare Gini Impurity with Shannon Entropy / Information Gain.", "Decision Trees & Information Theory", "Information Gain, Gini Impurity & Splitting"),
                ("In extreme class imbalance (e.g. 99.9% negative, 0.1% positive in fraud detection), why is ROC-AUC dangerously deceptive compared to PR-AUC? Walk through the mathematical calculation.", "Evaluation Metrics & Statistics", "ROC-AUC vs PR-AUC & Class Imbalance"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Design an algorithm to detect malicious IP brute-force attacks in high-speed network traffic over a rolling 5-minute window in limited memory using Count-Min Sketch.", "Security Algorithms & Data Structures", "Count-Min Sketch & Sliding Window"),
                ("Explain how string matching algorithms (such as Aho-Corasick or Boyer-Moore) are used by Intrusion Detection Systems (Snort/Suricata) to match thousands of malware signatures simultaneously.", "Pattern Matching Algorithms", "Aho-Corasick Multi-Pattern Search"),
                ("Explain the Fast Modular Exponentiation algorithm (repeated squaring) used in RSA cryptographic key generation and decryption. Walk through its time complexity.", "Cryptographic Algorithms", "Modular Exponentiation & Complexity"),
                ("Given a network connectivity matrix of enterprise servers, write an algorithm to find all potential Attack Paths an adversary could traverse from a DMZ server to the Core Database.", "Graph Algorithms & Threat Modeling", "Attack Graph Traversal (DFS/BFS)"),
                ("How does a Bloom Filter work mathematically in security systems to check if a malicious URL is present in a database of 1 billion known threat indicators?", "Probabilistic Data Structures", "Bloom Filter & False Positive Math"),
            ]
        }

        role_pools_behavioral = {
            "AI/ML Engineer": [
                ("Tell me about a time when a machine learning model or critical AI feature performed poorly, hallucinated, or produced biased outputs in production. Walk me through your Situation, Task, Action to diagnose the root cause, and the measurable Result or safeguards implemented.", "Production Incident & Ethics", "Model Reliability & Incident Response"),
                ("Describe a scenario where product managers or business stakeholders wanted to rush an AI/ML feature into production before you validated safety, data leakage, or evaluation benchmarks. How did you communicate technical risk and negotiate a phased launch?", "Stakeholder Negotiation & Ethics", "Cross-Functional Communication & Risk Management"),
                ("Describe a project where you had to balance short-term delivery pressure against long-term engineering health (such as investing in automated model evaluation pipelines or improving data labeling quality).", "Prioritization & Technical Debt", "Engineering Prioritization & Task Management"),
                ("Tell me about an unassigned problem or optimization (such as drastically reducing cloud GPU training costs or improving inference throughput) that you noticed and spearheaded proactively.", "Proactivity & Engineering Ownership", "Proactive Problem Solving & Impact"),
                ("Describe a scenario where you had to explain a complex algorithmic decision, trade-off, or failure mode to non-technical stakeholders or executive leadership.", "Communication & Leadership", "Technical Translation & Executive Presence"),
            ],
            "Frontend Developer": [
                ("Tell me about a high-severity frontend production incident you faced (e.g., infinite re-render loop crashing browser tabs, broken checkout button, or memory leak). Walk me through your STAR response.", "Production Incident Response", "Frontend Triage & Emergency Response"),
                ("Describe a situation where UI/UX designers proposed complex, heavy animations that would severely degrade mobile performance or accessibility. How did you negotiate technical trade-offs to reach a shared solution?", "Cross-Functional Collaboration", "Designer Collaboration & Technical Trade-offs"),
                ("Walk through a scenario where you led or advocated for a major frontend refactor or tooling upgrade (e.g., migrating Webpack to Vite, moving to TypeScript, or adopting React Query). How did you gain team alignment?", "Technical Leadership & Modernization", "Frontend Tooling Migration & ROI"),
                ("Describe a project where a critical feature worked seamlessly on Chrome on desktop but broke completely on Safari iOS or low-end mobile devices right before launch.", "Cross-Browser Compatibility & Debugging", "Cross-Browser Debugging & Polyfills"),
                ("Tell me about a time you noticed accessibility (a11y) barriers in your web application and took the initiative to audit and remediate them even though it was not explicitly on the sprint backlog.", "Accessibility & Engineering Ownership", "Accessibility Advocacy & WCAG Compliance"),
            ],
            "Full Stack Engineer": [
                ("Tell me about a high-priority production bug or outage in a web application you deployed. Walk through your Situation, Task, Action to restore service, and the Resulting preventative measures.", "Production Incident Response", "Incident Management & STAR"),
                ("Describe a situation where you had a strong disagreement with a backend or frontend peer regarding API schema design or state management. How did you resolve the deadlock?", "Team Collaboration & Conflict", "Engineering Conflict Resolution"),
                ("Walk through a project where product requirements shifted drastically midway through development. How did you realign your tasks and deliver a reliable release?", "Agility & Adaptability", "Requirement Management & Scope Control"),
                ("Tell me about a time you identified significant technical debt (e.g. monolithic legacy code, poor test coverage) and convinced management to allocate sprint cycles to refactor it.", "Technical Leadership & Proactivity", "Advocating for Code Quality"),
                ("Describe a scenario where you mentored a junior engineer or onboarded a new team member onto a complex codebase. What strategies ensured their rapid productivity?", "Mentorship & Culture", "Engineering Mentorship & Onboarding"),
            ],
            "Backend Developer": [
                ("Describe a scenario where a database migration or critical backend release caused downtime or data corruption. Walk through your STAR response from initial detection to full recovery.", "Data Integrity & Incident Response", "Production Incident & STAR"),
                ("Tell me about a time you had to push back against unreasonable product deadlines to protect backend reliability, security, or scalability. How did you frame the conversation?", "Stakeholder Management & Boundaries", "Negotiating Engineering Scope"),
                ("Describe a project where you solved a severe backend bottleneck that was degrading user latency or spiking server costs. What was your investigation methodology?", "Performance Optimization & Root Cause", "Profiling & Bottleneck Resolution"),
                ("Tell me about a disagreement with a team architect over database choice (e.g. SQL vs Document NoSQL vs Key-Value). How did you evaluate trade-offs and reach a decision?", "Architecture Debate & Consensus", "Technical Decision Making"),
                ("Describe a time when you had to take ownership of a legacy, undocumented backend service with high error rates. How did you stabilize and modernize it?", "Legacy Systems & Ownership", "Code Modernization & SRE"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("Tell me about a catastrophic cloud infrastructure failure or DNS outage you managed. Walk through your STAR response: initial incident command, mitigation, and post-mortem.", "Incident Command & SRE", "Major Incident Management & STAR"),
                ("Describe a situation where developers were bypassing infrastructure guardrails or security policies to deploy faster. How did you address the friction without stalling delivery?", "DevOps Culture & Collaboration", "DevSecOps Culture Transformation"),
                ("Tell me about a major cloud cost optimization initiative you led. How did you identify waste, negotiate resource rightsizing with development teams, and verify savings?", "FinOps & Cross-Functional Influence", "Cloud FinOps & Stakeholder Influence"),
                ("Describe a project where you migrated mission-critical stateful infrastructure (e.g. production databases or Kubernetes clusters) with zero downtime.", "High-Stakes Execution", "Zero-Downtime Migration Planning"),
                ("Tell me about a time when an on-call alert was firing frequently, causing alert fatigue. How did you audit and remediate the alerting strategy?", "SRE Health & Alert Hygiene", "Alert Fatigue Remediation"),
            ],
            "Data Scientist & AI Engineer": [
                ("Tell me about a time when a statistical or machine learning model achieved stellar cross-validation metrics in notebook experimentation but failed drastically when evaluated on live out-of-sample data. How did you diagnose data leakage?", "Model Failure & Forensic Validation", "Data Leakage Diagnosis & STAR"),
                ("Describe a situation where product or executive stakeholders were celebrating an apparent conversion win that was actually driven by an algorithmic glitch, bot activity, or metric cannibalization. How did you challenge the prevailing narrative with data evidence?", "Data Integrity & Stakeholder Influence", "Scientific Rigor & Executive Communication"),
                ("Describe a project where you had to decide between continuing to explore complex advanced modeling techniques versus shipping a simpler heuristic or linear baseline. How did you justify the trade-off?", "Engineering Pragmatism & ROI", "Model Complexity vs Business Velocity"),
                ("Tell me about a time you audited a predictive model or training dataset and uncovered systemic algorithmic bias or disparate impact against a specific demographic. What concrete steps did you take to mitigate the bias?", "Ethical AI & Fairness", "Algorithmic Bias Auditing & Fairness"),
                ("Describe a scenario where you had to explain statistical confidence intervals, p-values, or experiment sample size requirements to non-technical stakeholders who wanted to call an A/B test early.", "Statistical Communication & Leadership", "Translating Statistics & Risk"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Tell me about a time you investigated a critical security alert under high pressure where initial indicators were ambiguous. Walk through your STAR triage and decision process.", "Security Triage & STAR", "Threat Triage & Incident Investigation"),
                ("Describe a situation where software engineers resisted implementing a required security control (e.g. mandatory MFA, secrets rotation, strict egress firewalls). How did you gain their cooperation?", "Security Culture & Persuasion", "Security Advocacy & Influence"),
                ("Tell me about an incident where you discovered a vulnerability or data exposure in a third-party vendor or executive system. How did you communicate the risk to leadership confidentially?", "Executive Communication & Confidentiality", "Executive Security Reporting"),
                ("Describe a time when a suspected false positive alert turned out to be an actual stealthy security compromise. How did you identify the subtle discrepancy?", "Threat Hunting & Diligence", "Threat Hunting & Anomaly Detection"),
                ("Tell me about how you stay updated on zero-day vulnerabilities (like Log4j or XZ Utils backdoor) and how you rapidly assess enterprise exposure within 24 hours.", "Vulnerability Management & Agility", "Rapid Zero-Day Triage"),
            ]
        }

        # Resolve role strictly
        canonical_role_lower = str(canonical_role or request.target_role or "").lower()
        if "frontend" in canonical_role_lower:
            matched_role = "Frontend Developer"
        elif "data scientist" in canonical_role_lower or "data science" in canonical_role_lower:
            matched_role = "Data Scientist & AI Engineer"
        elif "full stack" in canonical_role_lower or "mern" in canonical_role_lower or "fullstack" in canonical_role_lower:
            matched_role = "Full Stack Engineer"
        elif "ai" in canonical_role_lower or "ml" in canonical_role_lower or "machine learning" in canonical_role_lower:
            matched_role = "AI/ML Engineer"
        elif "cloud" in canonical_role_lower or "devops" in canonical_role_lower or "aws" in canonical_role_lower or "infrastructure" in canonical_role_lower:
            matched_role = "AWS / DevOps & Cloud Engineer"
        elif "cyber" in canonical_role_lower or "security" in canonical_role_lower or "analyst" in canonical_role_lower or "soc" in canonical_role_lower:
            matched_role = "Cybersecurity Analyst & Engineer"
        else:
            matched_role = "Backend Developer"

        # Track previously asked questions in this session to prevent duplicate questions
        prev_qa = request.previous_qa or []
        asked_texts = {p.get("question") if isinstance(p, dict) else getattr(p, "question", "") for p in prev_qa}
        asked_summary = "; ".join([q for q in asked_texts if q])

        modality_display_name = {
            "system_design": "System Architecture & Design",
            "dsa": "Technical / DSA Drill",
            "behavioral": "Behavioral & HR STAR Drill",
            "combined": "Full Tier-1 SDE Mock (Combined)",
            "project": "Project Architecture & Code Review",
        }.get(itype, "Technical & System Architecture")

        # ---------------------------------------------------------------------
        # 1. Attempt Dynamic AI Question Generation via Groq / LLM
        # ---------------------------------------------------------------------
        if self.llm_service:
            try:
                llm_prompt = (
                    f"You are a Principal Engineering Interviewer conducting a mock interview for the role of '{matched_role}'.\n"
                    f"Category / Modality: '{modality_display_name}'.\n"
                    f"Difficulty: '{diff}'. Question Number: {q_num} of {request.total_questions}.\n"
                    f"Questions already asked in this session (DO NOT repeat or overlap with these):\n{asked_summary or 'None'}\n\n"
                    "INSTRUCTIONS:\n"
                )
                if itype == "behavioral":
                    llm_prompt += (
                        "Generate a realistic, high-impact behavioral interview question tailored specifically to this role.\n"
                        "The candidate MUST use the STAR (Situation, Task, Action, Result) methodology.\n"
                        "Focus on production outages, difficult trade-offs, engineering disagreements, or architectural ownership."
                    )
                elif itype == "dsa":
                    llm_prompt += (
                        "Generate a rigorous Data Structures, Algorithms, or Technical Computational Complexity question tailored to this role.\n"
                        "Focus on algorithmic logic, computational complexity (Big-O time and space), edge cases, and code structure."
                    )
                else:  # system_design
                    llm_prompt += (
                        "Generate an enterprise-grade System Architecture & Scalability design question tailored to this role.\n"
                        "Focus on distributed systems, throughput & latency bottlenecks, caching, database sharding, or resilience."
                    )
                llm_prompt += (
                    "\n\nReturn ONLY a JSON object with EXACTLY the following keys:\n"
                    "{\n"
                    '  "question": "The interview question text",\n'
                    '  "category": "High-level domain category",\n'
                    '  "skill": "Specific core skill or technology tested",\n'
                    '  "expected_focus": "Key points candidate must address",\n'
                    '  "hint": "Copilot hint to assist candidate if requested"\n'
                    "}"
                )

                raw_llm_out = self.llm_service.generate_text(llm_prompt)
                parsed = self._extract_json(raw_llm_out)
                if parsed and parsed.get("question"):
                    q_focus = parsed.get("expected_focus")
                    if isinstance(q_focus, list):
                        q_focus_str = "; ".join(str(f) for f in q_focus)
                    else:
                        q_focus_str = str(q_focus or "Core technical principles and trade-offs.")

                    return AIInterviewQuestionResponse(
                        question_id=f"q_{request.target_role.lower().replace(' ', '_')}_{q_num}_{uuid.uuid4().hex[:6]}",
                        question_number=q_num,
                        question=str(parsed.get("question")).strip(),
                        category=str(parsed.get("category") or modality_display_name).strip(),
                        skill=str(parsed.get("skill") or selected_skill).strip(),
                        difficulty=diff,
                        expected_focus=q_focus_str,
                        hint=str(parsed.get("hint") or f"Focus on systematic reasoning and concrete {matched_role} practices.").strip(),
                    )
            except Exception as e:
                logger.warning("LLM dynamic question generation failed (%s), falling back to dynamic pool selection.", e)

        # ---------------------------------------------------------------------
        # 2. Dynamic Pool Fallback (Filtered & Randomized)
        # ---------------------------------------------------------------------
        if itype == "project" and projects:
            p = projects[0]
            p_name = p.get("title") or p.get("name") or "Portfolio Project"
            p_tech = ", ".join(p.get("technologies", ["Python"]))
            question_text = f"In your project '{p_name}' using {p_tech}, describe the architectural trade-offs you faced when designing the data flow and how you handled high throughput or errors."
            category = "Project Architecture"
            expected_focus = "System design decisions, error handling, scale bottlenecks"
            hint = f"Focus on how {p_name} manages component separation and performance under load."

        elif itype == "hr" or itype == "behavioral":
            pool = role_pools_behavioral.get(matched_role, role_pools_behavioral["Backend Developer"])
            unasked = [item for item in pool if item[0] not in asked_texts]
            q_tuple = random.choice(unasked) if unasked else random.choice(pool)
            question_text = q_tuple[0]
            category = q_tuple[1]
            selected_skill = q_tuple[2]
            expected_focus = "Use the STAR method: Situation, Task, Action, and Quantified Result."
            hint = "Structure your answer: 1. Situation & context, 2. Task & responsibilities, 3. Concrete action taken, 4. Quantifiable result."

        elif itype == "dsa":
            pool = role_pools_dsa.get(matched_role, role_pools_dsa["Backend Developer"])
            unasked = [item for item in pool if item[0] not in asked_texts]
            q_tuple = random.choice(unasked) if unasked else random.choice(pool)
            question_text = q_tuple[0]
            category = q_tuple[1]
            selected_skill = q_tuple[2]
            expected_focus = "Algorithmic logic, computational complexity (Big-O time and space), edge cases, and code structure."
            hint = "State the brute force complexity first, then explain the optimal hash, heap, or dynamic programming strategy."

        else:  # system_design
            pool = role_pools_sys.get(matched_role, role_pools_sys["Backend Developer"])
            unasked = [item for item in pool if item[0] not in asked_texts]
            q_tuple = random.choice(unasked) if unasked else random.choice(pool)
            question_text = q_tuple[0]
            category = q_tuple[1]
            selected_skill = q_tuple[2]
            expected_focus = "Distributed systems design, throughput & latency bottlenecks, caching trade-offs, and horizontal scalability."
            hint = "Diagram key components: Load Balancer -> API Gateway -> Service Instances -> Cache -> Database."

        return AIInterviewQuestionResponse(
            question_id=f"q_{request.target_role.lower().replace(' ', '_')}_{q_num}_{uuid.uuid4().hex[:6]}",
            question_number=q_num,
            question=question_text,
            category=category,
            skill=selected_skill,
            difficulty=diff,
            expected_focus=expected_focus,
            hint=hint,
        )

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        import json, re
        if not text:
            return None
        text = text.strip()
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            try:
                return json.loads(fence_match.group(1))
            except Exception:
                pass
        brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except Exception:
                pass
        try:
            return json.loads(text)
        except Exception:
            return None


    def _is_non_answer(self, ans: str) -> bool:
        if not ans:
            return True
        import re
        cleaned = re.sub(r"[^\w\s]", " ", ans.strip().lower())
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        compact = cleaned.replace(" ", "")

        non_answer_exact = {
            "na", "none", "nil", "null", "nothing", "idk", "dunno", "pass",
            "skip", "next", "no", "nope", "dont know", "dontknow", "donot know",
            "donotknow", "do not know", "no idea", "noidea", "no clue", "noclue",
            "not sure", "notsure", "not known", "notknown", "unknown", "cant answer",
            "cannot answer", "unable to answer", "no answer", "no response",
            "idont know", "i dont know", "i donot know", "i do not know",
            "i have no idea", "i have no clue", "not aware", "dont remember"
        }
        if cleaned in non_answer_exact or compact in non_answer_exact or ans.strip().lower() in non_answer_exact:
            return True

        if len(compact) <= 3:
            return True

        tokens = cleaned.split()
        if len(tokens) <= 12:
            raw_no_quote = ans.lower().replace("'", "").replace("’", "")
            phrases = [
                "dont know", "donot know", "do not know", "no idea", "no clue",
                "not sure", "not familiar", "havent learned", "havent studied",
                "cant answer", "cannot answer", "skip this", "pass this",
                "no knowledge", "zero knowledge", "forgot this", "dont remember"
            ]
            if any(p in raw_no_quote for p in phrases):
                return True

        if bool(re.match(r"^(.)\1{3,}$", compact)) or bool(re.match(r"^(asdf|qwer|zxcv|1234|abcd)+$", compact, re.IGNORECASE)):
            return True

        return False

    def evaluate_answer(self, request: AIInterviewAnswerEvaluateRequest) -> AIInterviewAnswerEvaluation:
        """Evaluate student submitted answer using rule-based metrics & structured analysis."""
        ans = request.answer.strip()
        word_count = len(ans.split()) if ans else 0

        # 1. Non-answer check: "NA", "i donot know", "idk", "pass", "skip", etc.
        if self._is_non_answer(ans):
            return AIInterviewAnswerEvaluation(
                score=0,
                correctness=0,
                relevance=0,
                clarity=0,
                depth=0,
                technical_accuracy=0,
                communication_quality=0,
                strengths=["Acknowledged knowledge gap honestly instead of fabricating incorrect information."],
                weaknesses=[
                    "Did not attempt the technical prompt or demonstrate foundational knowledge.",
                    "Lacks familiarity with the required technical concept."
                ],
                improvement_suggestions=[
                    "Review the fundamental concepts, architecture patterns, and trade-offs for this topic.",
                    "When answering technical questions, attempt to reason from first principles rather than passing completely."
                ],
                ai_feedback=f"No answer provided (0/100). The candidate answered '{ans[:40]}' and did not attempt the technical prompt.",
                follow_up_needed=True,
                suggested_next_topic=request.skill,
            )

        # 2. Trivial short response check (< 6 words with no technical substance)
        if word_count < 6:
            return AIInterviewAnswerEvaluation(
                score=5,
                correctness=5,
                relevance=5,
                clarity=5,
                depth=5,
                technical_accuracy=5,
                communication_quality=5,
                strengths=["Submitted a brief response."],
                weaknesses=["Answer is too brief and contains no technical substance, mechanisms, or explanations."],
                improvement_suggestions=["Expand answer by covering: 1. Core concept, 2. Implementation details, 3. Trade-offs/metrics."],
                ai_feedback="Insufficient response (5/100). The submission contains no relevant technical explanation.",
                follow_up_needed=True,
                suggested_next_topic=request.skill,
            )

        # Evaluate quality based on key technical vocabulary & structure
        has_metrics = any(char.isdigit() for char in ans)
        has_structure = any(marker in ans.lower() for marker in ["first", "second", "specifically", "because", "however", "for example", "trade-off"])
        has_tech_kw = any(kw in ans.lower() for kw in [request.skill.lower(), "performance", "api", "database", "complexity", "o(n)", "cache", "scale", "system"])

        score_acc = min(95, max(60, 65 + (15 if has_tech_kw else 0) + (10 if has_metrics else 0)))
        score_depth = min(95, max(55, 60 + min(25, word_count // 5)))
        score_clarity = min(95, max(60, 70 + (15 if has_structure else 0)))
        score_comm = min(95, max(65, 75 + (10 if word_count >= 40 else 0)))

        overall = int((score_acc * 0.35) + (score_depth * 0.25) + (score_clarity * 0.20) + (score_comm * 0.20))

        strengths = [
            f"Demonstrated good conceptual awareness of {request.skill}.",
            "Used appropriate technical terms and structured reasoning.",
        ]
        if has_metrics:
            strengths.append("Included quantitative references and metrics.")

        weaknesses = []
        if not has_metrics:
            weaknesses.append("Could include concrete quantitative benchmark metrics (e.g. latency, throughput, memory impact).")
        if word_count < 35:
            weaknesses.append("Response depth could be expanded to cover edge cases and failover strategies.")

        suggestions = [
            f"When answering {request.category} questions, explicitly state time/space complexity or latency trade-offs.",
            "Use the STAR approach for behavioral/project questions (Situation, Task, Action, Result).",
        ]

        return AIInterviewAnswerEvaluation(
            score=overall,
            correctness=score_acc,
            relevance=min(95, score_acc + 5),
            clarity=score_clarity,
            depth=score_depth,
            technical_accuracy=score_acc,
            communication_quality=score_comm,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=suggestions,
            ai_feedback=f"Solid technical explanation scored at {overall}/100. Good coverage of {request.skill} principles.",
            follow_up_needed=overall < 70,
            suggested_next_topic=request.skill if overall < 70 else None,
        )

    def evaluate_complete_session(self, request: AIInterviewCompleteRequest) -> AIInterviewSummaryEvaluation:
        """Calculate overall interview evaluation from Q&A history."""
        qna = request.qna_history or []
        if not qna:
            return AIInterviewSummaryEvaluation(
                overall_score=70,
                category_scores={"Technical": 70, "Communication": 70},
                strengths=["Completed session setup."],
                weaknesses=["No answers recorded."],
                recommendations=["Attempt all questions in the mock interview drill."],
                technical_gaps=[],
                communication_feedback={"clarity": 70},
                overall_feedback="Session ended with no submitted answers.",
            )

        scores = []
        cat_scores: Dict[str, List[int]] = {}
        all_strengths = []
        all_weaknesses = []
        tech_gaps = []

        for item in qna:
            ev = item.get("evaluation") or {}
            sc = ev.get("score", 75)
            scores.append(sc)

            cat = item.get("category", "Technical")
            cat_scores.setdefault(cat, []).append(sc)

            if isinstance(ev.get("strengths"), list):
                all_strengths.extend(ev.get("strengths", []))
            if isinstance(ev.get("weaknesses"), list):
                all_weaknesses.extend(ev.get("weaknesses", []))
            if sc < 65 and item.get("skill"):
                tech_gaps.append(item.get("skill"))

        avg_score = int(sum(scores) / len(scores)) if scores else 75
        avg_cat = {cat: int(sum(sc_list) / len(sc_list)) for cat, sc_list in cat_scores.items()}

        unique_strengths = list(dict.fromkeys(all_strengths))[:4] or ["Good baseline technical knowledge."]
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:4] or ["Can improve STAR structure compliance."]
        unique_gaps = list(dict.fromkeys(tech_gaps))

        recommendations = [
            f"Focus upcoming daily task practice on identified technical gaps: {', '.join(unique_gaps or ['Advanced System Design']).title()}.",
            "Practice structuring answers into clear 3-step points (Context -> Core Architecture -> Quantitative Outcome).",
            "Maintain optimal speaking cadence (140-150 WPM) during live verbal delivery.",
        ]

        return AIInterviewSummaryEvaluation(
            overall_score=avg_score,
            category_scores=avg_cat,
            strengths=unique_strengths,
            weaknesses=unique_weaknesses,
            recommendations=recommendations,
            technical_gaps=unique_gaps,
            communication_feedback={
                "clarity": int(avg_score * 0.95),
                "structure": int(avg_score * 0.92),
                "articulation": "Optimal interview cadence" if avg_score >= 75 else "Needs structural refinement",
            },
            overall_feedback=f"Performance rated at {avg_score}/100 across {len(qna)} question(s) for target role {request.target_role}.",
        )
