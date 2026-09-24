// Centralized mock data for AI Mock Interview Studio (14.html)

const STORAGE_KEY = "placementor_interview_history";

export const defaultQuestions = [
  {
    id: "q-1",
    category: "System Design",
    topic: "Distributed Caching & Eviction",
    question: "Design a high-throughput distributed caching layer for a microservices architecture. How do you handle cache invalidation, stampede, and LRU eviction under peak traffic?",
    hint: "Mention Cache-Aside strategy, Redis Cluster, Mutex locks for cache stampede, and TTL expiration policies.",
    targetDuration: "10 mins",
    difficulty: "Hard",
    starterCodeOrAnswer: ""
  },
  {
    id: "q-2",
    category: "Technical / DSA",
    topic: "Graph Topological Sort",
    question: "Given a list of prerequisite courses (LC 207: Course Schedule), explain how you would detect cycles in a directed graph using Kahn's algorithm or DFS colors.",
    hint: "Explain in-degree array, queue traversal, and checking if visited count equals total nodes.",
    targetDuration: "8 mins",
    difficulty: "Medium",
    starterCodeOrAnswer: ""
  },
  {
    id: "q-3",
    category: "Behavioral / STAR",
    topic: "Conflict & Technical Trade-offs",
    question: "Describe a situation where you disagreed with a teammate's architectural decision. How did you evaluate trade-offs and reach a consensus using evidence?",
    hint: "Use STAR format: Situation, Task, Action (benchmarks/metrics), and Result (successful deployment).",
    targetDuration: "5 mins",
    difficulty: "Medium",
    starterCodeOrAnswer: ""
  },
  {
    id: "q-4",
    category: "Backend / Database",
    topic: "PostgreSQL Deadlock Prevention",
    question: "How do PostgreSQL transactions handle deadlock detection, and what strategies do you employ in application code to prevent deadlock conditions during concurrent updates?",
    hint: "Discuss lock order consistency, short transaction boundaries, explicit row locking (FOR UPDATE), and deadlock_timeout.",
    targetDuration: "7 mins",
    difficulty: "Hard",
    starterCodeOrAnswer: ""
  }
];

export const defaultInterviewHistory = [
  {
    id: "session-1",
    date: "Yesterday, 04:15 PM",
    role: "Backend SDE-1",
    type: "System Architecture & Design",
    difficulty: "Hard",
    questionCount: 3,
    durationText: "22 mins",
    score: 82,
    status: "Completed",
    strengths: ["Strong caching trade-off explanation", "Clean STAR response format"],
    weaknesses: ["Requires deeper explanation of Redis cluster partition tolerance"]
  },
  {
    id: "session-2",
    date: "3 days ago",
    role: "Backend SDE-1",
    type: "Technical / DSA Drill",
    difficulty: "Medium",
    questionCount: 5,
    durationText: "35 mins",
    score: 76,
    status: "Completed",
    strengths: ["Optimal Topological Sort code", "Accurate time complexity analysis"],
    weaknesses: ["2D Dynamic Programming space optimization missed"]
  }
];

export const getStoredInterviewHistory = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      return JSON.parse(data);
    }
  } catch (e) {
    console.error("Failed to load interview history from localStorage", e);
  }
  return defaultInterviewHistory;
};

export const saveInterviewHistory = (history) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    console.error("Failed to save interview history to localStorage", e);
  }
};
