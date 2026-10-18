// Centralized mock data generator for Adaptive Roadmap across roles

export const getRoleRoadmapPhases = (targetRole = 'Full Stack Engineer', durationDays = 90) => {
  const norm = String(targetRole || '').toLowerCase();
  const d = Number(durationDays) || 90;
  const p1End = Math.max(1, Math.round(d * 0.33));
  const p2End = Math.max(p1End + 1, Math.round(d * 0.67));

  if (norm.includes('ai') || norm.includes('machine learning') || norm.includes('ml')) {
    return [
      {
        id: "phase-1",
        title: "Phase 1: ML Foundations, Math & Core Python",
        subtitle: "Linear Algebra, Statistics, NumPy/Pandas & Classic Algorithms",
        startDay: 1,
        endDay: p1End,
        durationDays: p1End,
        status: "in-progress",
        progressPercent: 30,
        milestones: [
          "Mastered Vector/Matrix Math & Gradient Descent Optimization",
          "Exploratory Data Analysis with Pandas, Seaborn & Scikit-Learn",
          "Implemented Supervised/Unsupervised Algorithms from Scratch",
        ],
      },
      {
        id: "phase-2",
        title: "Phase 2: Deep Learning, NLP & LLM Architecture",
        subtitle: "PyTorch, Transformers, RAG Pipelines & Fine-Tuning",
        startDay: p1End + 1,
        endDay: p2End,
        durationDays: p2End - p1End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Built Deep Neural Networks with PyTorch & Backprop",
          "Constructed RAG Retrieval Systems with Vector DBs (Pinecone/FAISS)",
          "Fine-tuned Open-Source LLMs (Llama 3/Mistral) with LoRA/QLoRA",
        ],
      },
      {
        id: "phase-3",
        title: "Phase 3: MLOps, Model Serving & Interview Mocks",
        subtitle: "FastAPI Inference, Docker, MLflow & System Design Mocks",
        startDay: p2End + 1,
        endDay: d,
        durationDays: d - p2End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Deployed Low-Latency Async APIs via Docker & Triton/FastAPI",
          "MLflow Experiment Tracking & Drift Detection Pipelines",
          "End-to-End ML System Design & Behavioral STAR Interview Polish",
        ],
      },
    ];
  }

  if (norm.includes('devops') || norm.includes('cloud') || norm.includes('aws') || norm.includes('sre')) {
    return [
      {
        id: "phase-1",
        title: "Phase 1: Linux, Networking & Containerization",
        subtitle: "Bash Scripting, VPC Routing, System Internals & Docker",
        startDay: 1,
        endDay: p1End,
        durationDays: p1End,
        status: "in-progress",
        progressPercent: 30,
        milestones: [
          "Linux Kernel, Process Monitoring, Systemd & Bash Automation",
          "TCP/IP, DNS, Subnetting & TLS/SSL Security Architecture",
          "Multi-stage Dockerfile Optimization & Minimal Distroless Containers",
        ],
      },
      {
        id: "phase-2",
        title: "Phase 2: Kubernetes, IaC & Cloud Platforms",
        subtitle: "AWS/GCP Core Services, Terraform Provisioning & Helm",
        startDay: p1End + 1,
        endDay: p2End,
        durationDays: p2End - p1End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Orchestrated Production K8s Deployments, StatefulSets & Ingress",
          "Automated Multi-Region Cloud Infra via Modular Terraform",
          "Configured Cloud IAM Policies & Zero-Trust Network Controls",
        ],
      },
      {
        id: "phase-3",
        title: "Phase 3: CI/CD, Observability & High Availability",
        subtitle: "GitHub Actions, Prometheus/Grafana, Chaos Drills & Mocks",
        startDay: p2End + 1,
        endDay: d,
        durationDays: d - p2End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Built Automated Canary / Blue-Green CI/CD Release Pipelines",
          "Set Up Prometheus, Alertmanager & Distributed Tracing",
          "Cloud Disaster Recovery, 99.99% SLA Architectures & SRE Mocks",
        ],
      },
    ];
  }

  if (norm.includes('cybersecurity') || norm.includes('security')) {
    return [
      {
        id: "phase-1",
        title: "Phase 1: Network Security, Linux Hardening & Cryptography",
        subtitle: "Wireshark Packet Analysis, OS Hardening, Hash/Ciphers",
        startDay: 1,
        endDay: p1End,
        durationDays: p1End,
        status: "in-progress",
        progressPercent: 30,
        milestones: [
          "Mastered Wireshark PCAP Packet Captures & Protocol Analysis",
          "Configured Linux IPTables, UFW, SSH Key Architecture & PAM",
          "Symmetric/Asymmetric Encryption, PKI & Digital Signatures",
        ],
      },
      {
        id: "phase-2",
        title: "Phase 2: Threat Detection, SIEM & SOC Operations",
        subtitle: "Splunk/Elastic, Log Ingestion, Incident Response & MITRE ATT&CK",
        startDay: p1End + 1,
        endDay: p2End,
        durationDays: p2End - p1End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Created Real-time Detection Correlation Queries in SIEM",
          "Mapped Adversary TTPs to the MITRE ATT&CK Framework",
          "Conducted Forensic Evidence Preservation & Incident Triage",
        ],
      },
      {
        id: "phase-3",
        title: "Phase 3: Web App PenTesting, Cloud Security & Audits",
        subtitle: "OWASP Top 10, Burp Suite, AWS IAM Audit & Security Mocks",
        startDay: p2End + 1,
        endDay: d,
        durationDays: d - p2End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Remediated Critical OWASP Vulnerabilities (SQLi, SSRF, IDOR)",
          "Conducted Cloud Security Posture Management & Zero-Trust Audits",
          "Security Architecture Defense Drills & Technical Interview Polish",
        ],
      },
    ];
  }

  if (norm.includes('data engineer')) {
    return [
      {
        id: "phase-1",
        title: "Phase 1: Advanced SQL, Data Modeling & Python for Data",
        subtitle: "Window Functions, Normalization, Star Schemas & Pandas",
        startDay: 1,
        endDay: p1End,
        durationDays: p1End,
        status: "in-progress",
        progressPercent: 30,
        milestones: [
          "Advanced CTEs, Window Aggregations & Query Execution Plan Tuning",
          "Designed Dimensional Star & Snowflake Warehousing Schemas",
          "Automated Robust Data Ingestion Scripts in Python",
        ],
      },
      {
        id: "phase-2",
        title: "Phase 2: Distributed Processing & Pipeline Orchestration",
        subtitle: "Apache Spark, PySpark, Airflow DAGs & Lakehouses",
        startDay: p1End + 1,
        endDay: p2End,
        durationDays: p2End - p1End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Engineered Distributed PySpark Transformations across Terabytes",
          "Built Resilient Airflow DAG Workflows with SLA Monitoring",
          "Configured Delta Lake / Iceberg ACID Table Storage",
        ],
      },
      {
        id: "phase-3",
        title: "Phase 3: Real-Time Streaming, Warehousing & Mocks",
        subtitle: "Kafka Streams, Snowflake/BigQuery Optimization & System Mocks",
        startDay: p2End + 1,
        endDay: d,
        durationDays: d - p2End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Implemented Kafka / Event-Hub Real-time Stream Consumers",
          "Snowflake/BigQuery Partitioning & Cost Optimization",
          "Distributed Data System Design Drills & Mock Interviews",
        ],
      },
    ];
  }

  if (norm.includes('frontend')) {
    return [
      {
        id: "phase-1",
        title: "Phase 1: Advanced JavaScript, TypeScript & DOM Systems",
        subtitle: "ES6+, Event Loops, Strict Types & Browser Rendering Engine",
        startDay: 1,
        endDay: p1End,
        durationDays: p1End,
        status: "in-progress",
        progressPercent: 30,
        milestones: [
          "Mastered Event Bubbling, Closures, Async/Await & Prototypal Chains",
          "Strict TypeScript Interfaces, Generics & Utility Types",
          "Built High-Performance Vanilla Components & Canvas Graphics",
        ],
      },
      {
        id: "phase-2",
        title: "Phase 2: Modern React Architecture & State Management",
        subtitle: "Hooks, Context, Server Components, Routing & Tailwind CSS",
        startDay: p1End + 1,
        endDay: p2End,
        durationDays: p2End - p1End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Architected Complex Custom Hooks & Global State (Zustand/Redux)",
          "Production SSR/SSG Implementation with Next.js App Router",
          "Pixel-Perfect Design Systems with Tailwind & Headless UI",
        ],
      },
      {
        id: "phase-3",
        title: "Phase 3: Core Web Vitals, Testing & Frontend System Design",
        subtitle: "LCP/FID/CLS Tuning, Jest/Cypress, Micro-Frontends & Mocks",
        startDay: p2End + 1,
        endDay: d,
        durationDays: d - p2End,
        status: "upcoming",
        progressPercent: 0,
        milestones: [
          "Achieved 95+ Lighthouse Score & Optimized Critical Rendering Path",
          "Automated Unit & E2E Testing with Vitest and Cypress",
          "Frontend System Design: Infinite Scroll, Virtualized Lists & Caching",
        ],
      },
    ];
  }

  // Default / Full Stack / Backend / Software Engineer
  return [
    {
      id: "phase-1",
      title: "Phase 1: Core Algorithms & CS Fundamentals",
      subtitle: "Arrays, Trees, Graphs, OOP & Relational SQL Foundations",
      startDay: 1,
      endDay: p1End,
      durationDays: p1End,
      status: "in-progress",
      progressPercent: 30,
      milestones: [
        "Mastered Binary Trees, Graph Traversals & Binary Search Patterns",
        "Completed 100+ LeetCode Medium Algorithmic Challenges",
        "Configured Database Normalization, Indexes & Transaction Isolation",
      ],
    },
    {
      id: "phase-2",
      title: "Phase 2: Microservices, Distributed Systems & Caching",
      subtitle: "REST/gRPC, Redis Caching, Event-Driven Messaging & APIs",
      startDay: p1End + 1,
      endDay: p2End,
      durationDays: p2End - p1End,
      status: "upcoming",
      progressPercent: 0,
      milestones: [
        "Built Scalable REST & Async APIs with Low Latency Benchmarks",
        "Integrated Redis Caching (Cache-Aside, Eviction Policies)",
        "Configured RabbitMQ / Kafka Pub-Sub Event Pipelines",
      ],
    },
    {
      id: "phase-3",
      title: "Phase 3: Tier-1 System Design & Placement Mocks",
      subtitle: "High-Level Architecture, Rate Limiters, STAR Polish & Mocks",
      startDay: p2End + 1,
      endDay: d,
      durationDays: d - p2End,
      status: "upcoming",
      progressPercent: 0,
      milestones: [
        "Designed Distributed Systems: URL Shortener, Chat & Rate Limiter",
        "Refactored Resume STAR Bullets with Quantified Technical Metrics",
        "Completed Live Technical Whiteboard & HR Behavioral Mocks",
      ],
    },
  ];
};

export const getDynamicRoadmap = (targetRole = 'Full Stack Engineer', totalDays = 90, dailyMinutes = 90) => {
  const d = Number(totalDays) || 90;
  const phases = getRoleRoadmapPhases(targetRole, d);

  return {
    id: `roadmap-${targetRole.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
    roadmapId: `roadmap-${targetRole.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
    title: `${d}-Day Adaptive Placement Roadmap`,
    targetRole,
    description: `Personalized ${d}-day preparation curriculum structured specifically for ${targetRole}.`,
    totalDays: d,
    currentDay: 1,
    currentPhaseId: "phase-1",
    availableMinutesPerDay: Number(dailyMinutes) || 90,
    overallProgressPercent: 0,
    lastAdapted: "Today, Just now (Role Dynamic)",
    activeSprintName: `Sprint 1: ${phases[0]?.title || 'Foundation'}`,
    phases,
  };
};

export const initialRoadmapData = getDynamicRoadmap('Full Stack Engineer', 90, 90);

