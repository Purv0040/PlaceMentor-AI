// Centralized mock data for Progress Telemetry (3.html, 13.html, 17.html)

export const initialProgressData = {
  overallProgressPercent: 64,
  completedTasksCount: 42,
  totalTasksCount: 70,
  currentStreakDays: 24,
  longestStreakDays: 48,
  roadmapCompletionPercent: 38,
  studyHoursTotal: 142,

  weeklyCompletionVelocity: [
    { week: "W1", completed: 8, target: 10, hours: 18 },
    { week: "W2", completed: 10, target: 10, hours: 22 },
    { week: "W3", completed: 9, target: 10, hours: 20 },
    { week: "W4", completed: 11, target: 10, hours: 25 },
    { week: "W5", completed: 12, target: 10, hours: 28 },
  ],

  moduleProgressBreakdown: [
    { module: "Resume Intelligence", score: 84, status: "ATS Verified", route: "/resume" },
    { module: "GitHub Intelligence", score: 82, status: "Production Grade", route: "/github" },
    { module: "LeetCode Intelligence", score: 79, status: "Knight Rank", route: "/leetcode" },
    { module: "Project Intelligence", score: 88, status: "System Architect", route: "/projects" },
    { module: "Placement Readiness", score: 82, status: "Tier-1 Prospect", route: "/placement-readiness" },
    { module: "Skill Gap Analyzer", score: 72, status: "6 Gaps Identified", route: "/skill-gaps" },
  ]
};
