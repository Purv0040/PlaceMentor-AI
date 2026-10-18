// Centralized data and prompts for Communication Readiness Lab

const STORAGE_KEY = "placementor_communication_history";

export const COMMUNICATION_CATEGORIES = [
  "All Categories",
  "System Design",
  "Behavioral & STAR",
  "Technical Trade-offs",
  "Incident & Problem Solving"
];

export const defaultCommunicationPrompts = [
  {
    id: "prompt-1",
    category: "System Design",
    title: "Explaining Caching & Eviction Strategy",
    promptText: "Explain how you designed the distributed caching layer in your portfolio project to a Senior Engineering Manager. Focus on articulating trade-offs clearly without filler words.",
    targetWpm: 145,
    targetDurationSec: 75,
    targetWordCount: "130–170 words",
    suggestedKeywords: ["Redis", "Cache-Aside", "Latency", "Throughput", "Eviction", "Invalidation"]
  },
  {
    id: "prompt-2",
    category: "Behavioral & STAR",
    title: "Handling High-Pressure Production Outages",
    promptText: "Walk through a situation where a critical database query caused high CPU utilization. How did you communicate with stakeholders during the incident and what root-cause fix did you deploy?",
    targetWpm: 140,
    targetDurationSec: 80,
    targetWordCount: "130–180 words",
    suggestedKeywords: ["STAR Framework", "Incident Management", "PostgreSQL", "EXPLAIN ANALYZE", "Stakeholders", "Post-mortem"]
  },
  {
    id: "prompt-3",
    category: "Technical Trade-offs",
    title: "REST vs. gRPC Protocol Selection",
    promptText: "Articulate why your microservices event bus used gRPC Protobuf for inter-service communication instead of standard REST JSON APIs. Highlight performance gains succinctly.",
    targetWpm: 150,
    targetDurationSec: 70,
    targetWordCount: "130–170 words",
    suggestedKeywords: ["gRPC", "Protobuf", "Serialization", "HTTP/2", "Multiplexing", "Payload Size"]
  },
  {
    id: "prompt-4",
    category: "System Design",
    title: "Database Sharding & Partitioning",
    promptText: "Explain how your system partitions and shards high-throughput relational data across database nodes to maintain low-latency query performance under peak load.",
    targetWpm: 145,
    targetDurationSec: 80,
    targetWordCount: "140–180 words",
    suggestedKeywords: ["Consistent Hashing", "Sharding Key", "Read Replicas", "Re-balancing", "Query Fanout"]
  },
  {
    id: "prompt-5",
    category: "Behavioral & STAR",
    title: "Resolving Technical Disagreements in a Team",
    promptText: "Describe a scenario where you and a senior teammate disagreed on an architectural decision or library choice. How did you resolve the conflict constructively while maintaining momentum?",
    targetWpm: 140,
    targetDurationSec: 75,
    targetWordCount: "130–170 words",
    suggestedKeywords: ["Active Listening", "Benchmarking", "Trade-off Matrix", "Objective Data", "Consensus"]
  },
  {
    id: "prompt-6",
    category: "Technical Trade-offs",
    title: "SQL vs. NoSQL Architectural Selection",
    promptText: "Defend your selection between PostgreSQL and MongoDB for a transactional user account and billing subsystem. What ACID or schema flexibility trade-offs justified your decision?",
    targetWpm: 145,
    targetDurationSec: 75,
    targetWordCount: "130–170 words",
    suggestedKeywords: ["ACID Compliance", "Foreign Keys", "Document Model", "Eventual Consistency", "Index Strategy"]
  },
  {
    id: "prompt-7",
    category: "Incident & Problem Solving",
    title: "Explaining Algorithms to Non-Technical Stakeholders",
    promptText: "Explain how a Dynamic Programming memoization algorithm works to a non-technical product manager using an everyday real-world analogy. Keep the explanation engaging and jargon-free.",
    targetWpm: 135,
    targetDurationSec: 70,
    targetWordCount: "120–160 words",
    suggestedKeywords: ["Real-world Analogy", "Subproblems", "Memoization", "Efficiency", "Time Reduction"]
  },
  {
    id: "prompt-8",
    category: "Incident & Problem Solving",
    title: "Troubleshooting a Production Memory Leak",
    promptText: "Walk through your step-by-step diagnostic methodology for isolating and resolving an unexpected heap memory leak or garbage collection spike in a live application service.",
    targetWpm: 140,
    targetDurationSec: 80,
    targetWordCount: "130–175 words",
    suggestedKeywords: ["Heap Profiling", "Tracemalloc", "GC Pauses", "Connection Leaks", "Root Cause Analysis"]
  }
];

export const defaultCommunicationHistory = [
  {
    id: "comm-1",
    date: "Today, 11:15 AM",
    title: "System Design Walkthrough",
    score: 78,
    verbalClarity: 82,
    wpm: 145,
    pitchStability: 74,
    fillerWordsCount: 2,
    feedback: "Excellent technical articulation. Speaking pace of 145 WPM is in the optimal range for Tier-1 engineering interviews."
  },
  {
    id: "comm-2",
    date: "2 days ago",
    title: "Behavioral / STAR",
    score: 72,
    verbalClarity: 75,
    wpm: 160,
    pitchStability: 68,
    fillerWordsCount: 5,
    feedback: "Pace was slightly fast (160 WPM). Slow down during the Action phase of the STAR narrative to emphasize metric outcomes."
  }
];

export const getPromptsByCategory = (category = "All Categories") => {
  if (!category || category === "All Categories") {
    return defaultCommunicationPrompts;
  }
  return defaultCommunicationPrompts.filter(p => p.category === category);
};

export const getRandomPrompt = (category = "All Categories", currentId = null) => {
  const list = getPromptsByCategory(category);
  if (list.length === 0) return defaultCommunicationPrompts[0];
  if (list.length === 1) return list[0];
  const candidates = currentId ? list.filter(p => p.id !== currentId) : list;
  const pool = candidates.length > 0 ? candidates : list;
  const randomIndex = Math.floor(Math.random() * pool.length);
  return pool[randomIndex];
};

export const getStoredCommunicationHistory = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      return JSON.parse(data);
    }
  } catch (e) {
    console.error("Failed to load communication history from localStorage", e);
  }
  return defaultCommunicationHistory;
};

export const saveCommunicationHistory = (history) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (e) {
    console.error("Failed to save communication history to localStorage", e);
  }
};
