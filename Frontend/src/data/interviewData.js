// Centralized dynamic questions bank categorized by User Role / Domain and Modality
// Supports: AI/ML, Full Stack, Backend, Cloud/DevOps, Cybersecurity
// Modalities: System Architecture & Design, Technical / DSA Drill, Behavioral & HR STAR Drill, Full Tier-1 SDE Mock

const STORAGE_KEY = "placementor_interview_history";

export const domainModalityQuestionsPool = {
  // ==========================================
  // 1. AI/ML Engineer
  // ==========================================
  "AI/ML Engineer": {
    "System Architecture & Design": [
      {
        question: "Design an enterprise-scale Retrieval-Augmented Generation (RAG) system serving 10M documents with sub-150ms latency. How do you design chunking, embedding generation pipelines, hybrid BM25 + dense vector search (HNSW), cross-encoder re-ranking, and cache frequently asked semantic queries?",
        category: "Applied AI & GenAI Systems",
        skill: "RAG Architecture & Vector Retrieval",
        hint: "Discuss semantic chunking with overlap, HNSW index in vector DBs, cross-encoder re-ranking, and hallucination guardrails.",
        expected_focus: "Chunking strategies, embedding distance metrics (cosine), BM25 + vector fusion, and re-ranking latency.",
        difficulty: "Hard"
      },
      {
        question: "Design a high-throughput, low-latency Real-Time Feature Store and Inference Engine for a fraud detection or recommendation system handling 50,000 req/sec. Walk through the streaming ingestion (Kafka/Flink), low-latency key-value store (Redis/Feast), model fallback strategies, and batch offline training pipelines.",
        category: "MLOps & Real-time Systems",
        skill: "Feature Store & Low-Latency Serving",
        hint: "Discuss point-in-time correctness (preventing data leakage), Redis cluster memory sizing, P99 latency SLA (<20ms), and fallback to rule-based heuristics.",
        expected_focus: "Dual-storage (online Redis + offline Parquet/Snowflake), feature freshness, and async inference workers.",
        difficulty: "Hard"
      },
      {
        question: "Architect a distributed training cluster for a 70B parameter Large Language Model. How do you configure Data Parallelism (DDP), Tensor Parallelism (Megatron-LM), and Pipeline Parallelism? Discuss gradient checkpointing, ZeRO stage memory partitioning (DeepSpeed), and InfiniBand network topology.",
        category: "Distributed Deep Learning",
        skill: "Distributed Training & GPU Clustering",
        hint: "Explain 3D parallelism (Data, Tensor, Pipeline), ZeRO-3 memory offloading, all-reduce communication bottlenecks, and checkpointing frequency.",
        expected_focus: "GPU memory math (parameters, activations, optimizer states), NVLink/InfiniBand bandwidth, and failover recovery.",
        difficulty: "Hard"
      },
      {
        question: "Design an end-to-end MLOps deployment pipeline with automated continuous training (CT) and zero-downtime canary deployment. How do you detect Data Drift vs Concept Drift (using KS-Test, Population Stability Index), trigger model shadow testing, and handle automated rollback?",
        category: "MLOps & Model Governance",
        skill: "Model Monitoring & CI/CD Deployment",
        hint: "Distinguish between input distribution shift P(X) vs conditional distribution shift P(Y|X). Explain shadow traffic routing and automated rollback criteria.",
        expected_focus: "Drift statistical tests (PSI, KL-divergence), canary traffic splitting, and continuous evaluation loops.",
        difficulty: "Medium"
      },
      {
        question: "When deploying a Large Language Model (LLM) to production, what techniques reduce inference latency and GPU memory footprint? Compare Quantization (INT8/FP4), KV Caching, and FlashAttention.",
        category: "MLOps & LLM Deployment",
        skill: "Model Optimization & Inference Acceleration",
        hint: "Discuss memory bandwidth bottlenecks in auto-regressive generation, KV cache size calculation, and continuous batching with vLLM.",
        expected_focus: "Quantization trade-offs, KV cache retention, continuous batching, and speculative decoding.",
        difficulty: "Hard"
      }
    ],

    "Technical / DSA Drill": [
      {
        question: "Explain the mathematical formulation and computational complexity of Transformer Self-Attention: Softmax((Q * K^T) / sqrt(d_k)) * V. Why is naive attention O(N^2) in sequence length, and how does FlashAttention reduce memory access overhead by fusing GPU SRAM operations?",
        category: "Deep Learning Foundations",
        skill: "Transformers & Attention Mechanisms",
        hint: "Explain why division by sqrt(d_k) stabilizes gradients, how matrix multiplications Q*K^T scale with sequence length N, and how tiling in SRAM prevents High-Bandwidth Memory (HBM) IO bottlenecks.",
        expected_focus: "Matrix multiplication dimensions, O(N^2) time/memory bottleneck, and FlashAttention tiling.",
        difficulty: "Hard"
      },
      {
        question: "Given an unsorted collection of 1,000,000 high-dimensional feature vectors (d=768), how do you find the K nearest neighbors efficiently? Compare exact brute-force search O(N*D) with Approximate Nearest Neighbors (ANN) using HNSW (Hierarchical Navigable Small World) graphs or Inverted File Index (IVF).",
        category: "Data Structures & Vector Search",
        skill: "Approximate Nearest Neighbors & Graph Traversal",
        hint: "Contrast Euclidean distance vs Cosine similarity. Explain multi-layer skip-list graph traversal in HNSW and inverted cluster indexing in IVF.",
        expected_focus: "Recall vs latency trade-offs, graph search complexity O(log N), and vector quantization (PQ).",
        difficulty: "Hard"
      },
      {
        question: "In modern deep learning frameworks (PyTorch/TensorFlow), how is the computational DAG (Directed Acyclic Graph) built and traversed during the forward and backward passes? Walk through the Topological Sort algorithm (Kahn's or DFS) used to schedule backward gradient execution.",
        category: "Algorithms & Computational Graphs",
        skill: "Graph Algorithms & Autograd",
        hint: "Discuss in-degrees of nodes in the autograd graph, topological ordering for reverse-mode automatic differentiation, and chain rule accumulation.",
        expected_focus: "DAG node dependencies, cycle validation, queue-based Kahn's algorithm, and space complexity.",
        difficulty: "Medium"
      },
      {
        question: "Explain how Byte-Pair Encoding (BPE) or WordPiece tokenization algorithms work algorithmically. How would you design an algorithm using Dynamic Programming to find the optimal subword segmentation or sequence edit distance?",
        category: "Algorithms & NLP",
        skill: "Dynamic Programming & String Algorithms",
        hint: "Explain greedy pair frequency merging in BPE vs unigram probabilistic tokenization. Walk through 2D DP matrix for Levenshtein edit distance with O(M*N) time.",
        expected_focus: "Vocabulary initialization, frequency counting hash tables, and DP recurrence relation.",
        difficulty: "Hard"
      },
      {
        question: "How does a 2D Convolution operation work algorithmically over an input image tensor? Walk through sliding window strides, padding calculations, dilation, and explain how Im2Col transforms convolution into a GEMM (General Matrix Multiply) operation.",
        category: "Algorithms & Tensor Computation",
        skill: "Tensor Operations & Convolution Algorithms",
        hint: "Formulate output dimensions: floor((W - K + 2P)/S) + 1. Explain how Im2Col unrolls sliding filter receptive fields into 2D matrix rows to leverage BLAS/cuBLAS matrix multiplication.",
        expected_focus: "Computational complexity, cache locality, and matrix multiplication equivalence.",
        difficulty: "Medium"
      }
    ],

    "Behavioral & HR STAR Drill": [
      {
        question: "Tell me about a time when a machine learning model or critical AI feature performed poorly, hallucinated, or produced biased outputs in production. Walk me through your Situation, Task, Action to diagnose the root cause, and the measurable Result or safeguards you implemented.",
        category: "Production Incident & Ethics",
        skill: "Model Reliability & Incident Response",
        hint: "Structure using STAR: Situation (model failure in staging/prod), Task (debugging and stabilizing), Action (root cause analysis, guardrails, data filtering), Result (quantifiable reduction in error rate).",
        expected_focus: "Accountability, systematic triage, safety guardrails, and post-mortem lessons.",
        difficulty: "Medium"
      },
      {
        question: "Describe a scenario where product managers or business stakeholders wanted to rush an AI/ML feature into production before you validated safety, data leakage, or evaluation benchmarks. How did you communicate technical risk, handle disagreement, and negotiate a phased launch?",
        category: "Stakeholder Negotiation & Ethics",
        skill: "Cross-Functional Communication & Risk Management",
        hint: "Explain how you translated technical risks (e.g., false positive costs, data leakage) into business metrics, proposed compromise (shadow deployment or beta testing), and preserved team trust.",
        expected_focus: "Diplomatic communication, data-driven reasoning, and collaborative risk mitigation.",
        difficulty: "Hard"
      },
      {
        question: "Describe a project where you had to balance short-term delivery pressure against long-term engineering health (such as investing in automated model evaluation pipelines, addressing technical debt, or improving data labeling quality). How did you prioritize tasks and deliver on time?",
        category: "Prioritization & Technical Debt",
        skill: "Engineering Prioritization & Task Management",
        hint: "Discuss how you scoped an MVP while establishing milestones for debt pay-down, automated testing, or pipeline refactoring.",
        expected_focus: "Pragmatism, trade-off evaluation, and measurable project outcomes.",
        difficulty: "Medium"
      },
      {
        question: "Tell me about an unassigned problem or optimization (such as drastically reducing cloud GPU training costs, improving inference throughput, or fixing data quality) that you noticed and spearheaded proactively. What was the impact?",
        category: "Proactivity & Engineering Ownership",
        skill: "Proactive Problem Solving & Impact",
        hint: "Highlight how you identified the bottleneck independently, drafted a proposal/prototype, benchmarked improvements, and delivered quantifiable cost/latency savings.",
        expected_focus: "Ownership mindset, metric-driven validation, and organizational impact.",
        difficulty: "Medium"
      },
      {
        question: "Describe a scenario where you had to explain a complex algorithmic decision, trade-off, or failure mode to non-technical stakeholders or executive leadership. How did you structure your communication to secure buy-in?",
        category: "Communication & Leadership",
        skill: "Technical Translation & Executive Presence",
        hint: "Focus on using analogies, clear business trade-offs (precision vs recall in terms of lost revenue or user friction), and visual summaries instead of jargon.",
        expected_focus: "Audience empathy, structured storytelling, and decision alignment.",
        difficulty: "Hard"
      }
    ]
  },

  // ==========================================
  // 2. Full Stack Engineer
  // ==========================================
  "Full Stack Engineer": {
    "System Architecture & Design": [
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
        question: "How do WebSockets and Server-Sent Events (SSE) compare for real-time applications like a collaborative dashboard or chat? Walk through connection scaling with Redis Pub/Sub.",
        category: "Real-Time Systems",
        skill: "WebSockets & Distributed Pub-Sub",
        hint: "Contrast bi-directional full-duplex WebSockets with unidirectional SSE, and explain horizontal scaling with sticky sessions or Redis adapter.",
        expected_focus: "Protocol handshakes, backpressure, heartbeat ping/pong, and multi-node broadcast.",
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
        question: "Design an API Gateway architecture for microservices handling authentication, rate limiting, request validation, and aggregated responses for web and mobile clients.",
        category: "API & Gateway Architecture",
        skill: "API Gateway & Microservices",
        hint: "Discuss Backend-for-Frontend (BFF) pattern, token parsing middleware, rate-limiting algorithms, and response compression.",
        expected_focus: "Latency impact, central authentication, circuit breaking, and caching.",
        difficulty: "Hard"
      }
    ],

    "Technical / DSA Drill": [
      {
        question: "Design and implement an LRU (Least Recently Used) Cache with O(1) time complexity for both get(key) and put(key, value) operations. Which underlying data structures do you combine and why?",
        category: "Data Structures & Memory Design",
        skill: "LRU Cache & Linked Hash Map",
        hint: "Combine a Hash Map for O(1) lookup with a Doubly Linked List for O(1) node eviction and insertion at head.",
        expected_focus: "Data structure synergy, pointer manipulation, boundary edge cases (capacity 1, overwrite).",
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
        question: "Given a DOM-like hierarchical tree structure, how would you write an algorithm to find the lowest common ancestor (LCA) of two target nodes? Provide both recursive and iterative approaches.",
        category: "Tree Algorithms & DOM",
        skill: "Tree Traversal & Lowest Common Ancestor",
        hint: "In a binary/n-ary tree, traverse post-order: if current node matches either target, return current node; if both left and right return non-null, current is LCA.",
        expected_focus: "Time complexity O(N), call stack depth, and handling missing nodes.",
        difficulty: "Medium"
      },
      {
        question: "Solve the Sliding Window Maximum problem: given an array of integers and a window size k, return the maximum element in each sliding window in O(N) linear time.",
        category: "Algorithms & Double-ended Queues",
        skill: "Sliding Window & Monotonic Deque",
        hint: "Use a monotonic decreasing deque to store indices of candidate maximums, removing indices outside window bounds and elements smaller than the incoming value.",
        expected_focus: "Amortized O(1) per element, monotonic invariant, and boundary indexing.",
        difficulty: "Hard"
      },
      {
        question: "Given a list of prerequisite software packages and dependencies, write an algorithm to determine if all packages can be installed without circular dependency deadlock.",
        category: "Graph Algorithms",
        skill: "Topological Sort & Cycle Detection",
        hint: "Model packages as a directed graph. Detect cycles using Kahn's BFS algorithm with in-degrees or DFS with 3-color visiting states (white/gray/black).",
        expected_focus: "Graph representation (adjacency list), cycle detection logic, and topological ordering.",
        difficulty: "Medium"
      }
    ],

    "Behavioral & HR STAR Drill": [
      {
        question: "Tell me about a high-priority production bug or outage in a web application you deployed. Walk through your Situation, Task, Action to restore service, and the Resulting preventative measures.",
        category: "Production Incident Response",
        skill: "Incident Management & STAR",
        hint: "Highlight calm triage, rollback strategy or hotfix, clear stakeholder communication, and post-mortem action items.",
        expected_focus: "Ownership, root cause analysis, logging improvements, and blameless post-mortem.",
        difficulty: "Medium"
      },
      {
        question: "Describe a situation where you had a strong disagreement with a backend or frontend peer regarding API schema design or state management. How did you resolve the deadlock?",
        category: "Team Collaboration & Conflict",
        skill: "Engineering Conflict Resolution",
        hint: "Focus on presenting technical trade-offs objectively (payload size, latency, developer velocity), testing prototypes, and reaching consensus.",
        expected_focus: "Diplomacy, data-driven compromise, and team alignment.",
        difficulty: "Hard"
      },
      {
        question: "Walk through a project where product requirements shifted drastically midway through development. How did you realign your tasks and deliver a reliable release?",
        category: "Agility & Adaptability",
        skill: "Requirement Management & Scope Control",
        hint: "Discuss re-evaluating architecture assumptions, modular refactoring, clear communication with product managers, and scope prioritization.",
        expected_focus: "Adaptability, agile mindset, and delivery reliability.",
        difficulty: "Medium"
      },
      {
        question: "Tell me about a time you identified significant technical debt (e.g. monolithic legacy code, poor test coverage) and convinced management to allocate sprint cycles to refactor it.",
        category: "Technical Leadership & Proactivity",
        skill: "Advocating for Code Quality",
        hint: "Quantify the cost of debt (bug rate, slower onboarding, developer hours) and show how the refactor accelerated subsequent feature velocity.",
        expected_focus: "Business justification, incremental refactoring plan, and measurable impact.",
        difficulty: "Hard"
      },
      {
        question: "Describe a scenario where you mentored a junior engineer or onboarded a new team member onto a complex codebase. What strategies ensured their rapid productivity?",
        category: "Mentorship & Culture",
        skill: "Engineering Mentorship & Onboarding",
        hint: "Discuss pairing, documentation improvements, breaking down complex modules into digestible starter tasks, and empathetic code reviews.",
        expected_focus: "Empathy, pedagogical clarity, and scaling team knowledge.",
        difficulty: "Medium"
      }
    ]
  },

  // ==========================================
  // 3. Backend Developer
  // ==========================================
  "Backend Developer": {
    "System Architecture & Design": [
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
        question: "How do you implement database horizontal sharding versus read replicas? How do you manage consistent hashing, shard key selection, and cross-shard queries?",
        category: "Distributed Databases",
        skill: "Sharding & Data Partitioning",
        hint: "Discuss virtual nodes on hash rings, hot spots prevention, and two-phase commits for cross-shard updates.",
        expected_focus: "Consistent hashing ring, re-balancing overhead, and CAP theorem trade-offs.",
        difficulty: "Hard"
      },
      {
        question: "Design an asynchronous event-driven architecture using Kafka or RabbitMQ for order processing. How do you guarantee exactly-once processing semantics and prevent message loss?",
        category: "Message Brokers & Streaming",
        skill: "Event-Driven Architecture & Kafka",
        hint: "Discuss idempotency keys, transactional outbox pattern, consumer offset commit strategies, and dead-letter queues.",
        expected_focus: "At-least-once vs exactly-once semantics, consumer lag monitoring, and partition ordering.",
        difficulty: "Hard"
      }
    ],

    "Technical / DSA Drill": [
      {
        question: "Design a thread-safe, bounded blocking queue in code without race conditions or busy waiting. How do condition variables (wait/signal/notify) prevent deadlocks?",
        category: "Concurrency & Data Structures",
        skill: "Thread-Safe Blocking Queue",
        hint: "Use mutex lock with two condition variables (not_full, not_empty) to coordinate producer and consumer threads.",
        expected_focus: "Race condition avoidance, lock granularity, and spurious wakeups handling.",
        difficulty: "Hard"
      },
      {
        question: "Given a massive log file of 100 million URL requests, find the Top K most frequently requested endpoints with limited RAM (e.g. 100MB). Walk through your algorithm and space complexity.",
        category: "Algorithms & Streaming Data",
        skill: "Top K Elements & Min-Heap",
        hint: "Discuss MapReduce chunking with hash partitioning, followed by a local hash table frequency count and a Min-Heap of size K.",
        expected_focus: "External sorting/hashing, Min-Heap O(N log K) time, and memory bound compliance.",
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
        question: "Implement a Trie (Prefix Tree) data structure supporting insert, search, and startsWith operations. How would you optimize it for memory when storing 10 million English words?",
        category: "Tree Data Structures",
        skill: "Trie & Memory Optimization",
        hint: "Contrast standard 26-pointer array per node with hash map children or Radix Tree (compressed prefix tree) nodes.",
        expected_focus: "Prefix query time O(L), node space footprint, and compression techniques.",
        difficulty: "Medium"
      },
      {
        question: "Explain the internal structure of B-Trees and B+ Trees used in relational database indexes. Why are B+ Trees favored over Binary Search Trees or Hash Tables for disk storage?",
        category: "Database Internals & Trees",
        skill: "B+ Tree Index Internals",
        hint: "Highlight high fan-out (low tree depth), sequential leaf node linked list for range scans, and block IO page alignment.",
        expected_focus: "Disk seek reduction, range query O(log N + K), and cache locality.",
        difficulty: "Hard"
      }
    ],

    "Behavioral & HR STAR Drill": [
      {
        question: "Describe a scenario where a database migration or critical backend release caused downtime or data corruption. Walk through your STAR response from initial detection to full recovery.",
        category: "Data Integrity & Incident Response",
        skill: "Production Incident & STAR",
        hint: "Focus on rollback scripts, point-in-time database restoration, transparent communication, and preventative migration tests.",
        expected_focus: "Accountability, incident composure, data recovery validation, and migration safety checklists.",
        difficulty: "Hard"
      },
      {
        question: "Tell me about a time you had to push back against unreasonable product deadlines to protect backend reliability, security, or scalability. How did you frame the conversation?",
        category: "Stakeholder Management & Boundaries",
        skill: "Negotiating Engineering Scope",
        hint: "Show how you tied engineering concerns directly to business risks (downtime cost, lost transactions) and offered phased MVP options.",
        expected_focus: "Professional assertiveness, risk quantification, and collaborative compromise.",
        difficulty: "Medium"
      },
      {
        question: "Describe a project where you solved a severe backend bottleneck that was degrading user latency or spiking server costs. What was your investigation methodology?",
        category: "Performance Optimization & Root Cause",
        skill: "Profiling & Bottleneck Resolution",
        hint: "Detail APM profiling (flamegraphs, query analysis), identifying the specific root cause (e.g. unindexed query, lock contention), and the quantifiable result.",
        expected_focus: "Methodical debugging, metric measurement, and measurable latency reduction.",
        difficulty: "Medium"
      },
      {
        question: "Tell me about a disagreement with a team architect over database choice (e.g. SQL vs Document NoSQL vs Key-Value). How did you evaluate trade-offs and reach a decision?",
        category: "Architecture Debate & Consensus",
        skill: "Technical Decision Making",
        hint: "Discuss evaluating access patterns, write/read ratios, consistency requirements, and running benchmarks rather than relying on dogma.",
        expected_focus: "Objective evaluation, benchmark evidence, and professional collaboration.",
        difficulty: "Hard"
      },
      {
        question: "Describe a time when you had to take ownership of a legacy, undocumented backend service with high error rates. How did you stabilize and modernize it?",
        category: "Legacy Systems & Ownership",
        skill: "Code Modernization & SRE",
        hint: "Discuss adding observability/telemetry first, writing regression tests around critical paths, and refactoring incrementally.",
        expected_focus: "Courage, systematic risk containment, and incremental improvement.",
        difficulty: "Medium"
      }
    ]
  },

  // ==========================================
  // 4. AWS / DevOps & Cloud Engineer
  // ==========================================
  "AWS / DevOps & Cloud Engineer": {
    "System Architecture & Design": [
      {
        question: "Design a highly available, multi-AZ architecture on AWS handling 100,000 active users. Detail VPC subnetting, ALB, Auto Scaling Groups, RDS Multi-AZ failover, and CloudFront caching.",
        category: "Cloud Architecture & Scalability",
        skill: "AWS High Availability Architecture",
        hint: "Discuss public vs private subnets, NAT Gateways, synchronous RDS standby replication, and RTO/RPO targets.",
        expected_focus: "Fault domain isolation, DNS failover (Route 53), and auto-scaling cooldown metrics.",
        difficulty: "Hard"
      },
      {
        question: "How do Kubernetes Deployments handle Zero-Downtime Rolling Updates? How do Liveness and Readiness probes prevent routing traffic to unhealthy containers?",
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

    "Technical / DSA Drill": [
      {
        question: "Given a network CIDR block (e.g., 10.0.0.0/16) and a list of required subnet sizes, write an algorithm to allocate non-overlapping subnets. How do binary bitwise operations validate IP ranges?",
        category: "Networking Algorithms & Bitwise",
        skill: "CIDR Subnet Allocation & Bitwise Ops",
        hint: "Convert IPs to 32-bit unsigned integers. Use bitmasks (32 - prefix) to calculate network boundaries and check for overlaps.",
        expected_focus: "Bitwise shifts, IP boundary checks, and greedy or interval tree allocation.",
        difficulty: "Hard"
      },
      {
        question: "In Terraform / CloudFormation, how does the engine construct the Dependency DAG (Directed Acyclic Graph) for infrastructure resources? Write out the Topological Sort algorithm with cycle detection.",
        category: "Graph Algorithms & IaC",
        skill: "DAG Execution & Cycle Detection",
        hint: "Model resources as nodes and references (e.g. vpc_id) as directed edges. Use Kahn's algorithm or DFS with recursion stack tracking.",
        expected_focus: "In-degree tracking, cycle detection exception, and parallel level-by-level resource provisioning.",
        difficulty: "Medium"
      },
      {
        question: "Design an algorithm to parse a high-volume live server log stream and alert when error status codes (HTTP 5xx) exceed 5% over any sliding 60-second window in real-time.",
        category: "Streaming Algorithms & Queues",
        skill: "Sliding Window Log Aggregation",
        hint: "Use a circular buffer or sliding window bucket array indexed by second % 60, storing total requests and error counts.",
        expected_focus: "O(1) update and query time, fixed memory footprint, and thread safety.",
        difficulty: "Medium"
      },
      {
        question: "Implement the Token Bucket rate limiting algorithm for cloud API gateways. How do you handle continuous fractional token refill without floating point drift or locking delays?",
        category: "Algorithms & Rate Limiting",
        skill: "Token Bucket Algorithm",
        hint: "Store last_refill_timestamp and compute tokensToAdd = (now - last_refill) * refill_rate, clamping to bucket_capacity.",
        expected_focus: "Lazy refill on request arrival, integer arithmetic, and microsecond precision.",
        difficulty: "Hard"
      },
      {
        question: "Explain how Linux process memory management and CFS (Completely Fair Scheduler) work. What data structure does CFS use to schedule tasks and why?",
        category: "OS Internals & Data Structures",
        skill: "Linux CFS & Red-Black Trees",
        hint: "CFS uses a Red-Black Tree ordered by virtual runtime (vruntime), always selecting the leftmost node with O(log N) operations.",
        expected_focus: "Virtual runtime concept, Red-Black Tree self-balancing, and container CPU throttling.",
        difficulty: "Hard"
      }
    ],

    "Behavioral & HR STAR Drill": [
      {
        question: "Tell me about a catastrophic cloud infrastructure failure or DNS outage you managed. Walk through your STAR response: initial incident command, mitigation, and post-mortem.",
        category: "Incident Command & SRE",
        skill: "Major Incident Management & STAR",
        hint: "Highlight communication cadence (internal status page, customer updates), rolling back bad configs, and writing a blameless post-mortem.",
        expected_focus: "Crisis leadership, systematic triage, and long-term architectural prevention.",
        difficulty: "Hard"
      },
      {
        question: "Describe a situation where developers were bypassing infrastructure guardrails or security policies to deploy faster. How did you address the friction without stalling delivery?",
        category: "DevOps Culture & Collaboration",
        skill: "DevSecOps Culture Transformation",
        hint: "Discuss building paved-path automated templates, integrating security scans into CI invisibly, and educating engineering teams.",
        expected_focus: "Empathy, developer enablement, and building trust across teams.",
        difficulty: "Medium"
      },
      {
        question: "Tell me about a major cloud cost optimization initiative you led. How did you identify waste, negotiate resource rightsizing with development teams, and verify savings?",
        category: "FinOps & Cross-Functional Influence",
        skill: "Cloud FinOps & Stakeholder Influence",
        hint: "Quantify dollar savings (e.g. idle compute, unattached EBS, Graviton migrations) and explain how you gained buy-in from engineering leads.",
        expected_focus: "FinOps metrics, data-driven negotiation, and quantifiable ROI.",
        difficulty: "Medium"
      },
      {
        question: "Describe a project where you migrated mission-critical stateful infrastructure (e.g. production databases or Kubernetes clusters) with zero downtime. How did you plan it?",
        category: "High-Stakes Execution",
        skill: "Zero-Downtime Migration Planning",
        hint: "Discuss dual-writing, replica synchronization verification, dry-run cutovers in staging, and explicit rollback triggers.",
        expected_focus: "Meticulous planning, risk hedging, and flawless execution.",
        difficulty: "Hard"
      },
      {
        question: "Tell me about a time when an on-call alert was firing frequently, causing alert fatigue. How did you audit and remediate the alerting strategy?",
        category: "SRE Health & Alert Hygiene",
        skill: "Alert Fatigue Remediation",
        hint: "Explain categorizing actionable pages vs non-actionable warnings, calibrating thresholds to SLO/SLA impact, and automating runbooks.",
        expected_focus: "SLO-driven alerting, operational sustainability, and team well-being.",
        difficulty: "Medium"
      }
    ]
  },

  // ==========================================
  // 5. Cybersecurity Analyst & Engineer
  // ==========================================
  "Cybersecurity Analyst & Engineer": {
    "System Architecture & Design": [
      {
        question: "Explain Zero Trust Architecture (NIST SP 800-207). How does it replace traditional perimeter-based security using continuous authentication, micro-segmentation, and least privilege?",
        category: "Enterprise Security Architecture",
        skill: "Zero Trust Principles & Identity",
        hint: "Explain 'never trust, always verify', contextual signals (device posture, geo-location, MFA), and software-defined perimeters.",
        expected_focus: "Policy Decision Points (PDP), Policy Enforcement Points (PEP), and identity-centric access control.",
        difficulty: "Medium"
      },
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

    "Technical / DSA Drill": [
      {
        question: "Design an algorithm to detect malicious IP brute-force attacks in high-speed network traffic. How do you track request frequencies per IP over a rolling 5-minute window in limited memory?",
        category: "Security Algorithms & Data Structures",
        skill: "Count-Min Sketch & Sliding Window",
        hint: "Explain Count-Min Sketch or Hash Map with sliding bucket timestamps to identify heavy hitters with sub-linear memory.",
        expected_focus: "Space complexity, hash collisions tolerance, and threshold alerting.",
        difficulty: "Hard"
      },
      {
        question: "Explain how string matching algorithms (such as Aho-Corasick or Boyer-Moore) are used by Intrusion Detection Systems (Snort/Suricata) to match thousands of malware signatures in packet payloads simultaneously.",
        category: "Pattern Matching Algorithms",
        skill: "Aho-Corasick Multi-Pattern Search",
        hint: "Aho-Corasick constructs a Trie with failure transitions (suffix links), matching all signatures in a single linear pass O(N + M).",
        expected_focus: "Trie construction, failure link transitions, and line-rate packet inspection.",
        difficulty: "Hard"
      },
      {
        question: "Explain the Fast Modular Exponentiation algorithm (repeated squaring) used in RSA cryptographic key generation and decryption. Walk through its time complexity compared to naive multiplication.",
        category: "Cryptographic Algorithms",
        skill: "Modular Exponentiation & Complexity",
        hint: "Compute a^b mod m in O(log b) steps by inspecting binary bits of exponent b, squaring base at each step.",
        expected_focus: "Binary exponent decomposition, constant-time execution against timing attacks, and bitwise operations.",
        difficulty: "Medium"
      },
      {
        question: "Given a network connectivity matrix of enterprise servers, write an algorithm to find all potential Attack Paths an adversary could traverse from an untrusted DMZ server to the Core Database.",
        category: "Graph Algorithms & Threat Modeling",
        skill: "Attack Graph Traversal (DFS/BFS)",
        hint: "Model servers and firewall port rules as a directed graph. Traverse using BFS/Dijkstra to find shortest exploitation path or all reachable paths.",
        expected_focus: "Path reconstruction, visited set cycle prevention, and vulnerability weight modeling.",
        difficulty: "Medium"
      },
      {
        question: "How does a Bloom Filter work mathematically in security systems to check if a malicious hash or URL is present in a database of 1 billion known threat indicators?",
        category: "Probabilistic Data Structures",
        skill: "Bloom Filter & False Positive Math",
        hint: "Explain bit array of size M, K independent hash functions, zero false negatives guarantee, and the false positive probability formula (1 - e^(-kn/m))^k.",
        expected_focus: "Bitwise set operations, hash function independence, and trade-off between memory and false positive rate.",
        difficulty: "Hard"
      }
    ],

    "Behavioral & HR STAR Drill": [
      {
        question: "Tell me about a time you investigated a critical security alert under high pressure where initial indicators were ambiguous. Walk through your STAR triage and decision process.",
        category: "Security Triage & STAR",
        skill: "Threat Triage & Incident Investigation",
        hint: "Highlight hypothesis testing, checking telemetry/logs without jumping to conclusions, and preventing premature escalation or panic.",
        expected_focus: "Methodical forensic analysis, composure under uncertainty, and decisive action.",
        difficulty: "Medium"
      },
      {
        question: "Describe a situation where software engineers resisted implementing a required security control (e.g. mandatory MFA, secrets rotation, strict egress firewalls). How did you gain their cooperation?",
        category: "Security Culture & Persuasion",
        skill: "Security Advocacy & Influence",
        hint: "Focus on understanding their workflow friction, demonstrating the real exploit risk through a benign PoC, and making the security tool seamless to use.",
        expected_focus: "Empathy, practical risk demonstration, and building collaborative security champions.",
        difficulty: "Hard"
      },
      {
        question: "Tell me about an incident where you discovered a vulnerability or data exposure in a third-party vendor or executive system. How did you communicate the risk to leadership confidentially?",
        category: "Executive Communication & Confidentiality",
        skill: "Executive Security Reporting",
        hint: "Discuss strict need-to-know disclosure, framing technical impact in terms of legal/reputational consequences, and providing an actionable remediation roadmap.",
        expected_focus: "Discretion, professional maturity, and executive clarity.",
        difficulty: "Hard"
      },
      {
        question: "Describe a time when a suspected false positive alert turned out to be an actual stealthy security compromise. How did you identify the subtle discrepancy?",
        category: "Threat Hunting & Diligence",
        skill: "Threat Hunting & Anomaly Detection",
        hint: "Explain noticing small anomalies in parent-child process trees, unusual command-line arguments, or off-hours traffic that automated filters overlooked.",
        expected_focus: "Analytical curiosity, deep log inspection, and persistence.",
        difficulty: "Medium"
      },
      {
        question: "Tell me about how you stay updated on zero-day vulnerabilities (like Log4j or XZ Utils backdoor) and how you rapidly assess enterprise exposure within 24 hours.",
        category: "Vulnerability Management & Agility",
        skill: "Rapid Zero-Day Triage",
        hint: "Discuss reliable threat intel sources (CISA KEV, security research advisories), rapid SBOM/dependency queries, and deploying virtual patches or WAF rules immediately.",
        expected_focus: "Proactive intelligence, inventory visibility, and speed of response.",
        difficulty: "Medium"
      }
    ]
  }
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

// Modality normalization helper
export const resolveModalityKey = (modality = "") => {
  const norm = String(modality || "").toLowerCase().trim();
  if (norm.includes("star") || norm.includes("behavioral") || norm.includes("hr")) {
    return "Behavioral & HR STAR Drill";
  }
  if (norm.includes("dsa") || norm.includes("drill") || norm.includes("algo") || norm.includes("coding")) {
    return "Technical / DSA Drill";
  }
  if (norm.includes("full") || norm.includes("combined") || norm.includes("tier")) {
    return "Full Tier-1 SDE Mock";
  }
  return "System Architecture & Design";
};

// General fallback list containing high-yield questions
export const defaultQuestions = [
  ...domainModalityQuestionsPool["Full Stack Engineer"]["System Architecture & Design"],
  ...domainModalityQuestionsPool["AI/ML Engineer"]["System Architecture & Design"],
  ...domainModalityQuestionsPool["Backend Developer"]["System Architecture & Design"],
];

/**
 * Dynamically picks questions grounded strictly in the user's registered target domain
 * and the specific Interview Modality / Category selected.
 * 
 * For "Full Tier-1 SDE Mock (Combined)", intelligently sequences:
 * Q1 -> Technical / DSA Drill
 * Q2 -> System Architecture & Design
 * Q3 -> Behavioral & HR STAR Drill
 * Q4 -> Technical / DSA Drill
 * Q5 -> System Architecture & Design
 */
export const getDynamicQuestion = (
  userRole = "Backend Developer",
  questionNumber = 1,
  usedQuestions = [],
  modality = "System Architecture & Design",
  difficulty = "Medium"
) => {
  const domainKey = resolveDomainKey(userRole);
  const modalityKey = resolveModalityKey(modality);

  let pool = [];
  if (modalityKey === "Full Tier-1 SDE Mock") {
    const stagePattern = [
      "Technical / DSA Drill",
      "System Architecture & Design",
      "Behavioral & HR STAR Drill",
      "Technical / DSA Drill",
      "System Architecture & Design"
    ];
    const stageModality = stagePattern[(questionNumber - 1) % stagePattern.length];
    pool = domainModalityQuestionsPool[domainKey]?.[stageModality] || [];
  } else {
    pool = domainModalityQuestionsPool[domainKey]?.[modalityKey] || [];
  }

  if (!pool || pool.length === 0) {
    pool = domainModalityQuestionsPool["Backend Developer"]["System Architecture & Design"];
  }

  // Filter out questions already asked in this session
  const usedTexts = new Set(
    usedQuestions.map((q) => (typeof q === "string" ? q : q?.question)).filter(Boolean)
  );
  const available = pool.filter((q) => !usedTexts.has(q.question));
  const candidates = available.length > 0 ? available : pool;

  const randomIndex = Math.floor(Math.random() * candidates.length);
  const selected = candidates[randomIndex] || pool[0];

  return {
    ...selected,
    id: `q_${domainKey.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}_${questionNumber}`,
    question_number: questionNumber,
    target_role: domainKey,
    modality: modalityKey,
    difficulty: difficulty || selected.difficulty || "Medium",
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
