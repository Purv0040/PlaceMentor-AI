// Centralized mock data for LeetCode Intelligence (9.html)

export const initialLeetcodeData = {
  isConnected: true,
  handle: "digisha_prep",
  profileUrl: "https://leetcode.com/digisha_prep",
  lastSynced: "Today, 10:30 AM",
  
  metrics: {
    contestRating: 1842,
    globalRank: "Top 4.8%",
    rankTitle: "Knight",
    totalSolved: 342,
    targetSolved: 400,
    readinessScore: 79,
    currentStreakDays: 24,
    longestStreakDays: 48,
    activeDaysCount: 156,
  },

  difficultyBreakdown: {
    easy: { solved: 140, total: 820, target: 120, percentage: 17 },
    medium: { solved: 165, total: 1740, target: 200, percentage: 9 },
    hard: { solved: 37, total: 750, target: 50, percentage: 5 },
  },

  difficultyChartData: [
    { name: "Easy", Solved: 140, Target: 120, color: "#4edea3" },
    { name: "Medium", Solved: 165, Target: 200, color: "#8083ff" },
    { name: "Hard", Solved: 37, Target: 50, color: "#ffb4ab" },
  ],

  topicPerformance: [
    { topic: "Arrays & Strings", score: 88, solved: 75, target: 70, status: "Mastered" },
    { topic: "Trees & Graphs", score: 80, solved: 54, target: 50, status: "Strong" },
    { topic: "Dynamic Programming", score: 58, solved: 32, target: 60, status: "Needs Practice" },
    { topic: "System Design & OOD", score: 64, solved: 18, target: 30, status: "Intermediate" },
    { topic: "Sliding Window & Two Pointers", score: 85, solved: 42, target: 40, status: "Mastered" },
    { topic: "Backtracking & Recursion", score: 72, solved: 26, target: 30, status: "Strong" },
  ],

  recentSubmissions: [
    {
      id: "sub1",
      title: "Course Schedule II",
      difficulty: "Medium",
      topic: "Graphs / Topological Sort",
      time: "2 hours ago",
      status: "Accepted",
      runtime: "48 ms (Beats 89%)",
      memory: "16.4 MB",
      aiRating: "Optimal O(V+E)"
    },
    {
      id: "sub2",
      title: "Coin Change",
      difficulty: "Medium",
      topic: "Dynamic Programming",
      time: "Yesterday",
      status: "Accepted",
      runtime: "124 ms (Beats 72%)",
      memory: "15.1 MB",
      aiRating: "Standard Bottom-up DP"
    },
    {
      id: "sub3",
      title: "Trapping Rain Water",
      difficulty: "Hard",
      topic: "Two Pointers",
      time: "2 days ago",
      status: "Accepted",
      runtime: "52 ms (Beats 94%)",
      memory: "16.8 MB",
      aiRating: "Optimal O(N) Two Pointer"
    },
    {
      id: "sub4",
      title: "Lowest Common Ancestor of BST",
      difficulty: "Medium",
      topic: "Trees",
      time: "3 days ago",
      status: "Accepted",
      runtime: "68 ms (Beats 85%)",
      memory: "18.2 MB",
      aiRating: "Optimal Recursive BST"
    }
  ],

  aiInsights: [
    {
      type: "focus",
      title: "Dynamic Programming Gap Identified",
      description: "You have solved 32 DP problems (target: 60). Focus on 2D DP matrix problems to pass Tier-1 SDE screening cutoffs.",
      actionLabel: "View Today's Tasks",
      actionRoute: "/tasks"
    },
    {
      type: "milestone",
      title: "Knight Rank Achieved (Rating 1842)",
      description: "Your contest rating puts you in the top 5% globally. Maintaining this rating unlocks direct referral readiness.",
      actionLabel: "View 90-Day Roadmap",
      actionRoute: "/roadmap"
    }
  ]
};
