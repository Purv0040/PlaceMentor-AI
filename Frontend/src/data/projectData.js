// Centralized mock data for Project Intelligence (10.html)

const STORAGE_KEY = "placementor_projects_data";

export const defaultProjects = [
  {
    id: "proj-1",
    title: "PlaceMentor AI — SDE Placement Copilot",
    description: "Full-stack AI placement mentoring platform featuring AST code audit, automated ATS resume intelligence, and adaptive 90-day roadmaps.",
    category: "Full Stack / AI",
    technologies: ["React", "FastAPI", "Python", "TailwindCSS", "Recharts", "PostgreSQL"],
    githubUrl: "https://github.com/Purv0040/PlaceMentor-AI",
    liveUrl: "https://placementor-ai.demo.app",
    score: 92,
    scoreBadge: "Production Grade",
    complexityScore: 92,
    architectureTags: ["Microservices", "JWT Auth", "AST Parsing", "Rest API"],
    evidenceBullets: [
      "Engineered full-stack placement copilot serving 1,000+ simulated candidate telemetry queries with sub-200ms API response time.",
      "Architected AST code parser and ATS resume scanner using Python and React, increasing resume match scoring accuracy by 35%."
    ],
    updatedAt: "2 days ago"
  },
  {
    id: "proj-2",
    title: "Distributed Event Bus & Pub-Sub Broker",
    description: "High-throughput messaging broker written in Go implementing AMQP protocol, RabbitMQ channels, and gRPC streaming endpoints.",
    category: "Backend / Systems",
    technologies: ["Go", "RabbitMQ", "gRPC", "Docker", "Protobuf"],
    githubUrl: "https://github.com/Purv0040/microservice-event-bus",
    liveUrl: "",
    score: 88,
    scoreBadge: "System Architect",
    complexityScore: 88,
    architectureTags: ["Pub-Sub", "gRPC Streaming", "Docker Compose", "Concurrent Pipelines"],
    evidenceBullets: [
      "Architected high-concurrency event bus in Go handling 2,000+ events/sec with zero message loss in benchmark tests.",
      "Implemented gRPC streaming handlers reducing inter-service payload size by 40% compared to REST JSON."
    ],
    updatedAt: "1 week ago"
  },
  {
    id: "proj-3",
    title: "OS Kernel Scheduler & Virtual Memory Lab",
    description: "Custom x86 process scheduler, round-robin preemptive scheduler, and buddy allocator memory manager built in C.",
    category: "Systems Programming",
    technologies: ["C", "Assembly", "QEMU", "Makefile", "GDB"],
    githubUrl: "https://github.com/Purv0040/distro-kernel-lab",
    liveUrl: "",
    score: 85,
    scoreBadge: "Advanced CS",
    complexityScore: 85,
    architectureTags: ["Low-level Kernel", "Interrupt Handlers", "Preemptive Scheduling"],
    evidenceBullets: [
      "Developed preemptive CPU scheduler in C supporting 64 concurrent tasks with context switching latency under 15 microseconds.",
      "Implemented buddy memory allocation scheme reducing external fragmentation by 28% in synthetic workloads."
    ],
    updatedAt: "3 weeks ago"
  },
  {
    id: "proj-4",
    title: "Real-Time Collaborative Markdown Editor",
    description: "Multi-user document editor utilizing Operational Transformation (OT), WebSockets, and Redis pub-sub for instant sync.",
    category: "Full Stack",
    technologies: ["Node.js", "WebSockets", "Redis", "React", "MongoDB"],
    githubUrl: "https://github.com/Purv0040/collab-md-editor",
    liveUrl: "https://collab-md.demo.app",
    score: 80,
    scoreBadge: "Good Evidence",
    complexityScore: 80,
    architectureTags: ["WebSockets", "Redis Pub-Sub", "Operational Transformation"],
    evidenceBullets: [
      "Built real-time collaborative document engine maintaining sub-50ms synchronization across 50 concurrent active websockets.",
      "Integrated Redis caching layer reducing database read queries by 65% during peak editor sessions."
    ],
    updatedAt: "1 month ago"
  }
];

export const getStoredProjects = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      return JSON.parse(data);
    }
  } catch (e) {
    console.error("Failed to load projects from localStorage", e);
  }
  return defaultProjects;
};

export const saveProjectsToStorage = (projects) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  } catch (e) {
    console.error("Failed to save projects to localStorage", e);
  }
};
