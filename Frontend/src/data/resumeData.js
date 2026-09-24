// Centralized mock data for Resume Intelligence (7.html)

export const initialResumeData = {
  fileName: "Digisha_Resume.pdf",
  fileSize: "1.4 MB",
  pageCount: 2,
  lastAnalyzed: "2 hours ago",
  targetRole: "Backend SDE-1 (Tier 1)",
  overallScore: 84,
  scoreChange: "+6% vs last version",
  status: "ATS Verified",
  
  metrics: {
    atsScore: 84,
    sectionCompleteness: 92,
    bulletActionability: 78,
    keywordMatch: 71,
  },

  sections: [
    { name: "Contact & Links", score: 100, status: "complete" },
    { name: "Education & GPA", score: 95, status: "complete" },
    { name: "Work Experience", score: 82, status: "needs-improvement" },
    { name: "Technical Projects", score: 88, status: "complete" },
    { name: "Skills & Tech Stack", score: 72, status: "missing-keywords" },
  ],

  detectedSkills: [
    { name: "Python", category: "Languages", level: "Advanced", match: true },
    { name: "TypeScript", category: "Languages", level: "Advanced", match: true },
    { name: "React.js", category: "Frameworks", level: "Intermediate", match: true },
    { name: "Node.js", category: "Frameworks", level: "Intermediate", match: true },
    { name: "FastAPI", category: "Frameworks", level: "Intermediate", match: true },
    { name: "PostgreSQL", category: "Databases", level: "Intermediate", match: true },
    { name: "Docker", category: "DevOps", level: "Basic", match: true },
    { name: "Git", category: "Tools", level: "Advanced", match: true },
  ],

  missingSkills: [
    { name: "Redis", category: "Databases", importance: "High", roleReq: "Required for SDE-1 Caching" },
    { name: "Kubernetes", category: "DevOps", importance: "Medium", roleReq: "Preferred Tier-1 Skill" },
    { name: "Kafka / RabbitMQ", category: "Architecture", importance: "High", roleReq: "Pub-Sub Messaging" },
    { name: "gRPC", category: "Networking", importance: "Low", roleReq: "Microservices Inter-comm" },
  ],

  bulletAudits: [
    {
      id: "b1",
      section: "Projects - PlaceMentor AI",
      original: "Built an AI resume scanner using React and Python backend.",
      improved: "Engineered an AI resume intelligence engine using React and FastAPI, reducing parser latency by 35% across 500+ test resumes.",
      rationale: "Quantified metric added (+35% latency reduction), strong action verb ('Engineered'), clear scale ('500+ test resumes').",
      score: 94,
      isWeak: true
    },
    {
      id: "b2",
      section: "Experience - SDE Intern",
      original: "Worked on REST APIs and fixed database queries.",
      improved: "Optimized 12+ PostgreSQL query plans using index tuning, improving endpoint throughput by 40% under peak load.",
      rationale: "Replaced generic 'worked on' with 'Optimized', specified PostgreSQL indexing, and quantified 40% throughput gain.",
      score: 92,
      isWeak: true
    },
    {
      id: "b3",
      section: "Projects - Microservice Event Bus",
      original: "Implemented Pub/Sub system using RabbitMQ and Docker containers.",
      improved: "Architected a decoupled event bus with RabbitMQ and Docker, handling 2,000+ events/sec with 99.9% uptime in local cluster testing.",
      rationale: "Demonstrates architectural ownership and high throughput scalability benchmarks.",
      score: 96,
      isWeak: false
    }
  ],

  aiInsights: [
    {
      type: "critical",
      title: "Missing Distributed Caching Evidence",
      description: "Tier-1 SDE-1 backend roles require explicit mention of Redis/Memcached. Consider adding caching impact to your database project.",
      actionLabel: "Analyze Skill Gaps",
      actionRoute: "/skill-gaps"
    },
    {
      type: "suggestion",
      title: "Bullet Actionability Boost Available",
      description: "2 experience bullets lack quantified metrics. Transforming bullet text to STAR format will raise overall ATS score from 84 to 90+.",
      actionLabel: "Fix Bullets with AI",
      actionTab: "bullets"
    }
  ]
};
