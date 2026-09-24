export const dashboardData = {
  readinessScore: 78,
  readinessTrend: "+4% from last week",
  targetRole: "Backend Developer (SDE-1)",
  targetCompanyTier: "Tier-1 Product (MAANG / Unicorns)",
  sprintDay: 34,
  totalSprintDays: 90,

  // 7-Vector Score Baseline
  vectorScores: [
    { id: "dsa", vector: "DSA & Algorithms", score: 82, target: 85, color: "#6366f1" },
    { id: "sysdesign", vector: "System Design & Architecture", score: 70, target: 80, color: "#a855f7" },
    { id: "backend", vector: "Backend Engineering & APIs", score: 85, target: 90, color: "#10b981" },
    { id: "github", vector: "GitHub Code Quality Telemetry", score: 74, target: 80, color: "#818cf8" },
    { id: "leetcode", vector: "LeetCode Solves & Speed", score: 79, target: 85, color: "#f59e0b" },
    { id: "mock", vector: "AI Mock Interview Drills", score: 72, target: 80, color: "#ef4444" },
    { id: "comm", vector: "Verbal & Tech Articulation", score: 80, target: 85, color: "#34d399" }
  ],

  // 5-Week Telemetry Curve Data for Recharts
  weeklyTelemetryCurve: [
    { week: "W1", dsa: 62, sysDesign: 50, commits: 14, readiness: 60 },
    { week: "W2", dsa: 68, sysDesign: 55, commits: 22, readiness: 65 },
    { week: "W3", dsa: 74, sysDesign: 62, commits: 35, readiness: 71 },
    { week: "W4", dsa: 78, sysDesign: 66, commits: 48, readiness: 74 },
    { week: "W5", dsa: 82, sysDesign: 70, commits: 58, readiness: 78 }
  ],

  // AI Insights & Recommendations
  aiInsights: [
    {
      id: "ins-1",
      type: "remediation",
      title: "High Priority: Redis Invalidation & Caching",
      description: "Missing hands-on caching implementation in portfolio repos. Recommended 2-hour drill.",
      priority: "High",
      route: "/skill-gaps"
    },
    {
      id: "ins-2",
      type: "achievement",
      title: "Strong Performance: Graph Traversal Algorithms",
      description: "Scored 92% on LC 207 & LC 210 Topological Sort drills. Mastered Phase 2 Graph milestone!",
      priority: "Success",
      route: "/leetcode"
    },
    {
      id: "ins-3",
      type: "suggestion",
      title: "Upcoming Mock Drill: Spring Boot & Microservices",
      description: "Scheduled diagnostic simulation based on your target Tier-1 Backend Developer role.",
      priority: "Medium",
      route: "/mock-interview"
    }
  ],

  // Recent Activity Feed
  recentActivity: [
    { id: "act-1", title: "GitHub Sync", desc: "Pushed 4 commits to backend-microservices repo", time: "2 hours ago", type: "github" },
    { id: "act-2", title: "LeetCode Drill", desc: "Solved LC 207: Course Schedule (Medium Graph)", time: " Yesterday", type: "leetcode" },
    { id: "act-3", title: "ATS Resume Audit", desc: "Scored 84/100 for Backend Developer alignment", time: "2 days ago", type: "resume" },
    { id: "act-4", title: "AI Mock Interview", desc: "Completed System Design & REST API drill", time: "3 days ago", type: "mock" }
  ],

  // Quick Action Shortcuts
  quickActions: [
    { label: "Resume Audit", path: "/resume", color: "indigo" },
    { label: "GitHub Telemetry", path: "/github", color: "purple" },
    { label: "LeetCode Analytics", path: "/leetcode", color: "amber" },
    { label: "Projects Audit", path: "/projects", color: "emerald" },
    { label: "Launch AI Mock", path: "/mock-interview", color: "rose" }
  ]
};
