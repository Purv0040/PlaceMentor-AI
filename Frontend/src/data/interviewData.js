// Centralized dynamic questions bank categorized by User Role / Domain
// Supports: Full Stack, AI/ML, Cloud/DevOps, Cybersecurity, Backend, Data Science

const STORAGE_KEY = "placementor_interview_history";

export const domainQuestionsPool = {
  // 1. Full Stack Engineer
  "Full Stack Engineer": [
    {
      question: "How do you optimize initial page load performance in a React / Single Page Application? Discuss Server-Side Rendering (SSR), code-splitting, lazy loading, and asset caching strategies.",
      category: "Frontend Architecture & Web Performance",
      skill: "React Performance & Web Vitals",
      hint: "Explain React.lazy / Suspense, bundle splitting, CDN edge caching, and minimizing First Contentful Paint (FCP).",
      expected_focus: "SSR vs CSR trade-offs, bundle analysis, hydration, and Core Web Vitals.",
      difficulty: "Hard"
    },
    {
      question: "Design an end-to-end authentication flow using JWT with HTTP-only cookies and refresh token rotation. How do you defend against XSS and CSRF simultaneously?",
      category: "Full Stack Security & Auth",
      skill: "Authentication & Security Architecture",
      hint: "Discuss SameSite cookie flags, token expiration boundaries, refresh token replay detection, and CSRF double submit tokens.",
      expected_focus: "XSS prevention (CSP, sanitization), CSRF token validation, and secure token lifecycle.",
      difficulty: "Hard"
    },
    {
      question: "Explain the React reconciliation algorithm and Fiber architecture. How does React determine when to re-render, and how do useMemo, useCallback, and React.memo prevent wasted cycles?",
      category: "Frontend Core",
      skill: "React Internals & State Management",
      hint: "Discuss Virtual DOM diffing (keys, component types) and referential equality of props and callbacks.",
      expected_focus: "Diffing heuristics, Fiber work phases, and memoization trade-offs.",
      difficulty: "Medium"
    },
    {
      question: "In Node.js / Express backend with PostgreSQL, how do you handle high-concurrency database queries? Explain connection pooling, query batching, and preventing N+1 problems.",
      category: "Backend & Database",
      skill: "Node.js & Database Optimization",
      hint: "Discuss pg-pool sizing, DataLoader/JOIN indexing, and database deadlocks prevention.",
      expected_focus: "Connection starvation prevention, ORM/query optimization, and index design.",
      difficulty: "Hard"
    },
    {
      question: "How do WebSockets and Server-Sent Events (SSE) compare for real-time applications like a collaborative dashboard or chat? Walk through connection scaling with Redis Pub/Sub.",
      category: "Real-Time Systems",
      skill: "WebSockets & Distributed Pub-Sub",
      hint: "Contrast bi-directional full-duplex WebSockets with unidirectional SSE, and explain horizontal scaling with sticky sessions or Redis adapter.",
      expected_focus: "Protocol handshakes, backpressure, heartbeat ping/pong, and multi-node broadcast.",
      difficulty: "Medium"
    }
  ],

  // 2. AI/ML Engineer
  "AI/ML Engineer": [
    {
      question: "How does the Transformer self-attention mechanism work mathematically? Explain Query, Key, Value matrix projections, scaled dot-product attention, and multi-head benefits.",
      category: "Deep Learning & NLP",
      skill: "Transformers & Attention Mechanisms",
      hint: "Explain softmax((Q * K^T) / sqrt(d_k)) * V, why division by sqrt(d_k) stabilizes gradients, and positional encodings.",
      expected_focus: "Mathematical formula, complexity O(N^2), multi-head subspace representations.",
      difficulty: "Hard"
    },
    {
      question: "When deploying a Large Language Model (LLM) to production, what techniques reduce inference latency and GPU memory footprint? Compare Quantization (INT8/FP4), KV Caching, and FlashAttention.",
      category: "MLOps & LLM Deployment",
      skill: "Model Optimization & Inference Acceleration",
      hint: "Discuss memory bandwidth bottlenecks in auto-regressive generation, KV cache size calculation, and pruning.",
      expected_focus: "Quantization trade-offs, KV cache retention, batching (vLLM / continuous batching).",
      difficulty: "Hard"
    },
    {
      question: "Explain the vanishing and exploding gradient problem in deep neural networks. How do Residual Connections (ResNets), Layer Normalization, and Adam optimizer mitigate it?",
      category: "Deep Learning Foundations",
      skill: "Optimization & Backpropagation",
      hint: "Discuss chain rule gradient flow in skip connections: d(x + F(x))/dx = 1 + F'(x).",
      expected_focus: "Gradient norms, skip connections gradient highways, adaptive learning rates.",
      difficulty: "Medium"
    },
    {
      question: "Design a Retrieval-Augmented Generation (RAG) pipeline for 500,000 internal enterprise PDF documents. How do you chunk documents, select embedding models, and handle hybrid vector-keyword retrieval?",
      category: "Applied AI & GenAI Systems",
      skill: "RAG Architecture & Vector Databases",
      hint: "Discuss semantic chunking with overlap, HNSW index in vector DBs, cross-encoder re-ranking, and hallucination guardrails.",
      expected_focus: "Chunking strategies, embedding distance metrics (cosine), BM25 + vector fusion, and re-ranking.",
      difficulty: "Hard"
    },
    {
      question: "How do you detect and mitigate Data Drift and Concept Drift in a production machine learning pipeline? Walk through monitoring metrics (KS-test, PSI) and re-training triggers.",
      category: "MLOps & Monitoring",
      skill: "Model Governance & Continuous Evaluation",
      hint: "Distinguish between change in input distribution P(X) vs relationship P(Y|X).",
      expected_focus: "Population Stability Index, statistical distribution divergence, automated rollback.",
      difficulty: "Medium"
    }
  ],

  // 3. AWS / DevOps & Cloud Engineer
  "AWS / DevOps & Cloud Engineer": [
    {
      question: "How do Kubernetes Pods, ReplicaSets, and Deployments handle Zero-Downtime Rolling Updates? How do Liveness and Readiness probes prevent routing traffic to unhealthy containers?",
      category: "Container Orchestration & Kubernetes",
      skill: "Kubernetes Lifecycle & Health Probes",
      hint: "Discuss maxSurge, maxUnavailable, preStop hooks, and endpoint controller propagation delays.",
      expected_focus: "Traffic draining, graceful termination SIGTERM, and probe interval calibration.",
      difficulty: "Hard"
    },
    {
      question: "In Terraform, how do you architect multi-environment (dev/stage/prod) infrastructure with remote state management and state locking? How do you prevent state drift?",
      category: "Infrastructure as Code (IaC)",
      skill: "Terraform State & CI/CD Automation",
      hint: "Explain S3 remote backend with DynamoDB locking, workspace vs directory isolation, and terraform plan CI checks.",
      expected_focus: "State file security, locking concurrency, module modularity, and drift detection.",
      difficulty: "Medium"
    },
    {
      question: "Design a highly available, multi-AZ architecture on AWS handling 100,000 active users. Detail VPC subnetting, ALB, Auto Scaling Groups, RDS Multi-AZ failover, and CloudFront caching.",
      category: "Cloud Architecture & Scalability",
      skill: "AWS High Availability Architecture",
      hint: "Discuss public vs private subnets, NAT Gateways, synchronous RDS standby replication, and RTO/RPO targets.",
      expected_focus: "Fault domain isolation, DNS failover (Route 53), and auto-scaling cooldown metrics.",
      difficulty: "Hard"
    },
    {
      question: "Walk through setting up a secure, immutable Docker container pipeline in GitHub Actions / GitLab CI. How do you integrate image vulnerability scanning (Trivy), SBOMs, and secret-free builds?",
      category: "CI/CD & DevSecOps",
      skill: "Container Security & Pipeline Hardening",
      hint: "Discuss multi-stage Docker builds, non-root USER directives, OIDC authentication instead of static AWS credentials.",
      expected_focus: "Least privilege CI/CD runners, minimal base images (distroless/alpine), and artifact signing (Cosign).",
      difficulty: "Medium"
    },
    {
      question: "How do you configure comprehensive Observability in a distributed microservices environment using Prometheus, Grafana, and OpenTelemetry? Contrast Metrics, Logs, and Distributed Tracing.",
      category: "Observability & SRE",
      skill: "Prometheus Monitoring & Tracing",
      hint: "Explain trace context propagation (trace-id / span-id) across HTTP headers and RED method (Rate, Errors, Duration).",
      expected_focus: "Telemetry overhead, metric retention, sampling rates, and actionable alerting thresholds.",
      difficulty: "Hard"
    }
  ],

  // 4. Cybersecurity Analyst & Engineer
  "Cybersecurity Analyst & Engineer": [
    {
      question: "Walk through the MITRE ATT&CK framework and Cyber Kill Chain. How would your SOC investigate an alert indicating lateral movement via PsExec or WMI with credential dumping?",
      category: "SOC Operations & Threat Hunting",
      skill: "Threat Detection & MITRE ATT&CK",
      hint: "Discuss Windows Event IDs (4624, 4672, 7045), LSASS memory access, and isolating infected endpoints via EDR.",
      expected_focus: "Triage process, SIEM log correlation, host containment, and forensic memory imaging.",
      difficulty: "Hard"
    },
    {
      question: "Explain the OWASP Top 10 web application vulnerabilities with focus on Broken Access Control (BOLA/IDOR) and Server-Side Request Forgery (SSRF). How do you audit and remediate them?",
      category: "Application Security & OWASP",
      skill: "Vulnerability Assessment & Code Auditing",
      hint: "Discuss verifying object-level ownership in middleware and restricting egress traffic to cloud metadata services (169.254.169.254).",
      expected_focus: "Root causes, exploitation mechanics, defense-in-depth, and automated SAST/DAST testing.",
      difficulty: "Hard"
    },
    {
      question: "Explain Zero Trust Architecture (NIST SP 800-207). How does it replace traditional perimeter-based security using continuous authentication, micro-segmentation, and least privilege?",
      category: "Enterprise Security Architecture",
      skill: "Zero Trust Principles & Identity",
      hint: "Explain 'never trust, always verify', contextual signals (device posture, geo-location, MFA), and software-defined perimeters.",
      expected_focus: "Policy Decision Points (PDP), Policy Enforcement Points (PEP), and identity-centric access control.",
      difficulty: "Medium"
    },
    {
      question: "During a suspected Ransomware incident on enterprise servers, walk step-by-step through Incident Response (NIST 800-61): Identification, Containment, Eradication, and Recovery.",
      category: "Incident Response & Forensics",
      skill: "Incident Response Playbooks",
      hint: "Highlight segmenting network interfaces before powering down machines, preserving volatile RAM, and verifying clean offline backup integrity.",
      expected_focus: "Containment speed, evidence chain of custody, root cause persistence removal, and post-incident review.",
      difficulty: "Hard"
    },
    {
      question: "How does Public Key Infrastructure (PKI) and TLS 1.3 handshake establish encrypted communication? Detail asymmetric key exchange (Diffie-Hellman), certificate validation, and Perfect Forward Secrecy.",
      category: "Cryptography & Network Security",
      skill: "TLS Protocol & Cryptography",
      hint: "Contrast RSA static key exchange with ephemeral Diffie-Hellman (ECDHE) for preventing retroactive decryption if private keys are compromised.",
      expected_focus: "Handshake round-trips, Certificate Authorities (CA/CRL/OCSP), and cipher suite selection.",
      difficulty: "Medium"
    }
  ],

  // 5. Backend Developer / SDE
  "Backend Developer": [
    {
      question: "How do you design a high-throughput distributed caching layer using Redis for microservices? How do you prevent Cache Penetration, Cache Breakdown, and Cache Stampede under peak load?",
      category: "System Design & Architecture",
      skill: "Distributed Caching (Redis)",
      hint: "Discuss Bloom filters for penetration, Mutex locks for breakdown, and randomized TTL jitter for stampedes.",
      expected_focus: "Cache-Aside pattern, Write-Through/Back, memory eviction policies (LRU/LFU), and cluster replication.",
      difficulty: "Hard"
    },
    {
      question: "Explain PostgreSQL transaction isolation levels (MVCC). What is the difference between Read Committed, Repeatable Read, and Serializable, and how does PostgreSQL prevent deadlocks?",
      category: "Database Concurrency",
      skill: "PostgreSQL Internals & MVCC",
      hint: "Discuss row versioning (xmin, xmax), Snapshot Isolation anomalies (write skew), and deadlock_timeout.",
      expected_focus: "Concurrency anomalies, locking hierarchy (row vs table locks), and lock escalation.",
      difficulty: "Hard"
    },
    {
      question: "Design an API Rate Limiter in a distributed environment handling 50,000 req/sec. Compare Token Bucket, Leaky Bucket, and Redis Sliding Window Log algorithms.",
      category: "System Design & Scalability",
      skill: "Distributed Rate Limiting",
      hint: "Explain concurrency race conditions with Redis MULTI/EXEC or Lua scripts, and client HTTP 429 status response headers.",
      expected_focus: "Redis Lua scripting, Token Bucket algorithm, memory footprint, and HTTP 429 Retry-After.",
      difficulty: "Hard"
    },
    {
      question: "How does the Python asyncio / Node.js event loop handle asynchronous non-blocking I/O operations under high load? What happens when a synchronous CPU-bound task runs on the main thread?",
      category: "Core Runtime Architecture",
      skill: "Event Loop & Concurrency",
      hint: "Explain epoll/kqueue system calls, libuv thread pools, and worker process offloading (ProcessPoolExecutor).",
      expected_focus: "Call stack, event queue, microtasks vs macrotasks, and preventing thread starvation.",
      difficulty: "Medium"
    },
    {
      question: "How do you implement database horizontal sharding versus read replicas? How do you manage consistent hashing, shard key selection, and cross-shard queries?",
      category: "Distributed Databases",
      skill: "Sharding & Data Partitioning",
      hint: "Discuss virtual nodes on hash rings, hot spots prevention, and two-phase commits for cross-shard updates.",
      expected_focus: "Consistent hashing ring, re-balancing overhead, and CAP theorem trade-offs.",
      difficulty: "Hard"
    }
  ]
};

// Aliases mapping user-selected roles from Onboarding to canonical question pools
export const resolveDomainKey = (role = "") => {
  const norm = String(role || "").toLowerCase().trim();
  if (norm.includes("full stack") || norm.includes("mern") || norm.includes("react") || norm.includes("frontend")) {
    return "Full Stack Engineer";
  }
  if (norm.includes("ai") || norm.includes("ml") || norm.includes("machine learning") || norm.includes("data scientist")) {
    return "AI/ML Engineer";
  }
  if (norm.includes("cloud") || norm.includes("devops") || norm.includes("aws") || norm.includes("infrastructure") || norm.includes("sre")) {
    return "AWS / DevOps & Cloud Engineer";
  }
  if (norm.includes("cyber") || norm.includes("security") || norm.includes("analyst") || norm.includes("pentest") || norm.includes("soc")) {
    return "Cybersecurity Analyst & Engineer";
  }
  return "Backend Developer";
};

// General fallback list containing high-yield questions
export const defaultQuestions = [
  ...domainQuestionsPool["Full Stack Engineer"],
  ...domainQuestionsPool["AI/ML Engineer"],
  ...domainQuestionsPool["AWS / DevOps & Cloud Engineer"],
  ...domainQuestionsPool["Cybersecurity Analyst & Engineer"],
  ...domainQuestionsPool["Backend Developer"],
];

/**
 * Dynamically picks questions grounded strictly in the user's registered target domain.
 * Ensures questions rotate dynamically and never repeat within the same interview session.
 */
export const getDynamicQuestion = (userRole = "Backend Developer", questionNumber = 1, usedQuestions = []) => {
  const domainKey = resolveDomainKey(userRole);
  const pool = domainQuestionsPool[domainKey] || domainQuestionsPool["Backend Developer"];

  // Filter out questions already asked in this session
  const usedTexts = new Set(
    usedQuestions.map((q) => (typeof q === "string" ? q : q?.question)).filter(Boolean)
  );
  const available = pool.filter((q) => !usedTexts.has(q.question));

  const candidates = available.length > 0 ? available : pool;
  
  // Pick a random question from candidate pool for continuous variance
  const randomIndex = Math.floor(Math.random() * candidates.length);
  const selected = candidates[randomIndex];

  return {
    ...selected,
    id: `q_${domainKey.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}_${questionNumber}`,
    question_number: questionNumber,
    target_role: domainKey,
  };
};

export const defaultInterviewHistory = [
  {
    id: "session-1",
    date: "Recent",
    role: "Full Stack Engineer",
    type: "Technical Drill",
    difficulty: "Hard",
    questionCount: 3,
    durationText: "22 mins",
    score: 82,
    status: "Completed",
    strengths: ["Strong caching trade-off explanation", "Clean STAR response format"],
    weaknesses: ["Requires deeper explanation of partition tolerance"]
  }
];

export const getStoredInterviewHistory = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) return JSON.parse(data);
  } catch (e) {
    console.error("Failed to load interview history from localStorage", e);
  }
  return defaultInterviewHistory;
};

export const saveInterviewHistory = (history) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    console.error("Failed to save interview history to localStorage", e);
  }
};
