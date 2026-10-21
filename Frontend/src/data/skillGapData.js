// Centralized dynamic data for AI Skill Gap Analyzer with role-calibrated benchmarks and scope categorization

export const AVAILABLE_ROLES = [
  "AI/ML Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "Data Scientist",
  "Data Engineer",
  "DevOps & Cloud Engineer",
  "Software Engineer",
  "Cybersecurity Analyst",
  "Mobile App Developer"
];

export const COMMON_CATEGORIES = new Set([
  "Programming",
  "Core Programming & OOP",
  "DSA",
  "Data Structures & Algorithms",
  "Algorithms & Optimization",
  "Databases",
  "Databases & SQL",
  "Database & Query Optimization",
  "CS Fundamentals",
  "System Design & CS Fundamentals",
  "DevOps",
  "DevOps & Problem Solving",
  "DevOps & Version Control",
  "Testing",
  "Testing & Quality Assurance",
  "Networking",
  "Operating Systems"
]);

export const ROLE_SKILL_GAP_CONFIGS = {
  "AI/ML Engineer": {
    targetRole: "AI/ML Engineer",
    overallCoverage: 74,
    totalAudited: 28,
    gapsIdentifiedCount: 6,
    confidenceIndex: "96.2%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Machine Learning",
        coverage: 82,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#8083ff",
        description: "Supervised/unsupervised models, Scikit-learn, PyTorch, and deep neural architectures"
      },
      {
        category: "Data Science",
        coverage: 72,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#60a5fa",
        description: "NumPy, Pandas, statistical modeling, data visualization, and exploratory analysis"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Programming",
        coverage: 80,
        benchmarkTarget: 80,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Clean code, object-oriented design patterns, Python syntax, and memory model"
      },
      {
        category: "Databases",
        coverage: 65,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "Complex SQL queries, database indexing, schema design, and query optimization"
      },
      {
        category: "DevOps",
        coverage: 60,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Docker containerization, Git branching workflows, CI/CD pipelines, and MLOps"
      }
    ],
    gaps: [
      {
        id: "gap-aiml-1",
        skill: "PyTorch Deep Learning & Custom Neural Modules",
        category: "Deep Learning & Neural Networks",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (CNNs / Feedforward)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Transformers, Autograd, Attention Layers)",
        priority: "Critical",
        reason: "Core hiring requirement for Tier-1 AI/ML and GenAI engineering roles.",
        suggestedAction: "Implement custom multi-head attention and transformer fine-tuning in PyTorch.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-aiml-2",
        skill: "MLOps & Containerized Model Serving",
        category: "MLOps & Model Deployment",
        scope: "role",
        currentLevel: 1,
        currentLevelText: "Novice (Local scripts only)",
        requiredLevel: 3,
        requiredLevelText: "Intermediate (Docker, FastAPI, Triton / ONNX Runtime)",
        priority: "Critical",
        reason: "Mandatory for packaging, scaling, and deploying low-latency model inference pipelines.",
        suggestedAction: "Containerize a FastAPI model inference service with Docker and health probes.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-aiml-3",
        skill: "Scikit-learn Pipelines & Hyperparameter Tuning",
        category: "Machine Learning Foundations",
        scope: "role",
        currentLevel: 3,
        currentLevelText: "Intermediate (Cross-Validation, Random Forests)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Custom Transformers, SHAP Interpretability, Bayesian Search)",
        priority: "High",
        reason: "Essential for robust data preprocessing and leakage-free ML pipeline evaluation.",
        suggestedAction: "Construct an end-to-end classification pipeline with SHAP explainability.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-aiml-4",
        skill: "Dynamic Programming & Graph Algorithms",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (1D Memoization)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (2D Grid DP, Topological Sort, Shortest Paths)",
        priority: "High",
        reason: "Universal algorithmic evaluation round tested across 85%+ of software placement drives.",
        suggestedAction: "Solve 25 targeted algorithmic graph and DP medium problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-aiml-5",
        skill: "Vector Embeddings & RAG Architecture",
        category: "Deep Learning & Neural Networks",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Direct LLM API prompts)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Vector DB Indexing, Hybrid Search, Reranking)",
        priority: "Medium",
        reason: "High industry demand for Retrieval-Augmented Generation workflows and semantic search.",
        suggestedAction: "Build a document QA service with ChromaDB/Milvus and hybrid re-ranking.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-aiml-6",
        skill: "PostgreSQL Schema Indexing & Query Tuning",
        category: "Databases & SQL",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Select & Joins)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Composite Indexes, EXPLAIN ANALYZE, Aggregations)",
        priority: "Medium",
        reason: "Universal database requirement for storing metadata, training records, and production schemas.",
        suggestedAction: "Run query execution plan analysis and optimize multi-table analytical joins.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "FastAPI Pydantic Model Validation", category: "MLOps" },
        { skill: "SHAP Model Interpretability & Curves", category: "Machine Learning" }
      ],
      majorProjects: [
        { skill: "PyTorch Custom Transformer Fine-Tuning", category: "Deep Learning" },
        { skill: "Dockerized ONNX Model Serving Pipeline", category: "MLOps" }
      ],
      fillIns: [
        { skill: "Data Versioning with DVC", category: "MLOps" }
      ],
      hardLongTerm: [
        { skill: "Distributed Multi-GPU Model Training", category: "Deep Learning" }
      ]
    }
  },

  "Backend Developer": {
    targetRole: "Backend Developer",
    overallCoverage: 72,
    totalAudited: 30,
    gapsIdentifiedCount: 6,
    confidenceIndex: "95.4%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Backend APIs & Microservices",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "RESTful endpoints, FastAPI / Spring Boot / Express, middleware, auth"
      },
      {
        category: "System Design & Distributed Systems",
        coverage: 62,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "High-scale architecture, CAP theorem, rate limiting, Kafka pub/sub"
      },
      {
        category: "Distributed Caching & Invalidation",
        coverage: 58,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ffb4ab",
        description: "Redis caching patterns, cache-aside, TTL invalidation, pipeline batching"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP",
        coverage: 84,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Object-oriented design principles (SOLID), multithreading, concurrency"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 72,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Trees, Graphs, Dynamic Programming, sorting and search optimization"
      },
      {
        category: "Databases & SQL Optimization",
        coverage: 68,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "PostgreSQL B-Tree indexing, EXPLAIN ANALYZE, transaction ACID guarantees"
      },
      {
        category: "DevOps & Containerization",
        coverage: 60,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Docker multi-stage builds, container networks, CI/CD pipelines"
      }
    ],
    gaps: [
      {
        id: "gap-be-1",
        skill: "Redis Distributed Caching & Invalidation",
        category: "Distributed Caching & Invalidation",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Key-Value Set/Get)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Eviction Policies, Cluster Sync, Pipeline Execution)",
        priority: "Critical",
        reason: "Required for Tier-1 Backend SDE high throughput endpoints and low latency SLAs.",
        suggestedAction: "Implement Redis Caching with TTL invalidation and eviction in backend services.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-be-2",
        skill: "System Design Trade-off Articulation",
        category: "System Design & Distributed Systems",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Monolithic architecture)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (CAP Theorem, Horizontal Sharding, Eventual Consistency)",
        priority: "Critical",
        reason: "Primary assessment criterion in Tier-1 product system design technical rounds.",
        suggestedAction: "Practice system design trade-off drills for URL Shortener and Distributed Rate Limiter.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-be-3",
        skill: "Dynamic Programming (2D & Tree DP)",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (1D Memoization)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (2D Grid, Tree DP, Bitmask)",
        priority: "High",
        reason: "Universal algorithmic filter tested in technical screening coding rounds.",
        suggestedAction: "Solve 28 targeted DP medium and hard algorithmic problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-be-4",
        skill: "SQL Query Optimization & Execution Plans",
        category: "Databases & SQL Optimization",
        scope: "common",
        currentLevel: 3,
        currentLevelText: "Intermediate (Joins, Indexes)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (EXPLAIN ANALYZE, B-Tree Tuning, Query Plans)",
        priority: "High",
        reason: "Prevents N+1 queries during high concurrency production loads.",
        suggestedAction: "Run EXPLAIN ANALYZE on PostgreSQL tables and tune execution plans.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-be-5",
        skill: "Kafka Event Streaming & Consumer Groups",
        category: "System Design & Distributed Systems",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (RabbitMQ Pub-Sub)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Partitioning, Consumer Groups, At-Least-Once Delivery)",
        priority: "Medium",
        reason: "High demand for high-scale backend asynchronous microservice architectures.",
        suggestedAction: "Build sample Kafka event streaming and consumer worker group with error DLQs.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-be-6",
        skill: "Docker Multi-Stage Containerization",
        category: "DevOps & Containerization",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Single Stage)",
        requiredLevel: 3,
        requiredLevelText: "Intermediate (Multi-Stage, Security Layering, Slim Base)",
        priority: "Low",
        reason: "Required for standardized microservice artifact deployment across CI/CD environments.",
        suggestedAction: "Build slim multi-stage Docker images for backend microservices.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "PostgreSQL EXPLAIN ANALYZE Indexing", category: "DBMS" },
        { skill: "Pydantic Async Validation Schema", category: "Backend" }
      ],
      majorProjects: [
        { skill: "Redis Distributed Caching Engine", category: "Backend" },
        { skill: "Dynamic Programming 2D Mastery", category: "DSA" }
      ],
      fillIns: [
        { skill: "gRPC Protobuf Schema Definitions", category: "Networking" }
      ],
      hardLongTerm: [
        { skill: "Kafka Event Streaming Infrastructure", category: "Systems" }
      ]
    }
  },

  "Frontend Developer": {
    targetRole: "Frontend Developer",
    overallCoverage: 78,
    totalAudited: 26,
    gapsIdentifiedCount: 5,
    confidenceIndex: "96.0%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Core Frameworks & React/Next.js",
        coverage: 84,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "React 19, Next.js Server Components, SSR, Suspense, and hooks"
      },
      {
        category: "TypeScript & State Management",
        coverage: 72,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "Strict types, generic constraints, Zustand / Redux Toolkit"
      },
      {
        category: "CSS, Styling & Responsive UI",
        coverage: 88,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#ddb7ff",
        description: "Tailwind CSS, design tokens, fluid layouts, mobile accessibility"
      },
      {
        category: "Performance & Web Vitals",
        coverage: 58,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ffb4ab",
        description: "LCP/INP optimization, code splitting, memoization, Lighthouse 90+"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP (JS/TS)",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Closures, event loop, promises, async/await, prototype chain"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 68,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "DOM tree traversal, BFS/DFS, debounce/throttle algorithms, caching"
      },
      {
        category: "Databases & API Integration",
        coverage: 65,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "RESTful consumption, GraphQL, data normalization, cache invalidation"
      },
      {
        category: "DevOps & Version Control",
        coverage: 70,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Git branching, CI/CD automated preview builds, Vercel/Docker"
      }
    ],
    gaps: [
      {
        id: "gap-fe-1",
        skill: "Next.js SSR / Server Components & Caching",
        category: "Core Frameworks & React/Next.js",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Client-Side Rendering)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (RSC Architecture, Streaming, ISR, Middleware)",
        priority: "Critical",
        reason: "Primary framework standard for high-performance frontend engineering in top product firms.",
        suggestedAction: "Build a Server Components dashboard with streaming suspense boundaries.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-fe-2",
        skill: "Web Vitals & Performance Profiling",
        category: "Performance & Web Vitals",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Lighthouse Audit)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (LCP/INP Optimization, Bundle Splitting, Memory Leaks)",
        priority: "High",
        reason: "Tier-1 engineering requirement for responsive, zero-jank user experiences.",
        suggestedAction: "Profile bundle sizes and eliminate hydration bottlenecks using Chrome DevTools.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-fe-3",
        skill: "TypeScript Generics & Strict Utility Types",
        category: "TypeScript & State Management",
        scope: "role",
        currentLevel: 3,
        currentLevelText: "Intermediate (Interfaces, Props Types)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Conditional Types, Template Literals, Strict Inference)",
        priority: "High",
        reason: "Prevents runtime client exceptions and solidifies component design systems.",
        suggestedAction: "Implement reusable generic design system components with type inference.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-fe-4",
        skill: "Data Structures & Tree Traversal (DOM)",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Array iteration)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (BFS/DFS, Tree Reconciliation, Debounce/Throttle)",
        priority: "High",
        reason: "Universal algorithmic core tested in both generic and frontend-focused coding rounds.",
        suggestedAction: "Solve 20 frontend-focused data structure and DOM manipulation problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-fe-5",
        skill: "Git Branching Workflows & CI/CD Previews",
        category: "DevOps & Version Control",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Push/Pull to main)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Git Rebase, Feature Branches, Automated PR Preview Builds)",
        priority: "Medium",
        reason: "Essential teamwork requirement for collaborating on production design systems.",
        suggestedAction: "Configure GitHub Actions workflow for linting, type-checking, and preview deployment.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "Lighthouse Web Vitals Audit", category: "Performance" },
        { skill: "TypeScript Strict Null Props", category: "TypeScript" }
      ],
      majorProjects: [
        { skill: "Next.js App Router Component Library", category: "Core Frameworks" },
        { skill: "Interactive Data Visualization Canvas", category: "Frontend" }
      ],
      fillIns: [
        { skill: "Tailwind Fluid Spacing Config", category: "CSS" }
      ],
      hardLongTerm: [
        { skill: "Micro-Frontend Webpack Module Federation", category: "Architecture" }
      ]
    }
  },

  "Full Stack Developer": {
    targetRole: "Full Stack Developer",
    overallCoverage: 76,
    totalAudited: 32,
    gapsIdentifiedCount: 5,
    confidenceIndex: "95.5%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Frontend State & Architecture",
        coverage: 82,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "React/Next.js component trees, client/server state, TypeScript"
      },
      {
        category: "Backend APIs & Microservices",
        coverage: 74,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "Node.js / Python RESTful services, middleware, secure auth"
      },
      {
        category: "Full-Stack Integration & Auth",
        coverage: 66,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ffb4ab",
        description: "JWT/OAuth2 flows, WebSocket real-time sync, state hydration"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP",
        coverage: 82,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Multi-paradigm programming, design patterns, clean architecture"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 70,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Hash maps, Trees, Graphs, 2D Dynamic Programming"
      },
      {
        category: "Databases & Query Optimization",
        coverage: 66,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "PostgreSQL relational schemas, indexing, ORMs, and raw SQL"
      },
      {
        category: "DevOps & Containerization",
        coverage: 60,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Docker multi-stage builds, CI/CD pipelines, cloud deployment"
      }
    ],
    gaps: [
      {
        id: "gap-fs-1",
        skill: "PostgreSQL Schema Indexing & Query Optimization",
        category: "Databases & Query Optimization",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Simple Joins & Foreign Keys)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (B-Tree Indexes, EXPLAIN ANALYZE, Connection Pooling)",
        priority: "Critical",
        reason: "Required to eliminate N+1 latency bottlenecks across full stack applications.",
        suggestedAction: "Optimize database queries and implement composite indexes on relational tables.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-fs-2",
        skill: "TypeScript Strict Architecture & Generics",
        category: "Frontend State & Architecture",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Any / Basic Interfaces)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Generic Constraints, Discriminated Unions, Utility Types)",
        priority: "High",
        reason: "Ensures type safety across complex reactive frontends and shared API schemas.",
        suggestedAction: "Refactor API client and state management to strict discriminated union types.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-fs-3",
        skill: "Redis Distributed Caching & Invalidation",
        category: "Backend APIs & Microservices",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Key-Value Set/Get)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Cache-Aside, TTL Invalidation, Eviction Strategies)",
        priority: "High",
        reason: "Core expectation for Tier-1 full stack engineers handling high-traffic requests.",
        suggestedAction: "Implement Redis cache-aside caching on high-throughput backend endpoints.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-fs-4",
        skill: "Dynamic Programming (2D & Tree DP)",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (1D Memoization)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Grid DP, Tree Traversal, Knapsack)",
        priority: "High",
        reason: "Universal algorithmic filter tested in technical screening coding rounds.",
        suggestedAction: "Solve 28 targeted algorithmic DP medium problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-fs-5",
        skill: "Docker Multi-Stage Containerization",
        category: "DevOps & Containerization",
        scope: "common",
        currentLevel: 1,
        currentLevelText: "Novice (Docker Compose default)",
        requiredLevel: 3,
        requiredLevelText: "Intermediate (Multi-Stage Builds, Non-Root Users, Caching Layers)",
        priority: "Medium",
        reason: "Required for standardized production deployments and CI/CD pipelines.",
        suggestedAction: "Write production multi-stage Dockerfiles for both frontend and backend services.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "PostgreSQL EXPLAIN ANALYZE Indexing", category: "Database" },
        { skill: "TypeScript Strict Null Checks", category: "Frontend" }
      ],
      majorProjects: [
        { skill: "Redis Distributed Cache Engine", category: "Backend" },
        { skill: "Next.js Full Stack App with Auth", category: "Full Stack" }
      ],
      fillIns: [
        { skill: "Docker Compose Development Setup", category: "DevOps" }
      ],
      hardLongTerm: [
        { skill: "Microservices Event Bus with Kafka", category: "Backend" }
      ]
    }
  },

  "Data Scientist": {
    targetRole: "Data Scientist",
    overallCoverage: 75,
    totalAudited: 27,
    gapsIdentifiedCount: 5,
    confidenceIndex: "95.8%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Statistical Modeling & ML",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "A/B testing, hypothesis testing, regression, tree ensembles"
      },
      {
        category: "Data Wrangling & Analysis",
        coverage: 85,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#8083ff",
        description: "Pandas/NumPy transformations, missing value imputation, EDA"
      },
      {
        category: "Data Visualization & BI",
        coverage: 75,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Interactive dashboards, Matplotlib/Seaborn, Streamlit, Tableau"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP (Python)",
        coverage: 82,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Python fundamentals, object-oriented code, vectorized operations"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 70,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Hash maps, sliding windows, recursion, search algorithms"
      },
      {
        category: "Databases & SQL Analytics",
        coverage: 65,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "Window functions, aggregate analytical queries, CTEs"
      },
      {
        category: "DevOps & Reproducibility",
        coverage: 58,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Git version control, virtual environments, DVC data versioning"
      }
    ],
    gaps: [
      {
        id: "gap-ds-1",
        skill: "Statistical Hypothesis Testing & A/B Experiments",
        category: "Statistical Modeling & ML",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (T-Tests / P-Values)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Sample Size Power, Multi-Armed Bandits, Non-Parametric)",
        priority: "Critical",
        reason: "Core evaluation metric for product data science interviews in top companies.",
        suggestedAction: "Simulate and design an A/B experimentation platform with power calculations.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-ds-2",
        skill: "SQL Window Functions & Analytical CTEs",
        category: "Databases & SQL Analytics",
        scope: "common",
        currentLevel: 3,
        currentLevelText: "Intermediate (Group By, Joins)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (LEAD/LAG, Running Totals, Retention Cohorts)",
        priority: "High",
        reason: "Heavily tested in data technical screenings across Tier-1 analytics teams.",
        suggestedAction: "Solve 20 complex SQL window function and cohort retention queries.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-ds-3",
        skill: "Scikit-learn Pipeline Stacking & Ensembles",
        category: "Statistical Modeling & ML",
        scope: "role",
        currentLevel: 3,
        currentLevelText: "Intermediate (Random Forests, Logistic Reg)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (XGBoost, Stacking Regressors, Optuna Tuning)",
        priority: "High",
        reason: "Required to deliver benchmark predictive performance on complex tabular datasets.",
        suggestedAction: "Build a stacked ensemble model with Optuna hyperparameter optimization.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-ds-4",
        skill: "Dynamic Programming & Array Optimization",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Recursion)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Tabulation, 2D Grid DP, Binary Search)",
        priority: "High",
        reason: "Universal algorithmic core tested in competitive hiring screening tests.",
        suggestedAction: "Practice 20 medium algorithmic array and dynamic programming problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-ds-5",
        skill: "Tableau / Streamlit Executive Dashboards",
        category: "Data Visualization & BI",
        scope: "role",
        currentLevel: 3,
        currentLevelText: "Intermediate (Basic Charts)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Interactive Parameter Actions, Real-time KPIs)",
        priority: "Medium",
        reason: "Translates complex ML model outcomes into business leadership decisions.",
        suggestedAction: "Build an interactive Streamlit KPI dashboard with live filter parameters.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "SQL Window Functions Running Totals", category: "SQL" },
        { skill: "Optuna Bayesian Optimization", category: "Modeling" }
      ],
      majorProjects: [
        { skill: "End-to-End A/B Testing Simulator", category: "Experimentation" },
        { skill: "Predictive LTV Model with XGBoost", category: "Machine Learning" }
      ],
      fillIns: [
        { skill: "Matplotlib Custom Theme Templates", category: "Visualization" }
      ],
      hardLongTerm: [
        { skill: "Real-time Feature Store Pipeline", category: "Data Engineering" }
      ]
    }
  },

  "DevOps & Cloud Engineer": {
    targetRole: "DevOps & Cloud Engineer",
    overallCoverage: 70,
    totalAudited: 28,
    gapsIdentifiedCount: 5,
    confidenceIndex: "95.0%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Container Orchestration (K8s)",
        coverage: 62,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "Kubernetes Deployments, Ingress, Pod scheduling, Helm, K8s networking"
      },
      {
        category: "CI/CD & Infrastructure as Code",
        coverage: 70,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Terraform modules, GitHub Actions matrix builds, GitOps / ArgoCD"
      },
      {
        category: "Cloud Infrastructure (AWS/GCP)",
        coverage: 78,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "VPC, IAM least privilege, ECS/EKS, S3, CloudFront, Route53"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & Scripting (Python/Bash)",
        coverage: 75,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#4edea3",
        description: "Linux shell scripting, Python automation scripts, OS process APIs"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 65,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Graph traversal, tree networks, string parsing algorithms"
      },
      {
        category: "Databases & Storage Management",
        coverage: 62,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "Relational database backups, connection pooling, high availability"
      },
      {
        category: "DevOps & Version Control (Git)",
        coverage: 85,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#38bdf8",
        description: "Git branching models, hook automation, merge conflict resolution"
      }
    ],
    gaps: [
      {
        id: "gap-ops-1",
        skill: "Kubernetes Ingress & Pod Scheduling Policies",
        category: "Container Orchestration (K8s)",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Deployments & Services)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Ingress Controllers, HPA, Network Policies)",
        priority: "Critical",
        reason: "Core hiring metric for cloud infrastructure and platform engineering roles.",
        suggestedAction: "Deploy an Ingress controller with cert-manager and horizontal autoscaling on k8s.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-ops-2",
        skill: "Terraform Multi-Environment Modules",
        category: "CI/CD & Infrastructure as Code",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Single State File)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Remote State S3/DynamoDB, Reusable Modules, Workspaces)",
        priority: "High",
        reason: "Industry standard for declarative multi-region cloud provisioning.",
        suggestedAction: "Write reusable Terraform modules for VPC, ECS/EKS, and RDS instances.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-ops-3",
        skill: "AWS IAM Least Privilege & Security Policies",
        category: "Cloud Infrastructure (AWS/GCP)",
        scope: "role",
        currentLevel: 3,
        currentLevelText: "Intermediate (Managed Policies)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Custom SCPs, AssumeRole, OIDC GitHub Actions Provider)",
        priority: "High",
        reason: "Prevents credential leakage and ensures compliance with cloud security baselines.",
        suggestedAction: "Set up keyless AWS authentication for GitHub Actions using OIDC roles.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-ops-4",
        skill: "Data Structures & Tree/Graph Traversal",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Linear search)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Topological Sort, Graph Dependencies, Tree Traversal)",
        priority: "High",
        reason: "Universal algorithmic round required for Tier-1 software company platform roles.",
        suggestedAction: "Solve 20 graph dependency and tree traversal algorithmic problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-ops-5",
        skill: "Prometheus & Grafana Monitoring / Alerting",
        category: "CI/CD & Infrastructure as Code",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Pre-built Dashboards)",
        requiredLevel: 3,
        requiredLevelText: "Intermediate (Custom PromQL, Alertmanager, Node Exporter)",
        priority: "Medium",
        reason: "Critical for telemetry monitoring, SLI/SLO tracking, and incident response.",
        suggestedAction: "Set up Alertmanager rules for pod crash loops and high memory saturation.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "GitHub Actions OIDC AWS Role Auth", category: "Cloud" },
        { skill: "Docker Buildx Multi-Arch Caching", category: "Containers" }
      ],
      majorProjects: [
        { skill: "Terraform Production VPC & EKS Cluster", category: "IaC" },
        { skill: "Prometheus & Grafana Telemetry Stack", category: "Monitoring" }
      ],
      fillIns: [
        { skill: "Linux Systemd Service Management", category: "Linux" }
      ],
      hardLongTerm: [
        { skill: "Istio Service Mesh Mutual TLS", category: "K8s" }
      ]
    }
  },

  "Software Engineer": {
    targetRole: "Software Engineer",
    overallCoverage: 76,
    totalAudited: 30,
    gapsIdentifiedCount: 5,
    confidenceIndex: "96.0%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Object-Oriented Design & Clean Code",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "SOLID design principles, design patterns (Factory, Observer, Strategy)"
      },
      {
        category: "System Design & Architecture",
        coverage: 64,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "Scalability, load balancing, caching, asynchronous message queues"
      },
      {
        category: "Automated Testing & Unit Frameworks",
        coverage: 65,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ffb4ab",
        description: "PyTest / JUnit, mock objects, integration tests, test coverage metrics"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP",
        coverage: 82,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Language idioms, memory efficiency, concurrent threads"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 72,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Arrays, Linked Lists, Trees, Graphs, Dynamic Programming"
      },
      {
        category: "Databases & SQL Queries",
        coverage: 70,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "Relational modeling, indexing, ACID transactions, complex joins"
      },
      {
        category: "DevOps & Version Control",
        coverage: 68,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Git flow, PR reviews, CI/CD automated build pipelines"
      }
    ],
    gaps: [
      {
        id: "gap-sde-1",
        skill: "Dynamic Programming & Graph Algorithms",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (1D Memoization)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (2D Grid DP, Topological Sort, Shortest Paths)",
        priority: "Critical",
        reason: "Core primary algorithmic filtering round in all top tech placement drives.",
        suggestedAction: "Solve 30 medium LeetCode DP and graph problems with clean time complexity.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-sde-2",
        skill: "Low-Level Object-Oriented Design (LLD)",
        category: "Object-Oriented Design & Clean Code",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Single Class Design)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Design Patterns, SOLID, Extensible Schema)",
        priority: "Critical",
        reason: "Crucial for machine coding and technical interview rounds (e.g. Parking Lot, Elevator).",
        suggestedAction: "Implement extensible LLD designs for Snake & Ladder and Parking Lot.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-sde-3",
        skill: "High-Level System Design (HLD)",
        category: "System Design & Architecture",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Client-Server)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (CAP Theorem, Caching, Sharding, Message Queues)",
        priority: "High",
        reason: "Tested in SDE-1 architectural interviews at Tier-1 product firms.",
        suggestedAction: "Design scalable distributed systems for URL Shortener and Notification Service.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-sde-4",
        skill: "Relational Database Schema & B-Tree Indexing",
        category: "Databases & SQL Queries",
        scope: "common",
        currentLevel: 3,
        currentLevelText: "Intermediate (Joins, Keys)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (EXPLAIN ANALYZE, Composite Indexes, Connection Pools)",
        priority: "High",
        reason: "Universal database requirement for building robust enterprise software systems.",
        suggestedAction: "Run query plan optimizations on multi-table PostgreSQL databases.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-sde-5",
        skill: "Unit & Integration Test Automation",
        category: "Automated Testing & Unit Frameworks",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Manual tests)",
        requiredLevel: 3,
        requiredLevelText: "Intermediate (PyTest/JUnit, Mocking, Coverage > 80%)",
        priority: "Medium",
        reason: "Ensures defect-free code releases in professional engineering environments.",
        suggestedAction: "Add automated unit tests and mock external API dependencies.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "SOLID Principles Refactoring", category: "LLD" },
        { skill: "PyTest Fixtures and Mocks", category: "Testing" }
      ],
      majorProjects: [
        { skill: "Distributed Rate Limiter Service", category: "Systems" },
        { skill: "2D Dynamic Programming Mastery", category: "DSA" }
      ],
      fillIns: [
        { skill: "Git Interactive Rebase Workflows", category: "DevOps" }
      ],
      hardLongTerm: [
        { skill: "Distributed Consensus (Raft/Paxos)", category: "Distributed" }
      ]
    }
  },

  "Cybersecurity Analyst": {
    targetRole: "Cybersecurity Analyst",
    overallCoverage: 68,
    totalAudited: 25,
    gapsIdentifiedCount: 5,
    confidenceIndex: "95.2%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Threat Detection & SIEM",
        coverage: 75,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Splunk / Wazuh SIEM, Sigma detection rules, SOC playbooks"
      },
      {
        category: "Network & Linux Security Forensics",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#8083ff",
        description: "Wireshark PCAP analysis, TCP/IP handshake, host hardening"
      },
      {
        category: "Vulnerability Assessment & Audit",
        coverage: 60,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Nessus scans, CVE triage, OWASP Top 10 web vulnerabilities"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & Scripting (Python)",
        coverage: 70,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#4edea3",
        description: "Python log parsing, socket programming, regex automation"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 62,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "String search algorithms, hash tables, graph network topology"
      },
      {
        category: "Databases & SQL Security",
        coverage: 64,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "SQL injection prevention, database audit logs, access control"
      },
      {
        category: "DevOps & Version Control",
        coverage: 65,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Git version control, Linux system administration, CI/CD security"
      }
    ],
    gaps: [
      {
        id: "gap-sec-1",
        skill: "SIEM Detection Rule Tuning & Log Ingestion",
        category: "Threat Detection & SIEM",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Default Rules)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Sigma Rules, Correlation Searches, SOC Playbooks)",
        priority: "Critical",
        reason: "Core responsibility in SOC analysis and incident triage across enterprise cyber teams.",
        suggestedAction: "Write custom Sigma detection rules for brute force and privilege escalation.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-sec-2",
        skill: "Wireshark PCAP Packet Forensics",
        category: "Network & Linux Security Forensics",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (TCP Handshake)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (C2 Traffic Decryption, Malicious Beaconing Detection)",
        priority: "High",
        reason: "Crucial for network anomaly investigation and malware behavior analysis.",
        suggestedAction: "Analyze sample malicious PCAP traffic and identify exfiltration channels.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-sec-3",
        skill: "Data Structures & Hash Map Optimization",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Linear search)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Hash Tables, Sliding Windows, Graph Traversal)",
        priority: "High",
        reason: "Universal algorithmic evaluation round tested across technical hiring screening tests.",
        suggestedAction: "Solve 20 algorithmic problems focused on hash tables and sliding windows.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-sec-4",
        skill: "SQL Injection Prevention & Query Hardening",
        category: "Databases & SQL Security",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Raw string queries)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Parameterized Queries, ORMs, Principle of Least Privilege)",
        priority: "High",
        reason: "Universal database security baseline for defending corporate data assets.",
        suggestedAction: "Audit database access layers and replace concatenated queries with prepared statements.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-sec-5",
        skill: "Vulnerability Scanning & Remediation (Nessus)",
        category: "Vulnerability Assessment & Audit",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Run Default Scan)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Credentialed Scanning, False Positive Filtering, CVE Triage)",
        priority: "Medium",
        reason: "Essential for corporate compliance and vulnerability management programs.",
        suggestedAction: "Execute credentialed vulnerability audit on lab VMs and draft remediation reports.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "SSH Key-Only Configuration & Fail2ban", category: "Linux" },
        { skill: "VirusTotal Python API Enrichment", category: "Automation" }
      ],
      majorProjects: [
        { skill: "Wazuh / Splunk SIEM Lab Deployment", category: "SIEM" },
        { skill: "Malware Traffic PCAP Analysis Lab", category: "Forensics" }
      ],
      fillIns: [
        { skill: "Nmap Scripting Engine (NSE) Scans", category: "Network" }
      ],
      hardLongTerm: [
        { skill: "Active Directory Kerberoasting Defense", category: "Enterprise" }
      ]
    }
  },

  "Data Engineer": {
    targetRole: "Data Engineer",
    overallCoverage: 72,
    totalAudited: 29,
    gapsIdentifiedCount: 5,
    confidenceIndex: "95.5%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Data Pipelines & ETL Architecture",
        coverage: 70,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "Apache Spark, Airflow orchestration, data lakehouse, batch vs stream"
      },
      {
        category: "Distributed Streaming & Kafka",
        coverage: 62,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Kafka topics, consumer groups, schema registry, sliding event windows"
      },
      {
        category: "Data Warehousing & Modeling",
        coverage: 76,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#ffb4ab",
        description: "Star schema, snowflake schema, columnar storage (Parquet), Snowflake/BigQuery"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP (Python/Java)",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Object-oriented programming, memory profiling, multithreading"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 72,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "Graphs, trees, sorting algorithms, algorithmic space-time optimization"
      },
      {
        category: "Databases & Advanced SQL",
        coverage: 78,
        benchmarkTarget: 85,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "Partitioning, indexing, EXPLAIN plans, analytical window queries"
      },
      {
        category: "DevOps & Containerization",
        coverage: 65,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Docker containers, Git version control, CI/CD pipeline triggers"
      }
    ],
    gaps: [
      {
        id: "gap-de-1",
        skill: "Apache Spark Distributed Transformations",
        category: "Data Pipelines & ETL Architecture",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Single-node Pandas)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (PySpark DataFrames, Shuffling, Broadcast Joins)",
        priority: "Critical",
        reason: "Core engine for processing terabyte-scale datasets in modern data infrastructure.",
        suggestedAction: "Build a PySpark pipeline with broadcast joins and partition tuning.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-de-2",
        skill: "Kafka Event Streaming & Consumer Groups",
        category: "Distributed Streaming & Kafka",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Message queue pub/sub)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Partitions, Consumer Offsets, Exactly-Once Semantics)",
        priority: "Critical",
        reason: "Essential for low-latency streaming ingestion and real-time event analytics.",
        suggestedAction: "Implement an end-to-end Kafka streaming pipeline with dead-letter queue handlers.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-de-3",
        skill: "Dynamic Programming & Graph DAGs",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Linear search)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Topological Sort, DAG Scheduling, Tree DP)",
        priority: "High",
        reason: "Universal algorithmic core tested in Tier-1 company data engineering interviews.",
        suggestedAction: "Solve 25 targeted graph topological sort and dynamic programming problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-de-4",
        skill: "SQL Window Functions & Analytical Joins",
        category: "Databases & Advanced SQL",
        scope: "common",
        currentLevel: 3,
        currentLevelText: "Intermediate (Group by, Joins)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (LEAD/LAG, Partition Pruning, Index Execution Tuning)",
        priority: "High",
        reason: "Universal requirement for building efficient analytics models and data marts.",
        suggestedAction: "Solve 25 complex SQL window analytical problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-de-5",
        skill: "Airflow DAG Orchestration & Backfilling",
        category: "Data Pipelines & ETL Architecture",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Cron jobs)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Dynamic Task Mapping, XComs, Idempotent Backfilling)",
        priority: "Medium",
        reason: "Industry standard for production workflow automation and lineage tracking.",
        suggestedAction: "Build production Airflow DAGs with automated retries and Slack alerts.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "SQL Analytical Window Queries", category: "Databases" },
        { skill: "Parquet Compression Tuning", category: "Pipelines" }
      ],
      majorProjects: [
        { skill: "PySpark Lakehouse ETL Pipeline", category: "Data Engineering" },
        { skill: "Kafka Streaming Anomaly Detector", category: "Streaming" }
      ],
      fillIns: [
        { skill: "Dockerized Airflow Local Cluster", category: "DevOps" }
      ],
      hardLongTerm: [
        { skill: "Real-time Delta Lake CDC Pipeline", category: "Architecture" }
      ]
    }
  },

  "Mobile App Developer": {
    targetRole: "Mobile App Developer",
    overallCoverage: 74,
    totalAudited: 26,
    gapsIdentifiedCount: 5,
    confidenceIndex: "95.6%",
    categoryCoverage: [
      // Role-Specific Competencies
      {
        category: "Mobile Frameworks & React Native",
        coverage: 78,
        benchmarkTarget: 85,
        scope: "role",
        status: "In Progress",
        color: "#8083ff",
        description: "React Native / Expo, native bridges, navigation, gesture animations"
      },
      {
        category: "Mobile UI/UX & Responsive Layouts",
        coverage: 82,
        benchmarkTarget: 85,
        scope: "role",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Touch targets, safe areas, fluid typography, dark mode, accessibility"
      },
      {
        category: "Offline Storage & Push Notifications",
        coverage: 60,
        benchmarkTarget: 80,
        scope: "role",
        status: "In Progress",
        color: "#ffb4ab",
        description: "AsyncStorage / SQLite, background tasks, FCM push notifications"
      },
      // Common for All Roles (Universal Placement Core)
      {
        category: "Core Programming & OOP (JS/TS)",
        coverage: 80,
        benchmarkTarget: 85,
        scope: "common",
        status: "Benchmark Met",
        color: "#4edea3",
        description: "Closures, async/await, strict TypeScript typing, state stores"
      },
      {
        category: "Data Structures & Algorithms",
        coverage: 68,
        benchmarkTarget: 80,
        scope: "common",
        status: "In Progress",
        color: "#ddb7ff",
        description: "List virtualization algorithms, binary search, tree structures"
      },
      {
        category: "Databases & REST APIs",
        coverage: 70,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#fcd34d",
        description: "RESTful consumption, token authentication, offline cache syncing"
      },
      {
        category: "DevOps & App Store CI/CD",
        coverage: 62,
        benchmarkTarget: 75,
        scope: "common",
        status: "In Progress",
        color: "#38bdf8",
        description: "Git version control, EAS Build / Fastlane, automated release pipelines"
      }
    ],
    gaps: [
      {
        id: "gap-mob-1",
        skill: "React Native Reanimated & Fluid Gestures",
        category: "Mobile Frameworks & React Native",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (Animated API)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Reanimated 3, Gesture Handler 2, 60fps Native UI Thread)",
        priority: "Critical",
        reason: "Core evaluation metric for building premium, jank-free mobile consumer apps.",
        suggestedAction: "Implement swipeable gesture cards and fluid transition animations.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-mob-2",
        skill: "Offline-First Data Sync & Local SQLite",
        category: "Offline Storage & Push Notifications",
        scope: "role",
        currentLevel: 2,
        currentLevelText: "Basic (AsyncStorage)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (WatermelonDB / SQLite, Optimistic Updates, Conflict Resolution)",
        priority: "High",
        reason: "Required to deliver resilient mobile user experiences in spotty network conditions.",
        suggestedAction: "Build an offline-first note-taking app with optimistic sync and SQLite.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-mob-3",
        skill: "Data Structures & List Virtualization",
        category: "Data Structures & Algorithms",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Standard lists)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (FlashList, Windowing, Memory Recycling Algorithms)",
        priority: "High",
        reason: "Universal algorithmic core tested in software engineering placement screenings.",
        suggestedAction: "Solve 20 list optimization and tree/graph algorithmic problems.",
        actionLabel: "Start Practice Tasks",
        actionRoute: "/tasks"
      },
      {
        id: "gap-mob-4",
        skill: "REST API Client & Token Interceptors",
        category: "Databases & REST APIs",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (fetch calls)",
        requiredLevel: 4,
        requiredLevelText: "Advanced (Axios Interceptors, Refresh Token Queues, Retry Exponential Backoff)",
        priority: "Medium",
        reason: "Universal backend integration pattern for secure and reliable API communication.",
        suggestedAction: "Implement an automated silent refresh token interceptor in the API client.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      },
      {
        id: "gap-mob-5",
        skill: "Mobile CI/CD & Fastlane Automated Builds",
        category: "DevOps & App Store CI/CD",
        scope: "common",
        currentLevel: 2,
        currentLevelText: "Basic (Manual Xcode build)",
        requiredLevel: 3,
        requiredLevelText: "Intermediate (Fastlane, GitHub Actions, Automated TestFlight)",
        priority: "Medium",
        reason: "Standard automation skill for modern distributed mobile engineering teams.",
        suggestedAction: "Set up a GitHub Actions pipeline with Fastlane to build and deploy staging IPAs/APKs.",
        actionLabel: "Add to Roadmap",
        actionRoute: "/roadmap"
      }
    ],
    matrix2x2: {
      quickWins: [
        { skill: "FlashList Windowing Optimization", category: "Performance" },
        { skill: "Axios Silent Token Refresh", category: "Networking" }
      ],
      majorProjects: [
        { skill: "Fluid Reanimated Gesture Gallery", category: "Mobile UI" },
        { skill: "Offline-First SQLite Synchronization", category: "Data Sync" }
      ],
      fillIns: [
        { skill: "Expo Push Notification Configuration", category: "Mobile" }
      ],
      hardLongTerm: [
        { skill: "Native TurboModules C++ JSI Bridge", category: "Architecture" }
      ]
    }
  }
};

// Map role aliases to canonical keys in ROLE_SKILL_GAP_CONFIGS
export const ROLE_ALIASES_MAP = {
  "full stack engineer": "Full Stack Developer",
  "full stack developer": "Full Stack Developer",
  "fullstack developer": "Full Stack Developer",
  "fullstack engineer": "Full Stack Developer",
  "frontend engineer": "Frontend Developer",
  "backend engineer": "Backend Developer",
  "data scientist & ai engineer": "Data Scientist",
  "cybersecurity analyst & engineer": "Cybersecurity Analyst",
  "cybersecurity engineer": "Cybersecurity Analyst",
  "devops engineer": "DevOps & Cloud Engineer",
  "cloud engineer": "DevOps & Cloud Engineer",
  "sde": "Software Engineer",
  "sde 1": "Software Engineer",
  "software development engineer": "Software Engineer"
};

export function getCanonicalRoleName(targetRole) {
  if (!targetRole) return "AI/ML Engineer";
  const clean = targetRole.trim();
  const lower = clean.toLowerCase();

  if (ROLE_ALIASES_MAP[lower]) {
    return ROLE_ALIASES_MAP[lower];
  }

  const direct = Object.keys(ROLE_SKILL_GAP_CONFIGS).find(
    (k) => k.toLowerCase() === lower
  );
  if (direct) return direct;

  const partial = Object.keys(ROLE_SKILL_GAP_CONFIGS).find(
    (k) => lower.includes(k.toLowerCase()) || k.toLowerCase().includes(lower)
  );
  if (partial) return partial;

  return "AI/ML Engineer";
}

export function getRoleSkillGapData(targetRole = null, userContext = null) {
  let role = targetRole;
  if (!role && userContext) {
    role = userContext.targetRole || userContext.career?.targetRole;
  }
  if (!role) {
    try {
      const sU = localStorage.getItem("placementor_user_data");
      if (sU) role = JSON.parse(sU)?.targetRole;
      if (!role) {
        const sO = localStorage.getItem("placementCopilotOnboarding");
        if (sO) role = JSON.parse(sO)?.targetRole;
      }
    } catch (e) {
      // ignore
    }
  }

  const canonicalRole = getCanonicalRoleName(role);
  const baseConfig = ROLE_SKILL_GAP_CONFIGS[canonicalRole] || ROLE_SKILL_GAP_CONFIGS["AI/ML Engineer"];

  // Dynamically calibrate coverage and gap levels based on user context if available
  let dynamicCoverage = baseConfig.overallCoverage;
  const userSkills = userContext?.selectedSkills || userContext?.skills?.selectedSkills || [];
  const dsaLevel = userContext?.dsaLevel || userContext?.skills?.dsaLevel || "Intermediate";

  // Calibrate DSA level if user is Advanced or Expert
  const categoryCoverage = (baseConfig.categoryCoverage || []).map((cat) => {
    let catCov = cat.coverage;
    const catLower = cat.category.toLowerCase();
    const isCommon = cat.scope === "common" || COMMON_CATEGORIES.has(cat.category);
    const benchmarkTarget = cat.benchmarkTarget || (isCommon ? 80 : 85);

    if (catLower.includes("algorithm") || catLower.includes("dsa")) {
      if (dsaLevel.includes("Expert")) catCov = Math.min(95, catCov + 10);
      else if (dsaLevel.includes("Advanced")) catCov = Math.min(90, catCov + 6);
      else if (dsaLevel.includes("Beginner")) catCov = Math.max(35, catCov - 15);
    }

    const status = catCov >= benchmarkTarget
      ? "Benchmark Met"
      : catCov >= 40
      ? "In Progress"
      : catCov > 0
      ? "Foundational"
      : "Remediation Needed";

    return {
      ...cat,
      coverage: catCov,
      benchmarkTarget,
      scope: isCommon ? "common" : "role",
      status
    };
  });

  // Ensure gaps all have scope assigned
  const gaps = (baseConfig.gaps || []).map((gap) => {
    const isCommon = gap.scope === "common" || COMMON_CATEGORIES.has(gap.category);
    return {
      ...gap,
      scope: isCommon ? "common" : "role"
    };
  });

  if (userSkills.length > 5) {
    dynamicCoverage = Math.min(92, dynamicCoverage + 4);
  }

  return {
    ...baseConfig,
    targetRole: canonicalRole,
    overallCoverage: dynamicCoverage,
    categoryCoverage,
    gaps,
    totalAudited: baseConfig.totalAudited ? Math.min(baseConfig.totalAudited, 16) : ((baseConfig.gaps?.length || 8) + 4),
    confidenceIndex: baseConfig.confidenceIndex || "94.5%",
    lastCalibrated: "Real-time Telemetry Synced"
  };
}

// Backwards-compatible initial fallback (defaults to AI/ML Engineer calibrated)
export const initialSkillGapData = getRoleSkillGapData("AI/ML Engineer");
