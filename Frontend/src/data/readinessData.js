// Centralized mock data for Placement Readiness (11.html & 4.html)

export const initialReadinessData = {
  overallScore: 82,
  scoreStatus: "Strong Tier-1 Prospect",
  percentileRank: "Top 8.4% among Tier-1 Candidates",
  lastSynced: "Today, 10:55 PM (AST & API Verified)",
  confidenceIndex: "94.2% (7 Vectors Connected)",
  targetBenchmark: "Tier-1 SDE / ML Specialist",
  
  vectorScores: [
    { name: "Data Structures & Algorithms", score: 84, target: 85, weight: "25%", status: "On Track" },
    { name: "System Architecture & Design", score: 76, target: 80, weight: "20%", status: "Needs Review" },
    { name: "Portfolio Projects Audit", score: 88, target: 85, weight: "20%", status: "Exceeds" },
    { name: "CS Fundamentals & DBMS", score: 82, target: 80, weight: "15%", status: "On Track" },
    { name: "ATS Resume Compliance", score: 84, target: 85, weight: "10%", status: "On Track" },
    { name: "LeetCode Screening Rating", score: 79, target: 80, weight: "5%", status: "On Track" },
    { name: "Soft Skills & Communication", score: 75, target: 80, weight: "5%", status: "Needs Practice" },
  ],

  radarData: [
    { vector: "DSA", Score: 84, Benchmark: 85 },
    { vector: "Sys Design", Score: 76, Benchmark: 80 },
    { vector: "Projects", Score: 88, Benchmark: 85 },
    { vector: "CS Fund", Score: 82, Benchmark: 80 },
    { vector: "Resume", Score: 84, Benchmark: 85 },
    { vector: "LeetCode", Score: 79, Benchmark: 80 },
    { vector: "Soft Skills", Score: 75, Benchmark: 80 },
  ],

  dimensionsSummary: [
    {
      id: "dim-resume",
      name: "Resume Intelligence",
      score: 84,
      status: "ATS Verified",
      route: "/resume",
      detail: "84/100 · 2 bullets require quantitative STAR metrics"
    },
    {
      id: "dim-github",
      name: "GitHub Intelligence",
      score: 82,
      status: "Production Grade",
      route: "/github",
      detail: "82/100 · 648 commits, 42-day active streak"
    },
    {
      id: "dim-leetcode",
      name: "LeetCode Intelligence",
      score: 79,
      status: "Knight Rank (1842)",
      route: "/leetcode",
      detail: "342 solved · DP requires 28 additional medium problems"
    },
    {
      id: "dim-projects",
      name: "Project Intelligence",
      score: 88,
      status: "System Architect",
      route: "/projects",
      detail: "88/100 · 4 projects audited with sub-200ms latency"
    },
  ],

  tier1Benchmarks: [
    { company: "Google / Meta", minReadiness: 88, currentMatch: "82% (Requires DP + Sys Design Boost)" },
    { company: "Amazon / Microsoft", minReadiness: 82, currentMatch: "Qualified Benchmark Tier" },
    { company: "Tier-1 Unicorns (Uber / Swiggy)", minReadiness: 80, currentMatch: "Qualified Benchmark Tier" },
    { company: "High-Growth FinTech (Razorpay / CRED)", minReadiness: 78, currentMatch: "Exceeds Minimum Benchmark" },
  ],

  priorityRemediations: [
    {
      id: "rem-1",
      vector: "System Architecture",
      priority: "Critical",
      title: "Add Redis Invalidation & Caching Evidence",
      description: "Tier-1 SDE-1 backend roles require explicit mention of Redis/Memcached. Include distributed caching impact in your portfolio projects.",
      actionLabel: "Analyze Skill Gaps",
      actionRoute: "/skill-gaps"
    },
    {
      id: "rem-2",
      vector: "DSA & Screening",
      priority: "High",
      title: "Solve 28 Additional Dynamic Programming Medium Problems",
      description: "Your DP topic performance is at 58% (target 80%). Completing 28 medium DP problems will push your LeetCode readiness from 79 to 88%.",
      actionLabel: "View 90-Day Roadmap",
      actionRoute: "/roadmap"
    }
  ]
};
