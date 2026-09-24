// Centralized mock data for 90-Day Adaptive Roadmap (1.html, 2.html, 13.html)

export const initialRoadmapData = {
  totalDays: 90,
  currentDay: 34,
  currentPhaseId: "phase-2",
  completedDaysCount: 33,
  overallProgressPercent: 38,
  lastAdapted: "Today, 08:30 AM (Telemetry Driven)",
  activeSprintName: "Sprint 5: Microservices & Advanced Graphs",

  phases: [
    {
      id: "phase-1",
      title: "Phase 1: Core DSA & CS Fundamentals",
      subtitle: "Arrays, Trees, OOP & SQL Query Fundamentals",
      startDay: 1,
      endDay: 30,
      durationDays: 30,
      status: "completed",
      progressPercent: 100,
      milestones: [
        "Mastered Binary Trees & BFS/DFS Traversals",
        "Completed 120 Easy/Medium LeetCode problems",
        "Configured PostgreSQL indexing & ER Diagrams"
      ]
    },
    {
      id: "phase-2",
      title: "Phase 2: Advanced DSA & System Architecture",
      subtitle: "Graphs, Dynamic Programming, Microservices & Caching",
      startDay: 31,
      endDay: 60,
      durationDays: 30,
      status: "in-progress",
      progressPercent: 35,
      milestones: [
        "Day 31-35: Graph Cycle Detection & Topological Sort (Current)",
        "Day 36-45: 2D Dynamic Programming & Knapsack Patterns",
        "Day 46-60: Distributed Caching (Redis) & Pub-Sub Architecture"
      ]
    },
    {
      id: "phase-3",
      title: "Phase 3: Tier-1 Mocks & Behavioral Polish",
      subtitle: "Company Question Banks, System Design Mocks & STAR Audits",
      startDay: 61,
      endDay: 90,
      durationDays: 30,
      status: "upcoming",
      progressPercent: 0,
      milestones: [
        "Day 61-75: Target Company (Google/Amazon) Question Drills",
        "Day 76-85: Live AI System Design & Communication Mocks",
        "Day 86-90: Final Placement Drive Sprint & HR Behavioral Prep"
      ]
    }
  ],

  day34Details: {
    dayNumber: 34,
    dateText: "Today · Sprint 5 Day 4",
    focusTitle: "Graphs, Pub-Sub Microservices & DBMS Tuning",
    description: "Focus on Graph Cycle Detection (LC 207), RabbitMQ Event Bus channels, and PostgreSQL EXPLAIN ANALYZE index tuning.",
    skillsCovered: ["Graphs / Topological Sort", "RabbitMQ / Pub-Sub", "SQL Indexing"],
    recommendedHours: "3.5 Hours"
  },

  adaptiveRebalancingNotice: {
    isAdapted: true,
    reason: "Telemetry re-balanced based on Skill Gap analysis (Redis Caching & DP gaps prioritized).",
    adaptedAt: "Today, 08:30 AM",
    adjustments: [
      "Shifted 2 System Design tasks into Sprint 5 active schedule.",
      "Added 3 Medium DP problems to Day 36 execution matrix."
    ]
  }
};
