// Centralized mock data for GitHub Intelligence (8.html)

export const initialGithubData = {
  isConnected: true,
  handle: "Purv0040",
  profileUrl: "https://github.com/Purv0040",
  lastSynced: "Just now",
  
  metrics: {
    githubImpactScore: 82,
    scorePercentile: "Top 12% among Tier-1 candidates",
    totalCommits: 648,
    activeStreakDays: 42,
    longestStreakDays: 85,
    repoQualityIndex: 88,
    languageCount: 8,
    reposAnalyzedCount: 14,
  },

  languages: [
    { name: "TypeScript", percentage: 45, color: "#3178c6" },
    { name: "Python", percentage: 30, color: "#3572A5" },
    { name: "Go", percentage: 15, color: "#00ADD8" },
    { name: "Java", percentage: 10, color: "#b07219" },
  ],

  weeklyCadence: [
    { week: "W1", commits: 24, complexity: 78 },
    { week: "W2", commits: 38, complexity: 82 },
    { week: "W3", commits: 45, complexity: 85 },
    { week: "W4", commits: 30, complexity: 80 },
    { week: "W5", commits: 52, complexity: 90 },
  ],

  repositories: [
    {
      id: "repo1",
      name: "PlaceMentor-AI",
      description: "AI-driven placement prep copilot with AST code audit, resume intelligence, and adaptive roadmaps.",
      language: "TypeScript",
      stars: 42,
      forks: 12,
      astScore: 92,
      qualityTier: "Production Grade",
      tags: ["React", "FastAPI", "TailwindCSS", "Docker", "Recharts"],
      updatedAt: "2 days ago",
      complexity: "High (Modular Architecture)",
      isPrimary: true
    },
    {
      id: "repo2",
      name: "microservice-event-bus",
      description: "Distributed pub-sub event bus implemented in Go with RabbitMQ and gRPC endpoints.",
      language: "Go",
      stars: 28,
      forks: 6,
      astScore: 88,
      qualityTier: "System Architect",
      tags: ["Go", "RabbitMQ", "gRPC", "Docker Compose"],
      updatedAt: "1 week ago",
      complexity: "High (Concurrent Pipelines)",
      isPrimary: true
    },
    {
      id: "repo3",
      name: "distro-kernel-lab",
      description: "Custom OS kernel experiments, process scheduler, and virtual memory allocator in C.",
      language: "C",
      stars: 19,
      forks: 4,
      astScore: 85,
      qualityTier: "Advanced CS",
      tags: ["C", "Assembly", "Makefile", "QEMU"],
      updatedAt: "3 weeks ago",
      complexity: "Very High (Low-level)",
      isPrimary: false
    },
    {
      id: "repo4",
      name: "leetcode-patterns-300",
      description: "Curated solutions for 300+ LeetCode problems with time & space complexity annotations.",
      language: "Python",
      stars: 65,
      forks: 21,
      astScore: 84,
      qualityTier: "Problem Solver",
      tags: ["Python", "DSA", "Algorithms", "Tests"],
      updatedAt: "Yesterday",
      complexity: "Medium",
      isPrimary: false
    }
  ],

  aiInsights: [
    {
      type: "positive",
      title: "Strong Technical Variety",
      description: "Your language breakdown demonstrates proficiency across frontend (TypeScript), backend (Go), and AI/scripting (Python).",
      actionLabel: "View Projects",
      actionRoute: "/projects"
    },
    {
      type: "recommendation",
      title: "Add Architecture Documentation",
      description: "Adding a System Architecture diagram (Mermaid/SVG) to 'microservice-event-bus' will elevate repo audit score from 88 to 95+.",
      actionLabel: "Identify Skill Gaps",
      actionRoute: "/skill-gaps"
    }
  ]
};
