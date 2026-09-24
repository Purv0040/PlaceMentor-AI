// Centralized mock data for Communication Readiness Lab (15.html)

const STORAGE_KEY = "placementor_communication_history";

export const defaultCommunicationPrompts = [
  {
    id: "prompt-1",
    category: "System Design Walkthrough",
    title: "Explaining Caching & Eviction Strategy",
    promptText: "Explain how you designed the distributed caching layer in your portfolio project to a Senior Engineering Manager. Focus on articulating trade-offs clearly without filler words.",
    targetWpm: 145,
    suggestedKeywords: ["Redis", "Cache-Aside", "Latency", "Throughput", "Eviction", "Invalidation"]
  },
  {
    id: "prompt-2",
    category: "Behavioral / STAR",
    title: "Handling High-Pressure Production Outages",
    promptText: "Walk through a situation where a critical database query caused high CPU utilization. How did you communicate with stakeholders during the incident and what root-cause fix did you deploy?",
    targetWpm: 140,
    suggestedKeywords: ["STAR", "Incident Management", "PostgreSQL", "EXPLAIN ANALYZE", "Stakeholders", "Post-mortem"]
  },
  {
    id: "prompt-3",
    category: "Technical Trade-offs",
    title: "REST vs. gRPC Protocol Selection",
    promptText: "Articulate why your microservices event bus used gRPC Protobuf for inter-service communication instead of standard REST JSON APIs. Highlight performance gains succinctly.",
    targetWpm: 150,
    suggestedKeywords: ["gRPC", "Protobuf", "Serialization", "HTTP/2", "Multiplexing", "Payload Size"]
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
