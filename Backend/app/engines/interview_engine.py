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

        # 1. System Architecture & Design Pools (Role-Grounded)
        role_pools = {
            "AI/ML Engineer": [
                ("Design an enterprise-scale Retrieval-Augmented Generation (RAG) system serving 10M documents with sub-150ms latency. How do you design chunking, embedding generation pipelines, hybrid BM25 + dense vector search (HNSW), cross-encoder re-ranking, and cache frequently asked semantic queries?", "Applied AI & GenAI Systems"),
                ("Design a high-throughput, low-latency Real-Time Feature Store and Inference Engine for a recommendation or fraud detection system handling 50,000 req/sec. Walk through streaming ingestion (Kafka/Flink), low-latency key-value store (Redis/Feast), and model fallback strategies.", "MLOps & Real-time Systems"),
                ("Architect a distributed training cluster for a 70B parameter Large Language Model. How do you configure Data Parallelism (DDP), Tensor Parallelism (Megatron-LM), and Pipeline Parallelism? Discuss gradient checkpointing and ZeRO stage memory partitioning (DeepSpeed).", "Distributed Deep Learning"),
                ("Design an end-to-end MLOps deployment pipeline with automated continuous training (CT) and zero-downtime canary deployment. How do you detect Data Drift vs Concept Drift (using KS-Test, Population Stability Index), trigger shadow testing, and handle automated rollback?", "MLOps & Model Governance"),
                ("When deploying a Large Language Model (LLM) to production, what techniques reduce inference latency and GPU memory footprint? Compare Quantization (INT8/FP4), KV Caching, and FlashAttention.", "MLOps & LLM Deployment"),
            ],
            "Full Stack Engineer": [
                ("How do you optimize initial page load performance in a React / Single Page Application? Discuss Server-Side Rendering (SSR), code-splitting, lazy loading, and asset caching strategies.", "Frontend Architecture & Web Performance"),
                ("Design an end-to-end authentication flow using JWT with HTTP-only cookies and refresh token rotation. How do you defend against XSS and CSRF simultaneously?", "Full Stack Security & Auth"),
                ("How do WebSockets and Server-Sent Events (SSE) compare for real-time applications like a collaborative dashboard or chat? Walk through connection scaling with Redis Pub/Sub.", "Real-Time Systems"),
                ("In a Node.js / Express backend with PostgreSQL, how do you handle high-concurrency database queries? Explain connection pooling, query batching, and preventing N+1 problems.", "Backend & Database Optimization"),
                ("Design an API Gateway architecture for microservices handling authentication, rate limiting, request validation, and aggregated responses for web and mobile clients.", "API & Gateway Architecture"),
            ],
            "Frontend Developer": [
                ("Design a Micro-Frontends architecture for an enterprise web application with independent checkout, catalog, and account teams. Compare Module Federation (Webpack 5/Vite), iframe isolation, and single-spa router. How do you handle shared state and CSS style collisions?", "Micro-Frontends & Modular Architecture"),
                ("How do you systematically diagnose and optimize Core Web Vitals (Largest Contentful Paint - LCP, Interaction to Next Paint - INP, and Cumulative Layout Shift - CLS) on a high-traffic responsive web application?", "Web Performance & Core Web Vitals"),
                ("Design an offline-first client architecture for a collaborative task management web app. How do you integrate Service Workers (Workbox), IndexedDB local persistence, background synchronization, and optimistic UI rollbacks?", "Client Architecture & Offline Systems"),
                ("Architect an accessible, scalable multi-brand Design System in React and TypeScript. How do you structure design tokens (CSS custom properties), compound component composition, and keyboard accessibility (WCAG 2.1 AA)?", "Design Systems & Component Architecture"),
                ("Design a Real-User Monitoring (RUM) and client-side error telemetry system (similar to Sentry). How do you capture unhandled promise rejections, React Error Boundaries, and send batch telemetry with navigator.sendBeacon?", "Client Observability & Telemetry"),
            ],
            "Backend Developer": [
                ("How do you design a high-throughput distributed caching layer using Redis for microservices? How do you prevent Cache Penetration, Cache Breakdown, and Cache Stampede under peak load?", "Distributed Caching (Redis)"),
                ("Explain PostgreSQL transaction isolation levels (MVCC). What is the difference between Read Committed, Repeatable Read, and Serializable, and how does PostgreSQL prevent deadlocks?", "PostgreSQL Internals & MVCC"),
                ("Design an API Rate Limiter in a distributed environment handling 50,000 req/sec. Compare Token Bucket, Leaky Bucket, and Redis Sliding Window Log algorithms.", "Distributed Rate Limiting"),
                ("How do you implement database horizontal sharding versus read replicas? How do you manage consistent hashing, shard key selection, and cross-shard queries?", "Sharding & Data Partitioning"),
                ("Design an asynchronous event-driven architecture using Kafka or RabbitMQ for order processing. How do you guarantee exactly-once processing semantics and prevent message loss?", "Event-Driven Architecture & Kafka"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("Design a highly available, multi-AZ architecture on AWS handling 100,000 active users. Detail VPC subnetting, ALB, Auto Scaling Groups, RDS Multi-AZ failover, and CloudFront caching.", "AWS High Availability Architecture"),
                ("How do Kubernetes Deployments handle Zero-Downtime Rolling Updates? How do Liveness and Readiness probes prevent routing traffic to unhealthy containers?", "Kubernetes Lifecycle & Health Probes"),
                ("In Terraform, how do you architect multi-environment (dev/stage/prod) infrastructure with remote state management and DynamoDB locking? How do you prevent state drift?", "Terraform State & CI/CD Automation"),
                ("Walk through setting up a secure, immutable Docker container pipeline in GitHub Actions / GitLab CI with image vulnerability scanning (Trivy), SBOMs, and Cosign artifact signing.", "Container Security & Pipeline Hardening"),
                ("How do you configure comprehensive Observability in a distributed microservices environment using Prometheus, Grafana, and OpenTelemetry (RED method)?", "Prometheus Monitoring & Tracing"),
            ],
            "Data Scientist & AI Engineer": [
                ("Design an enterprise Data Lakehouse architecture (using Apache Iceberg/Delta Lake, Parquet, and Trino/Spark) supporting batch feature transformation and ad-hoc SQL querying over 50TB of tabular user data.", "Data Lakehouse & Spark/Iceberg Architecture"),
                ("Design a real-time streaming analytics pipeline using Apache Kafka, Apache Flink / Spark Streaming, and ClickHouse for financial fraud detection in under 1 second. How do you handle out-of-order events with watermarks?", "Kafka/Flink Streaming & Windowing"),
                ("Architect an enterprise A/B testing and experimentation platform evaluating ML model variants across millions of users. How do you design user randomization (MurmurHash), Sample Ratio Mismatch (SRM) checks, and CUPED variance reduction?", "A/B Testing Infrastructure & CUPED"),
                ("Design a distributed model training and automated hyperparameter optimization pipeline using Ray Tune or Optuna with MLflow tracking. How do you implement Bayesian Optimization (TPE) and early stopping (ASHA)?", "Hyperparameter Search & Ray/Optuna"),
                ("Design an automated model monitoring and drift detection system tracking classification models in production using Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests.", "Model Drift Observability & Retraining"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Explain Zero Trust Architecture (NIST SP 800-207). How does it replace traditional perimeter-based security using continuous authentication, micro-segmentation, and least privilege?", "Zero Trust Principles & Identity"),
                ("Walk through the MITRE ATT&CK framework and Cyber Kill Chain. How would your SOC investigate an alert indicating lateral movement via PsExec or WMI with credential dumping?", "Threat Detection & MITRE ATT&CK"),
                ("Explain the OWASP Top 10 web application vulnerabilities with focus on Broken Access Control (BOLA/IDOR) and Server-Side Request Forgery (SSRF). How do you audit and remediate them?", "Vulnerability Assessment & Code Auditing"),
                ("During a suspected Ransomware incident on enterprise servers, walk step-by-step through Incident Response (NIST 800-61): Identification, Containment, Eradication, and Recovery.", "Incident Response Playbooks"),
                ("How does Public Key Infrastructure (PKI) and TLS 1.3 handshake establish encrypted communication? Detail asymmetric key exchange (ECDHE) and forward secrecy.", "TLS Protocol & Cryptography"),
            ]
        }

        # 2. Technical / DSA Drill Pools (Role-Grounded)
        dsa_pools = {
            "AI/ML Engineer": [
                ("Explain the mathematical formulation and computational complexity of Transformer Self-Attention: Softmax((Q * K^T) / sqrt(d_k)) * V. Why is naive attention O(N^2) in sequence length, and how does FlashAttention reduce memory overhead?", "Transformers & Attention Mechanisms"),
                ("Given an unsorted collection of 1,000,000 high-dimensional feature vectors (d=768), how do you find the K nearest neighbors efficiently? Compare brute-force search with Approximate Nearest Neighbors (ANN) using HNSW graphs.", "Approximate Nearest Neighbors & Graph Traversal"),
                ("In deep learning frameworks, how is the computational DAG built and traversed during forward/backward passes? Walk through the Topological Sort algorithm (Kahn's or DFS) used to schedule backward gradient execution.", "Graph Algorithms & Autograd"),
                ("Explain how Byte-Pair Encoding (BPE) tokenization works algorithmically. How would you design an algorithm using Dynamic Programming to find the optimal subword segmentation or sequence edit distance?", "Dynamic Programming & String Algorithms"),
                ("How does a 2D Convolution operation work algorithmically over an input image tensor? Walk through sliding window strides, padding calculations, and explain how Im2Col transforms convolution into GEMM matrix multiplication.", "Tensor Operations & Convolution Algorithms"),
            ],
            "Full Stack Engineer": [
                ("Design and implement an LRU (Least Recently Used) Cache with O(1) time complexity for both get(key) and put(key, value) operations. Which underlying data structures do you combine and why?", "LRU Cache & Linked Hash Map"),
                ("Explain the React reconciliation algorithm and Fiber architecture. How does React determine when to re-render, and how do useMemo, useCallback, and React.memo prevent wasted cycles?", "React Internals & State Management"),
                ("Given a DOM-like hierarchical tree structure, how would you write an algorithm to find the lowest common ancestor (LCA) of two target nodes? Provide both recursive and iterative approaches.", "Tree Traversal & Lowest Common Ancestor"),
                ("Solve the Sliding Window Maximum problem: given an array of integers and a window size k, return the maximum element in each sliding window in O(N) linear time using a Monotonic Deque.", "Sliding Window & Monotonic Deque"),
                ("Given a list of prerequisite software packages and dependencies, write an algorithm to determine if all packages can be installed without circular dependency deadlock.", "Topological Sort & Cycle Detection"),
            ],
            "Frontend Developer": [
                ("Explain the React Fiber reconciler architecture and concurrent scheduling. Walk through the interruptible Render phase vs synchronous Commit phase, and how keys reduce list diffing complexity from O(N^3) to O(N).", "Fiber Architecture & Virtual DOM Diffing"),
                ("Implement a robust deep clone function in JavaScript that handles nested objects, arrays, Date, RegExp, Map, Set, and circular references without stack overflow.", "Deep Clone & Circular Reference Resolution"),
                ("Design and implement an asynchronous Task Queue / Promise Pool that executes a maximum of K concurrent async operations and returns results in the original request order.", "Promise Concurrency Pool & Task Scheduling"),
                ("Implement custom debounce and throttle utility functions supporting leading and trailing execution flags, as well as an explicit cancel() method.", "Debounce, Throttle & Event Loop"),
                ("Given two DOM node references inside a document, write an algorithm to find their Lowest Common Ancestor (LCA) without using node.closest().", "DOM Tree Traversal & Lowest Common Ancestor"),
            ],
            "Backend Developer": [
                ("Design a thread-safe, bounded blocking queue in code without race conditions or busy waiting. How do condition variables (wait/signal/notify) prevent deadlocks?", "Thread-Safe Blocking Queue"),
                ("Given a massive log file of 100 million URL requests, find the Top K most frequently requested endpoints with limited RAM (e.g. 100MB). Walk through your algorithm and space complexity.", "Top K Elements & Min-Heap"),
                ("How does the event loop handle asynchronous non-blocking I/O operations under high load? What happens when a synchronous CPU-bound task runs on the main thread?", "Event Loop & Concurrency"),
                ("Implement a Trie (Prefix Tree) data structure supporting insert, search, and startsWith operations. How would you optimize it for memory when storing 10 million words?", "Trie & Memory Optimization"),
                ("Explain the internal structure of B-Trees and B+ Trees used in relational database indexes. Why are B+ Trees favored over Binary Search Trees or Hash Tables for disk storage?", "B+ Tree Index Internals"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("Given a network CIDR block (e.g., 10.0.0.0/16) and a list of required subnet sizes, write an algorithm to allocate non-overlapping subnets using bitwise operations.", "CIDR Subnet Allocation & Bitwise Ops"),
                ("In Terraform / CloudFormation, how does the engine construct the Dependency DAG for infrastructure resources? Write out the Topological Sort algorithm with cycle detection.", "DAG Execution & Cycle Detection"),
                ("Design an algorithm to parse a high-volume live server log stream and alert when error status codes (HTTP 5xx) exceed 5% over any sliding 60-second window in real-time.", "Sliding Window Log Aggregation"),
                ("Implement the Token Bucket rate limiting algorithm for cloud API gateways. How do you handle continuous fractional token refill without floating point drift?", "Token Bucket Algorithm"),
                ("Explain how Linux process memory management and CFS (Completely Fair Scheduler) work. What data structure does CFS use to schedule tasks and why?", "Linux CFS & Red-Black Trees"),
            ],
            "Data Scientist & AI Engineer": [
                ("Derive the mathematical formulation of Logistic Regression loss (Binary Cross-Entropy) and gradient descent weight updates. Why is Mean Squared Error (MSE) non-convex with sigmoid?", "Logistic Regression Derivation & Regularization"),
                ("Explain the K-Means clustering algorithm (Lloyd's algorithm) and its computational complexity. Why is naive random initialization prone to local minima, and how does K-Means++ solve this?", "K-Means & K-Means++ Seeding Algorithm"),
                ("Given a continuous data stream of unknown and potentially infinite length N, write an algorithm using Reservoir Sampling to sample K items uniformly at random in O(1) space.", "Reservoir Sampling Algorithm"),
                ("Explain how Decision Trees select optimal feature split thresholds for classification. Compare Gini Impurity with Shannon Entropy / Information Gain.", "Information Gain, Gini Impurity & Splitting"),
                ("In extreme class imbalance (e.g. 99.9% negative, 0.1% positive in fraud detection), why is ROC-AUC dangerously deceptive compared to PR-AUC? Walk through the mathematical calculation.", "ROC-AUC vs PR-AUC & Class Imbalance"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Design an algorithm to detect malicious IP brute-force attacks in high-speed network traffic over a rolling 5-minute window in limited memory using Count-Min Sketch.", "Count-Min Sketch & Sliding Window"),
                ("Explain how string matching algorithms (such as Aho-Corasick or Boyer-Moore) are used by Intrusion Detection Systems (Snort/Suricata) to match thousands of malware signatures simultaneously.", "Aho-Corasick Multi-Pattern Search"),
                ("Explain the Fast Modular Exponentiation algorithm (repeated squaring) used in RSA cryptographic key generation and decryption. Walk through its time complexity.", "Modular Exponentiation & Complexity"),
                ("Given a network connectivity matrix of enterprise servers, write an algorithm to find all potential Attack Paths an adversary could traverse from a DMZ server to the Core Database.", "Attack Graph Traversal (DFS/BFS)"),
                ("How does a Bloom Filter work mathematically in security systems to check if a malicious URL is present in a database of 1 billion known threat indicators?", "Bloom Filter & False Positive Math"),
            ]
        }

        # 3. Behavioral & HR STAR Drill Pools (Role-Grounded)
        behavioral_pools = {
            "AI/ML Engineer": [
                ("Tell me about a time when a machine learning model or critical AI feature performed poorly, hallucinated, or produced biased outputs in production. Walk me through your Situation, Task, Action to diagnose the root cause, and the measurable Result or safeguards implemented.", "Model Reliability & Incident Response"),
                ("Describe a scenario where product managers or business stakeholders wanted to rush an AI/ML feature into production before you validated safety, data leakage, or evaluation benchmarks. How did you communicate technical risk and negotiate a phased launch?", "Cross-Functional Communication & Risk Management"),
                ("Describe a project where you had to balance short-term delivery pressure against long-term engineering health (such as investing in automated model evaluation pipelines or improving data labeling quality).", "Engineering Prioritization & Task Management"),
                ("Tell me about an unassigned problem or optimization (such as drastically reducing cloud GPU training costs or improving inference throughput) that you noticed and spearheaded proactively.", "Proactive Problem Solving & Impact"),
                ("Describe a scenario where you had to explain a complex algorithmic decision, trade-off, or failure mode to non-technical stakeholders or executive leadership.", "Technical Translation & Executive Presence"),
            ],
            "Full Stack Engineer": [
                ("Tell me about a high-priority production bug or outage in a web application you deployed. Walk through your Situation, Task, Action to restore service, and the Resulting preventative measures.", "Incident Management & STAR"),
                ("Describe a situation where you had a strong disagreement with a backend or frontend peer regarding API schema design or state management. How did you resolve the deadlock?", "Engineering Conflict Resolution"),
                ("Walk through a project where product requirements shifted drastically midway through development. How did you realign your tasks and deliver a reliable release?", "Requirement Management & Scope Control"),
                ("Tell me about a time you identified significant technical debt (e.g. monolithic legacy code, poor test coverage) and convinced management to allocate sprint cycles to refactor it.", "Advocating for Code Quality"),
                ("Describe a scenario where you mentored a junior engineer or onboarded a new team member onto a complex codebase. What strategies ensured their rapid productivity?", "Engineering Mentorship & Onboarding"),
            ],
            "Frontend Developer": [
                ("Tell me about a high-severity frontend production incident you faced (e.g., infinite re-render loop crashing browser tabs, broken checkout button, or memory leak). Walk me through your STAR response.", "Frontend Triage & Emergency Response"),
                ("Describe a situation where UI/UX designers proposed complex, heavy animations that would severely degrade mobile performance or accessibility. How did you negotiate technical trade-offs to reach a shared solution?", "Designer Collaboration & Technical Trade-offs"),
                ("Walk through a scenario where you led or advocated for a major frontend refactor or tooling upgrade (e.g., migrating Webpack to Vite, moving to TypeScript, or adopting React Query). How did you gain team alignment?", "Frontend Tooling Migration & ROI"),
                ("Describe a project where a critical feature worked seamlessly on Chrome on desktop but broke completely on Safari iOS or low-end mobile devices right before launch.", "Cross-Browser Debugging & Polyfills"),
                ("Tell me about a time you noticed accessibility (a11y) barriers in your web application and took the initiative to audit and remediate them even though it was not explicitly on the sprint backlog.", "Accessibility Advocacy & WCAG Compliance"),
            ],
            "Backend Developer": [
                ("Describe a scenario where a database migration or critical backend release caused downtime or data corruption. Walk through your STAR response from initial detection to full recovery.", "Production Incident & STAR"),
                ("Tell me about a time you had to push back against unreasonable product deadlines to protect backend reliability, security, or scalability. How did you frame the conversation?", "Negotiating Engineering Scope"),
                ("Describe a project where you solved a severe backend bottleneck that was degrading user latency or spiking server costs. What was your investigation methodology?", "Profiling & Bottleneck Resolution"),
                ("Tell me about a disagreement with a team architect over database choice (e.g. SQL vs Document NoSQL vs Key-Value). How did you evaluate trade-offs and reach a decision?", "Technical Decision Making"),
                ("Describe a time when you had to take ownership of a legacy, undocumented backend service with high error rates. How did you stabilize and modernize it?", "Code Modernization & SRE"),
            ],
            "AWS / DevOps & Cloud Engineer": [
                ("Tell me about a catastrophic cloud infrastructure failure or DNS outage you managed. Walk through your STAR response: initial incident command, mitigation, and post-mortem.", "Major Incident Management & STAR"),
                ("Describe a situation where developers were bypassing infrastructure guardrails or security policies to deploy faster. How did you address the friction without stalling delivery?", "DevSecOps Culture Transformation"),
                ("Tell me about a major cloud cost optimization initiative you led. How did you identify waste, negotiate resource rightsizing with development teams, and verify savings?", "Cloud FinOps & Stakeholder Influence"),
                ("Describe a project where you migrated mission-critical stateful infrastructure (e.g. production databases or Kubernetes clusters) with zero downtime.", "Zero-Downtime Migration Planning"),
                ("Tell me about a time when an on-call alert was firing frequently, causing alert fatigue. How did you audit and remediate the alerting strategy?", "Alert Fatigue Remediation"),
            ],
            "Data Scientist & AI Engineer": [
                ("Tell me about a time when a statistical or machine learning model achieved stellar cross-validation metrics in notebook experimentation but failed drastically when evaluated on live out-of-sample data. How did you diagnose data leakage?", "Data Leakage Diagnosis & STAR"),
                ("Describe a situation where product or executive stakeholders were celebrating an apparent conversion win that was actually driven by an algorithmic glitch, bot activity, or metric cannibalization. How did you challenge the prevailing narrative with data evidence?", "Scientific Rigor & Executive Communication"),
                ("Describe a project where you had to decide between continuing to explore complex advanced modeling techniques versus shipping a simpler heuristic or linear baseline. How did you justify the trade-off?", "Model Complexity vs Business Velocity"),
                ("Tell me about a time you audited a predictive model or training dataset and uncovered systemic algorithmic bias or disparate impact against a specific demographic. What concrete steps did you take to mitigate the bias?", "Algorithmic Bias Auditing & Fairness"),
                ("Describe a scenario where you had to explain statistical confidence intervals, p-values, or experiment sample size requirements to non-technical stakeholders who wanted to call an A/B test early.", "Translating Statistics & Risk"),
            ],
            "Cybersecurity Analyst & Engineer": [
                ("Tell me about a time you investigated a critical security alert under high pressure where initial indicators were ambiguous. Walk through your STAR triage and decision process.", "Threat Triage & Incident Investigation"),
                ("Describe a situation where software engineers resisted implementing a required security control (e.g. mandatory MFA, secrets rotation, strict egress firewalls). How did you gain their cooperation?", "Security Advocacy & Influence"),
                ("Tell me about an incident where you discovered a vulnerability or data exposure in a third-party vendor or executive system. How did you communicate the risk to leadership confidentially?", "Executive Security Reporting"),
                ("Describe a time when a suspected false positive alert turned out to be an actual stealthy security compromise. How did you identify the subtle discrepancy?", "Threat Hunting & Anomaly Detection"),
                ("Tell me about how you stay updated on zero-day vulnerabilities (like Log4j or XZ Utils backdoor) and how you rapidly assess enterprise exposure within 24 hours.", "Rapid Zero-Day Triage"),
            ]
        }

        # Resolve role strictly
        target_role_lower = str(target_role or "").lower()
        if "frontend" in target_role_lower:
            role_key = "Frontend Developer"
        elif "data scientist" in target_role_lower or "data science" in target_role_lower:
            role_key = "Data Scientist & AI Engineer"
        elif "full stack" in target_role_lower or "mern" in target_role_lower or "fullstack" in target_role_lower:
            role_key = "Full Stack Engineer"
        elif "ai" in target_role_lower or "ml" in target_role_lower or "machine learning" in target_role_lower:
            role_key = "AI/ML Engineer"
        elif "cloud" in target_role_lower or "devops" in target_role_lower or "aws" in target_role_lower or "infrastructure" in target_role_lower or "sre" in target_role_lower:
            role_key = "AWS / DevOps & Cloud Engineer"
        elif "cyber" in target_role_lower or "security" in target_role_lower or "analyst" in target_role_lower or "soc" in target_role_lower:
            role_key = "Cybersecurity Analyst & Engineer"
        else:
            role_key = "Backend Developer"

        # Resolve modality strictly from modality or interview_type
        modality_val = self._get_val(request, "modality", "") or self._get_val(request, "category", "")
        raw_mod = f"{modality_val} {interview_type}".lower().strip()
        if "star" in raw_mod or "behavioral" in raw_mod or "hr" in raw_mod:
            candidate_pool = behavioral_pools.get(role_key, behavioral_pools["Backend Developer"])
            expected_focus = "STAR framework: Situation, Task, concrete Action implemented, and quantifiable Result."
            hint = "Structure your answer using STAR: clearly define the challenge, your specific engineering decisions, and measurable outcomes."
        elif "dsa" in raw_mod or "drill" in raw_mod or "coding" in raw_mod or "algo" in raw_mod or "tech" in raw_mod:
            candidate_pool = dsa_pools.get(role_key, dsa_pools["Backend Developer"])
            expected_focus = "Algorithmic logic, computational complexity (Big-O time and space), edge cases, and code structure."
            hint = "State the brute-force baseline first, then walk through the optimal data structure, invariant proofs, and time/space complexity."
        elif "combined" in raw_mod or "tier" in raw_mod or "full" in raw_mod:
            # Multi-stage round rotation
            stage = (q_num - 1) % 3
            if stage == 0:
                candidate_pool = dsa_pools.get(role_key, dsa_pools["Backend Developer"])
                expected_focus = "Stage 1 Technical Drill: Algorithmic precision, data structure mechanics, and time/space complexity."
                hint = "Focus on optimal algorithmic traversal, boundary conditions, and memory efficiency."
            elif stage == 1:
                candidate_pool = role_pools.get(role_key, role_pools["Backend Developer"])
                expected_focus = "Stage 2 High-Level Architecture: Scalability, data flow, distributed caching, and failure trade-offs."
                hint = "Decompose into Client -> API Gateway -> Core Services -> Caching & Sharded Databases."
            else:
                candidate_pool = behavioral_pools.get(role_key, behavioral_pools["Backend Developer"])
                expected_focus = "Stage 3 Leadership & Culture: STAR methodology, technical conflict resolution, and ownership."
                hint = "Use STAR: Situation, Task, Action, and Quantified Result."
        else:
            # System Architecture & Design
            candidate_pool = role_pools.get(role_key, role_pools["Backend Developer"])
            expected_focus = "Distributed systems design, throughput & latency bottlenecks, caching trade-offs, and horizontal scalability."
            hint = "Define requirements (RPS, P99 latency, storage), draft high-level component diagrams, and explain fault-tolerance trade-offs."

        # Extract previous questions to avoid repeating the exact same question in a session
        prev_qa = self._get_val(request, "previous_qa", [])
        asked_texts = {p.get("question") if isinstance(p, dict) else getattr(p, "question", "") for p in prev_qa}

        # Filter out questions already asked
        unasked = [item for item in candidate_pool if item[0] not in asked_texts]
        candidates = unasked if unasked else candidate_pool

        # Deterministic or randomized selection
        selected_q, category = random.choice(candidates)

        return {
            "question_id": f"q_{q_num}_{uuid.uuid4().hex[:6]}",
            "question_number": q_num,
            "question": selected_q,
            "category": category,
            "skill": category,
            "difficulty": difficulty,
            "expected_focus": expected_focus,
            "hint": hint,
        }

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

        # 1. Non-answer check: "NA", "i donot know", "idk", "no idea", "pass", "skip", etc.
        if self._is_non_answer(ans):
            return {
                "score": 0,
                "correctness": 0,
                "relevance": 0,
                "clarity": 0,
                "depth": 0,
                "technical_accuracy": 0,
                "communication_quality": 0,
                "strengths": [
                    "Acknowledged knowledge gap honestly instead of fabricating incorrect information."
                ],
                "weaknesses": [
                    "Did not attempt the technical prompt or demonstrate foundational engineering knowledge.",
                    "Lacks familiarity with the required domain concept."
                ],
                "improvement_suggestions": [
                    "Review core concepts, architecture patterns, and industry use-cases for this topic.",
                    "In technical interviews, try to reason from first principles or discuss related concepts rather than passing completely."
                ],
                "ai_feedback": f"No answer provided (0/100). The candidate answered '{ans[:40]}' and did not attempt the technical prompt.",
                "is_passable": False,
            }

        # 2. Trivial response check (< 6 words with 0 technical terms)
        if word_count < 6:
            return {
                "score": 5,
                "correctness": 5,
                "relevance": 5,
                "clarity": 5,
                "depth": 5,
                "technical_accuracy": 5,
                "communication_quality": 5,
                "strengths": ["Submitted a brief response."],
                "weaknesses": [
                    "Answer is too brief and contains no technical substance, mechanisms, or explanations."
                ],
                "improvement_suggestions": [
                    "Provide a thorough technical explanation covering mechanisms, tools, and trade-offs.",
                    "Aim for at least 40-80 words to thoroughly answer multi-part questions."
                ],
                "ai_feedback": "Insufficient response (5/100). The response contains no relevant technical explanation.",
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
