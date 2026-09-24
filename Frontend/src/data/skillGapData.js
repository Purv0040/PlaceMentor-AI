// Centralized mock data for AI Skill Gap Analyzer (12.html)

export const initialSkillGapData = {
  overallCoverage: 72,
  totalAudited: 32,
  gapsIdentifiedCount: 6,
  lastCalibrated: "Today, 11:05 PM (Automated)",
  confidenceIndex: "95.4%",

  categoryCoverage: [
    { category: "Data Structures & Algorithms", coverage: 85, color: "#4edea3" },
    { category: "Backend Microservices", coverage: 78, color: "#8083ff" },
    { category: "System Design & Architecture", coverage: 62, color: "#ddb7ff" },
    { category: "Cloud & DevOps (Docker/K8s)", coverage: 54, color: "#ffb4ab" },
  ],

  gaps: [
    {
      id: "gap-1",
      skill: "Redis Distributed Caching",
      category: "Backend / Architecture",
      currentLevel: 2, // 1-5 scale (1: Novice, 2: Basic, 3: Intermediate, 4: Advanced, 5: Expert)
      currentLevelText: "Basic (Key-Value)",
      requiredLevel: 4,
      requiredLevelText: "Advanced (Eviction Policies, Cluster Sync)",
      priority: "Critical",
      reason: "Required for Tier-1 Backend SDE-1 high throughput endpoints.",
      suggestedAction: "Implement Redis Caching in PlaceMentor AI backend.",
      actionLabel: "Add to Roadmap",
      actionRoute: "/roadmap"
    },
    {
      id: "gap-2",
      skill: "Dynamic Programming (2D & Tree DP)",
      category: "DSA & Algorithms",
      currentLevel: 2,
      currentLevelText: "Basic (1D Memoization)",
      requiredLevel: 4,
      requiredLevelText: "Advanced (2D Grid, Tree DP, Bitmask)",
      priority: "High",
      reason: "Appears in 40% of MAANG / Unicorn coding screening rounds.",
      suggestedAction: "Solve 28 targeted DP medium problems.",
      actionLabel: "Start Practice Tasks",
      actionRoute: "/tasks"
    },
    {
      id: "gap-3",
      skill: "Kubernetes Container Orchestration",
      category: "Cloud & DevOps",
      currentLevel: 1,
      currentLevelText: "Novice (Docker Compose only)",
      requiredLevel: 3,
      requiredLevelText: "Intermediate (Pods, Deployments, Ingress)",
      priority: "High",
      reason: "Preferred Tier-1 DevOps evidence for backend microservices.",
      suggestedAction: "Deploy microservice-event-bus on Minikube.",
      actionLabel: "Add to Roadmap",
      actionRoute: "/roadmap"
    },
    {
      id: "gap-4",
      skill: "Kafka / Event Streaming",
      category: "Backend / Systems",
      currentLevel: 2,
      currentLevelText: "Basic (RabbitMQ Pub-Sub)",
      requiredLevel: 4,
      requiredLevelText: "Advanced (Partitioning, Consumer Groups)",
      priority: "Medium",
      reason: "High demand for high-scale backend engineering teams.",
      suggestedAction: "Build sample Kafka log streaming service.",
      actionLabel: "View Projects",
      actionRoute: "/projects"
    },
    {
      id: "gap-5",
      skill: "SQL Database Query Optimization",
      category: "CS Fundamentals / DBMS",
      currentLevel: 3,
      currentLevelText: "Intermediate (Indexes, Joins)",
      requiredLevel: 4,
      requiredLevelText: "Advanced (EXPLAIN ANALYZE, B-Tree Tuning)",
      priority: "Medium",
      reason: "Prevents N+1 queries during System Design interviews.",
      suggestedAction: "Run EXPLAIN ANALYZE on PostgreSQL tables.",
      actionLabel: "Add to Roadmap",
      actionRoute: "/roadmap"
    },
    {
      id: "gap-6",
      skill: "System Design Trade-off Articulation",
      category: "Communication / Design",
      currentLevel: 3,
      currentLevelText: "Intermediate (Basic Diagram)",
      requiredLevel: 4,
      requiredLevelText: "Advanced (CAP Theorem, Latency SLAs)",
      priority: "Low",
      reason: "Important for senior interviewer architectural evaluation.",
      suggestedAction: "Practice mock System Design interview drill.",
      actionLabel: "Practice Mock",
      actionRoute: "/mock-interview"
    }
  ],

  matrix2x2: {
    quickWins: [ // High Impact, Low Effort
      { skill: "STAR Resume Bullets Quantification", category: "Resume" },
      { skill: "EXPLAIN ANALYZE Indexing", category: "DBMS" }
    ],
    majorProjects: [ // High Impact, High Effort
      { skill: "Redis Distributed Caching Engine", category: "Backend" },
      { skill: "Dynamic Programming 2D Mastery", category: "DSA" }
    ],
    fillIns: [ // Low Impact, Low Effort
      { skill: "gRPC Protobuf Schema Definitions", category: "Networking" }
    ],
    hardLongTerm: [ // Low Impact, High Effort
      { skill: "Kubernetes Cluster Ingress Controller", category: "DevOps" }
    ]
  }
};
