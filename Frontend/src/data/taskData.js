// Centralized mock data for Today's Tasks (13.html, 20.html)

export const initialTaskData = [
  {
    id: "task-1",
    title: "Solve LC 207: Course Schedule (Graph Cycle Detection)",
    description: "Implement Kahn's Topological Sort algorithm in Python/TypeScript with O(V+E) time complexity.",
    category: "DSA",
    duration: "45 mins",
    priority: "High",
    completed: true,
    dayNumber: 34,
    phaseId: "phase-2",
    route: "/leetcode"
  },
  {
    id: "task-2",
    title: "Optimize PlaceMentor AI FastAPI Endpoint Latency",
    description: "Add async query execution to reduce parser latency by 35% across test resumes.",
    category: "Projects",
    duration: "60 mins",
    priority: "High",
    completed: true,
    dayNumber: 34,
    phaseId: "phase-2",
    route: "/projects"
  },
  {
    id: "task-3",
    title: "Review System Design: Redis Caching & Eviction Policies",
    description: "Study Cache-Aside, Write-Through, and LRU eviction policy trade-offs for backend screening.",
    category: "System Design",
    duration: "30 mins",
    priority: "High",
    completed: false,
    dayNumber: 34,
    phaseId: "phase-2",
    route: "/skill-gaps"
  },
  {
    id: "task-4",
    title: "Refactor Resume STAR Bullets for Experience Section",
    description: "Quantify metrics in SDE Intern bullets (+40% query throughput gain).",
    category: "Resume",
    duration: "20 mins",
    priority: "Medium",
    completed: false,
    dayNumber: 34,
    phaseId: "phase-2",
    route: "/resume"
  },
  {
    id: "task-5",
    title: "Solve LC 210: Course Schedule II (Topological Order)",
    description: "Return valid course ordering array or empty array if cycle exists.",
    category: "LeetCode",
    duration: "45 mins",
    priority: "Medium",
    completed: false,
    dayNumber: 34,
    phaseId: "phase-2",
    route: "/leetcode"
  }
];

export const taskData = initialTaskData;
