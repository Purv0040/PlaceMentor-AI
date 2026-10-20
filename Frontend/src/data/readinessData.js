// Centralized mock data for Placement Readiness

export const initialReadinessData = {
  overallScore: 82,
  scoreStatus: "Strong Tier-1 Prospect",
  percentileRank: "Top 8.4% among Tier-1 Candidates",
  lastSynced: "Today, 10:55 PM (AST & API Verified)",
  confidenceIndex: "94.2% (4 Vectors Connected)",
  targetBenchmark: "Full Stack Engineer",
  
  vectorScores: [
    { name: "DSA & Problem Solving", score: 84, target: 85, weight: "30%", status: "On Track" },
    { name: "Resume Intelligence", score: 84, target: 85, weight: "25%", status: "On Track" },
    { name: "GitHub Impact & Code", score: 80, target: 80, weight: "25%", status: "On Track" },
    { name: "Mock Technical Interview", score: 78, target: 75, weight: "20%", status: "On Track" },
  ],

  radarData: [
    { vector: "DSA", Score: 84, Benchmark: 85 },
    { vector: "Resume", Score: 84, Benchmark: 85 },
    { vector: "GitHub", Score: 80, Benchmark: 80 },
    { vector: "Interview", Score: 78, Benchmark: 75 },
  ],

  dimensionsSummary: [
    {
      id: "dim-resume",
      name: "Resume Intelligence",
      score: 84,
      status: "ATS Verified",
      route: "/resume",
      detail: "84/100 · ATS compliance & STAR formatting calibrated"
    },
    {
      id: "dim-dsa",
      name: "LeetCode & Problem Solving",
      score: 84,
      status: "Knight Rank",
      route: "/leetcode",
      detail: "84/100 · DSA problem solving and topic mastery"
    },
    {
      id: "dim-github",
      name: "GitHub Portfolio",
      score: 80,
      status: "Production Grade",
      route: "/github",
      detail: "80/100 · Repository depth and active commit streaks"
    },
    {
      id: "dim-interview",
      name: "Mock Technical Interview",
      score: 78,
      status: "Screen Ready",
      route: "/interviews",
      detail: "78/100 · Simulated technical screen and problem breakdown"
    },
  ],

  tier1Benchmarks: [
    { company: "Google / Meta", minReadiness: 88, currentMatch: "82% (Requires DP & System Design Boost)" },
    { company: "Amazon / Microsoft", minReadiness: 82, currentMatch: "Qualified Benchmark Tier" },
    { company: "Tier-1 Unicorns (Uber / Swiggy)", minReadiness: 80, currentMatch: "Qualified Benchmark Tier" },
    { company: "High-Growth FinTech (Razorpay / CRED)", minReadiness: 78, currentMatch: "Exceeds Minimum Benchmark" },
  ],

  priorityRemediations: [
    {
      id: "rem-1",
      vector: "DSA & Screening",
      priority: "Critical",
      title: "Solve Additional Dynamic Programming Problems",
      description: "Complete targeted medium DP problems to strengthen LeetCode screening confidence.",
      actionLabel: "View 90-Day Roadmap",
      actionRoute: "/roadmap"
    },
    {
      id: "rem-2",
      vector: "Resume Intelligence",
      priority: "High",
      title: "Strengthen STAR Bullet Action Verbs",
      description: "Enhance quantitative impact metrics across primary project bullets for higher ATS ranking.",
      actionLabel: "Audit Resume",
      actionRoute: "/resume"
    }
  ]
};

