// Centralized dynamic data generator for Today's Tasks (13.html, 20.html)

export const getDynamicTasks = (explicitRole = null, explicitSkills = null, explicitDay = 1) => {
  let role = explicitRole || 'Cybersecurity Analyst & Engineer';
  let skills = explicitSkills || ['Python', 'Java', 'Data Structures', 'SQL'];

  if (!explicitRole || !explicitSkills) {
    try {
      const sU = localStorage.getItem('placementor_user_data');
      if (sU) {
        const parsedU = JSON.parse(sU);
        if (!explicitRole && parsedU?.targetRole) role = parsedU.targetRole;
        if (!explicitSkills && parsedU?.selectedSkills) skills = parsedU.selectedSkills;
      }
      const sO = localStorage.getItem('placementCopilotOnboarding');
      if (sO) {
        const parsedO = JSON.parse(sO);
        if (!explicitRole && parsedO?.career?.targetRole) role = parsedO.career.targetRole;
        if (!explicitSkills && parsedO?.skills?.selectedSkills) skills = parsedO.skills.selectedSkills;
      }
    } catch (e) {}
  }

  const primarySkill = skills[0] || 'Core Stack';
  const day = explicitDay || 1;

  if (role.includes('AI/ML') || role.includes('Machine Learning')) {
    return [
      {
        id: "task-1",
        title: `Day ${day}: LC 207: Course Schedule & Tensor Matrix Operations`,
        description: "Implement Kahn's Topological Sort algorithm and matrix operations for ML dependency graphs.",
        category: "DSA",
        duration: "45 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/leetcode"
      },
      {
        id: "task-2",
        title: `Day ${day}: Build ${primarySkill || 'PyTorch'} Neural Network Training Pipeline`,
        description: "Implement model training, loss evaluation, and tensor data loaders.",
        category: "AI/ML",
        duration: "60 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/projects"
      },
      {
        id: "task-3",
        title: `Day ${day}: Deploy Model Inference API with FastAPI & Docker`,
        description: "Wrap trained model in asynchronous REST endpoint with sub-100ms inference latency.",
        category: "MLOps",
        duration: "30 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/skill-gaps"
      },
      {
        id: "task-4",
        title: `Day ${day}: Refactor Resume STAR Bullets for ML Model Accuracy`,
        description: "Include quantified metrics (+35% model throughput gain, 94% F1-score) in experience section.",
        category: "Resume",
        duration: "20 mins",
        priority: "Medium",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/resume"
      }
    ];
  } else if (role.includes('DevOps') || role.includes('Cloud') || role.includes('AWS')) {
    return [
      {
        id: "task-1",
        title: `Day ${day}: LC 207: Course Schedule (Network Graph Routing)`,
        description: "Implement Topological Sort algorithm for graph DAG network routing analysis.",
        category: "DSA",
        duration: "45 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/leetcode"
      },
      {
        id: "task-2",
        title: `Day ${day}: Write Terraform & Docker Manifests for Cloud Deploy`,
        description: "Automate multi-stage Docker builds and infrastructure provisioning for high availability.",
        category: "Cloud/DevOps",
        duration: "60 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/projects"
      },
      {
        id: "task-3",
        title: `Day ${day}: Configure Kubernetes Cluster Auto-Scaling & Helm Charts`,
        description: "Set up HPA (Horizontal Pod Autoscaler) and ingress controller rules for cloud workloads.",
        category: "Kubernetes",
        duration: "30 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/skill-gaps"
      },
      {
        id: "task-4",
        title: `Day ${day}: Refactor Resume STAR Bullets with Cloud Uptime Metrics`,
        description: "Quantify infrastructure gains (99.99% SLA uptime, 40% CI/CD build speedup) in experience section.",
        category: "Resume",
        duration: "20 mins",
        priority: "Medium",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/resume"
      }
    ];
  } else if (role.includes('Cybersecurity') || role.includes('Security')) {
    return [
      {
        id: "task-1",
        title: `Day ${day}: OWASP Security Audit & LC 207 (Dependency Graphs)`,
        description: "Audit REST Auth endpoints against OWASP Top 10 vulnerabilities & solve graph cycle detection.",
        category: "PenTesting",
        duration: "60 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/projects"
      },
      {
        id: "task-2",
        title: `Day ${day}: Solve LC 207: Course Schedule (Supply-Chain Graph Security)`,
        description: "Implement Topological Sort algorithm for software supply-chain dependency auditing.",
        category: "DSA",
        duration: "45 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/leetcode"
      },
      {
        id: "task-3",
        title: `Day ${day}: Wireshark Packet Analysis & SIEM Log Monitoring Drills`,
        description: "Set up intrusion detection rules (IDS) and audit Zero-Trust Network Access policies.",
        category: "Network Sec",
        duration: "30 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/skill-gaps"
      },
      {
        id: "task-4",
        title: `Day ${day}: Refactor Resume STAR Bullets with Security Compliance Metrics`,
        description: "Quantify security audit gains (100% OWASP compliance, zero critical CVEs) in experience section.",
        category: "Resume",
        duration: "20 mins",
        priority: "Medium",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/resume"
      }
    ];
  } else {
    return [
      {
        id: "task-1",
        title: `Day ${day}: LC 207: Course Schedule (Graph Cycle Detection)`,
        description: "Implement Kahn's Topological Sort algorithm in Python/TypeScript with O(V+E) time complexity.",
        category: "DSA",
        duration: "45 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/leetcode"
      },
      {
        id: "task-2",
        title: `Day ${day}: Optimize ${primarySkill || 'Full Stack'} REST Microservices Latency`,
        description: "Add async query execution and indexed database queries to boost response throughput by 35%.",
        category: "Projects",
        duration: "60 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/projects"
      },
      {
        id: "task-3",
        title: `Day ${day}: Review System Design: Redis Caching & Eviction Policies`,
        description: "Study Cache-Aside, Write-Through, and LRU eviction policy trade-offs for backend screening.",
        category: "System Design",
        duration: "30 mins",
        priority: "High",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/skill-gaps"
      },
      {
        id: "task-4",
        title: `Day ${day}: Refactor Resume STAR Bullets for Experience Section`,
        description: "Quantify metrics in SDE Intern bullets (+40% query throughput gain).",
        category: "Resume",
        duration: "20 mins",
        priority: "Medium",
        completed: false,
        dayNumber: day,
        phaseId: "phase-1",
        route: "/resume"
      }
    ];
  }
};

export const initialTaskData = getDynamicTasks();
export const taskData = initialTaskData;

