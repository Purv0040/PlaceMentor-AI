export const aiService = {
  analyzeResume: async (fileName) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          atsScore: 88,
          sectionScore: 92,
          skillsDetected: ["Python", "TypeScript", "React.js", "FastAPI", "PostgreSQL", "Docker"],
          missingSkills: ["Redis", "Kafka", "Kubernetes", "gRPC"],
          recommendations: [
            "Quantified metric added to project experience bullets (+35% speed improvement).",
            "Added explicit mention of Docker containerization and FastAPI endpoints.",
            "Include Redis distributed caching pattern evidence for Tier-1 backend eligibility."
          ],
          strengths: ["Strong action verbs (Engineered, Optimized, Architected)", "Clean multi-page ATS formatting"],
          warnings: ["2 experience bullets lack quantified scale metrics"]
        });
      }, 1000);
    });
  },

  getGithubAnalysis: async (handle) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          handle: handle || "Purv0040",
          impactScore: 82,
          qualityTier: "Production Grade",
          insights: [
            "Repository activity indicates consistent daily engineering commitment.",
            "AST audit shows high code modularity and proper error boundary coverage in PlaceMentor-AI."
          ]
        });
      }, 800);
    });
  },

  getLeetcodeAnalysis: async (handle) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          handle: handle || "digisha_prep",
          contestRating: 1842,
          rankTitle: "Knight",
          solvedTotal: 342,
          insights: [
            "Arrays and Trees show high mastery (>80%).",
            "Dynamic Programming requires 28 additional medium problems to meet Tier-1 screening benchmark."
          ]
        });
      }, 800);
    });
  },

  getProjectAudit: async (projectTitle) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          title: projectTitle,
          score: 92,
          architectureBadge: "System Architect",
          generatedBullets: [
            `Engineered ${projectTitle} featuring sub-200ms latency and high concurrency handling.`,
            `Architected decoupled event bus and REST endpoints, improving throughput by 35%.`
          ]
        });
      }, 700);
    });
  },

  generateReadinessInsights: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          overallScore: 82,
          status: "Strong Tier-1 Prospect",
          recommendations: [
            "Implement Redis distributed caching evidence in Projects to boost System Design score.",
            "Solve 28 additional Medium Dynamic Programming problems to reach Knight-level LeetCode readiness."
          ]
        });
      }, 700);
    });
  },

  analyzeSkillGaps: async (targetRole) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          targetRole: targetRole || "Backend Developer",
          overallCoverage: 72,
          criticalGapsCount: 2,
          topSkillToLearn: "Redis Distributed Caching",
          recommendationSummary: "Focusing on Redis Caching and 2D Dynamic Programming will close 80% of your Tier-1 screening gaps."
        });
      }, 800);
    });
  },

  analyzeSkillGap: async (targetRole) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          role: targetRole,
          gaps: [
            { skill: "Redis Caching Patterns", priority: "High" },
            { skill: "Kafka Event Streaming", priority: "Medium" }
          ]
        });
      }, 700);
    });
  },

  generateRoadmap: async (userPreferences) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          planDays: 90,
          currentDay: 34,
          primaryFocus: "Backend Microservices & Advanced DSA",
          lastAdapted: "Just now (AI Calibrated)"
        });
      }, 900);
    });
  },

  adaptRoadmapAI: async (skillGapItem) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          skill: skillGapItem.skill || "Target Skill",
          addedToDay: 35,
          phase: "Phase 2: Advanced DSA & System Architecture",
          message: `Added "${skillGapItem.skill || 'Skill'}" to Day 35 execution matrix with high priority.`
        });
      }, 700);
    });
  },

  evaluateInterviewAnswer: async (question, answerText) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const wordCount = answerText ? answerText.trim().split(/\s+/).length : 0;
        const score = wordCount > 40 ? 82 : wordCount > 15 ? 74 : 65;
        resolve({
          score: score,
          technicalAccuracy: Math.min(score + 4, 98),
          communicationClarity: Math.min(score - 2, 92),
          answerStructure: Math.min(score + 2, 95),
          strengths: [
            "Good identification of core architectural components",
            "Clear technical terminology and trade-off awareness"
          ],
          weaknesses: [
            "Could include more explicit scale numbers (e.g. throughput metrics)",
            "Consider detailing failover and error boundary handling"
          ],
          aiFeedback: "Solid technical response demonstrating understanding of backend microservices and data flow patterns."
        });
      }, 1000);
    });
  },

  evaluateCommunicationResponse: async (prompt, responseText) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const wordCount = responseText ? responseText.trim().split(/\s+/).length : 0;
        const score = wordCount > 30 ? 80 : 70;
        resolve({
          overallScore: score,
          verbalClarity: Math.min(score + 4, 95),
          wpm: 145,
          pitchStability: Math.min(score - 4, 88),
          fillerWordsCount: Math.max(1, 5 - Math.floor(wordCount / 20)),
          strengths: [
            "Speaking pace of 145 WPM is in the optimal interview cadence range",
            "Structured explanation using STAR narrative format"
          ],
          improvements: [
            "Pause slightly longer between key architectural points for emphasis",
            "Reduce filler transitions ('you know', 'like') during technical trade-offs"
          ],
          feedback: "Great articulation! You conveyed the technical concepts clearly with minimal speech hesitation."
        });
      }, 900);
    });
  },

  // Extended AI Mentor response generation supporting full context objects and persona tuning
  generateMentorResponse: async (userMessage, mentorContext = null, persona = 'tech') => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const query = typeof userMessage === 'string' ? userMessage.toLowerCase().trim() : '';
        const role = mentorContext?.user?.targetRole || 'Backend Developer';
        const name = mentorContext?.user?.name || 'Alex Patel';
        const day = mentorContext?.roadmap?.currentDay || 42;
        const score = mentorContext?.readiness?.overallScore || 78;
        const tasks = mentorContext?.todayTasks?.pendingTaskList || [];
        const solved = mentorContext?.leetcode?.totalSolved || 385;
        const ats = mentorContext?.resume?.atsScore || 84;
        const githubScore = mentorContext?.github?.impactScore || 82;

        let responseText = "";
        let codeSnippet = null;
        let svgDiagram = false;
        let checkpoint = null;
        let actions = [];

        // 1. Daily Planning & Today's Tasks
        if (query.includes("today") || query.includes("task") || query.includes("schedule") || query.includes("work on") || query.includes("daily")) {
          const firstTask = tasks[0]?.title || "Solve LC #210 (Course Schedule II)";
          const firstTaskCat = tasks[0]?.category || "DSA & Algorithms";
          const firstTaskDur = tasks[0]?.duration || "45 mins";

          responseText = `Hello **${name}**! Today is **Day ${day}** of your 90-Day Placement Roadmap.\n\nYou have **${tasks.length || 2} pending tasks** scheduled for today:\n\n1. 📌 **${firstTask}** (${firstTaskCat}, ${firstTaskDur})\n${tasks[1] ? `2. 📌 **${tasks[1].title}** (${tasks[1].category})\n` : ''}\nCompleting the **${firstTaskCat}** task first directly addresses your target role execution goals.`;

          actions = [
            { label: "View Today's Tasks", route: "/tasks" },
            { label: "Open 90-Day Roadmap", route: "/roadmap" }
          ];
        }
        // 2. Skill Gaps & Weaknesses
        else if (query.includes("gap") || query.includes("weakness") || query.includes("learn") || query.includes("improve skill")) {
          const topGaps = mentorContext?.skillGaps?.topGaps || [];
          const topGap1 = topGaps[0]?.skill || "Redis Distributed Caching";
          const topGap2 = topGaps[1]?.skill || "Dynamic Programming (2D & Tree DP)";
          const topGap3 = topGaps[2]?.skill || "Kubernetes Orchestration";

          responseText = `Based on your **${role}** target role audit, your overall skill coverage is **${mentorContext?.skillGaps?.overallCoverage || 72}%**.\n\nYour top critical skill gaps identified by our diagnostic engine are:\n\n- 🔴 **${topGap1}** (Critical - Required for Tier-1 SDE-1 high-throughput endpoints)\n- 🟡 **${topGap2}** (High - Appears in 40% of MAANG / Unicorn screening rounds)\n- 🟡 **${topGap3}** (High - Cloud microservices evidence)\n\nClosing **${topGap1}** will boost your System Architecture score by **+15%**.`;

          actions = [
            { label: "View Skill Gaps", route: "/skill-gaps" },
            { label: "Add to Roadmap", route: "/roadmap" }
          ];
        }
        // 3. Placement Readiness & Overall Progress
        else if (query.includes("readiness") || query.includes("how am i doing") || query.includes("progress") || query.includes("status") || query.includes("score")) {
          responseText = `Here is your real-time candidate readiness breakdown for **${role}**:\n\n- 🎯 **Overall Readiness**: **${score}/100** (${mentorContext?.readiness?.status || 'Strong Tier-1 Prospect'})\n- 🧩 **LeetCode**: **${solved} Solved** (${mentorContext?.leetcode?.rankTitle || 'Knight'} Rank, ${mentorContext?.leetcode?.contestRating || 1842} Rating)\n- 💻 **GitHub Impact**: **${githubScore}/100** (${mentorContext?.github?.commits || 342} Commits, ${mentorContext?.github?.streakDays || 14}-day streak)\n- 📄 **ATS Resume**: **${ats}/100** (STAR bullet compliance)\n- 🗺️ **Roadmap Progress**: **${mentorContext?.roadmap?.completionPercent || 46}%** (Day ${day}/90)\n\nYour strongest vector is **Projects & Coding Velocity**, while **Redis Distributed Caching** is your highest-priority gap.`;

          actions = [
            { label: "Placement Readiness", route: "/placement-readiness" },
            { label: "View Progress", route: "/progress" }
          ];
        }
        // 4. Resume Improvement
        else if (query.includes("resume") || query.includes("ats") || query.includes("cv") || query.includes("bullet")) {
          responseText = `Your resume currently scores **${ats}/100** on ATS compliance.\n\nKey optimization recommendations:\n1. **Quantify impact**: Add explicit metric gains to your project bullet points (e.g. "*Engineered PlaceMentor AI REST backend with sub-200ms latency and high concurrency*").\n2. **Keyword alignment**: Ensure explicit mentions of **Redis**, **Kafka**, and **Docker** to pass automated Tier-1 ATS filters for ${role}.`;

          actions = [
            { label: "Review Resume", route: "/resume" },
            { label: "Review Projects", route: "/projects" }
          ];
        }
        // 5. GitHub & Projects
        else if (query.includes("github") || query.includes("git") || query.includes("project") || query.includes("repo") || query.includes("ast")) {
          responseText = `Your GitHub profile shows strong commit cadence:\n\n- 🌟 **Impact Score**: **${githubScore}/100** (Top 12% among peer candidates)\n- 🔥 **Active Streak**: **${mentorContext?.github?.streakDays || 14} days** with ${mentorContext?.github?.commits || 342} total commits\n- 📂 **Portfolio Projects**: **${mentorContext?.projects?.count || 4} audited projects** (Avg architectural score: ${mentorContext?.projects?.avgScore || 88}/100)\n\nTo raise your GitHub score above 90, consider adding containerization manifests (Docker Compose / Minikube) to your main repository.`;

          actions = [
            { label: "GitHub Intelligence", route: "/github" },
            { label: "Review Projects", route: "/projects" }
          ];
        }
        // 6. LeetCode / DSA / Kahn's Algo / Graph Questions
        else if (query.includes("kahn") || query.includes("topological") || query.includes("graph") || query.includes("dsa") || query.includes("dp") || query.includes("leetcode") || query.includes("hint")) {
          responseText = `Excellent question! Let's examine **Kahn's Topological Sort algorithm** for **LeetCode #210 (Course Schedule II)** with **O(V + E)** runtime complexity.\n\nIn Kahn's algorithm:\n1. We calculate the in-degree for all vertices.\n2. Add all vertices with \`inDegree == 0\` to a Queue.\n3. Poll nodes from queue, add to topological order, and decrement neighbor in-degrees.\n4. If count of processed nodes equals total vertices $V$, no cycle exists! If less than $V$, a cycle was detected.\n\nHere is the C++ cycle reconstruction DFS implementation for reference:`;

          codeSnippet = {
            filename: "cycle_reconstruction_dfs.cpp",
            language: "cpp",
            code: `// State 0: Unvisited, 1: Visiting (Gray), 2: Visited (Black)\nbool reconstructCycleDFS(int u, const vector<vector<int>>& adj, vector<int>& state, vector<int>& parent, vector<int>& cycle) {\n    state[u] = 1; // Mark Gray\n    for (int v : adj[u]) {\n        if (state[v] == 1) {\n            // Cycle found! Backtrack along parent chain\n            cycle.push_back(v);\n            for (int curr = u; curr != v; curr = parent[curr]) {\n                cycle.push_back(curr);\n            }\n            cycle.push_back(v);\n            reverse(cycle.begin(), cycle.end());\n            return true;\n        } else if (state[v] == 0) {\n            parent[v] = u;\n            if (reconstructCycleDFS(v, adj, state, parent, cycle)) return true;\n        }\n    }\n    state[u] = 2; // Mark Black\n    return false;\n}`
          };

          svgDiagram = true;

          checkpoint = {
            title: "Interactive Checkpoint:",
            subtitle: "Would you like to trace this on a 5-node graph or switch to a System Design Rate Limiter drill?",
            options: [
              { label: "Trace 5-Node Graph", prompt: "Trace Kahn's algorithm on a 5-node graph" },
              { label: "Switch to Rate Limiter", prompt: "Explain how to design a distributed Rate Limiter" }
            ]
          };

          actions = [
            { label: "Practice LeetCode", route: "/leetcode" },
            { label: "Start Mock Interview", route: "/mock-interview" }
          ];
        }
        // 7. Mock Interview / Behavioral / Technical Drills
        else if (query.includes("interview") || query.includes("mock") || query.includes("drill") || query.includes("behavioral") || query.includes("conflict")) {
          responseText = `During technical and behavioral interviews for **${role}** at Tier-1 companies:\n\n1. **Technical Framework**: Clarify constraints → State brute force time complexity → Derive optimal algorithm → Walk through dry-run with invariants.\n2. **Behavioral STAR Method**: Situation → Task → Action → Quantified Result.\n\nYour latest Mock Interview technical score was **${mentorContext?.interview?.technicalScore || 82}%**.`;

          actions = [
            { label: "Start Mock Interview", route: "/mock-interview" },
            { label: "Practice Communication", route: "/communication" }
          ];
        }
        // 8. Communication Coaching
        else if (query.includes("communication") || query.includes("speak") || query.includes("pitch") || query.includes("wpm")) {
          responseText = `Your verbal communication diagnostic score is **${mentorContext?.communication?.clarityScore || 82}%**.\n\n- ⏱️ **Speaking Pace**: **${mentorContext?.communication?.wpm || 145} WPM** (Optimal 130-160 WPM interview cadence)\n- 💡 **Tip**: When explaining architectural trade-offs, pause 1-2 seconds after stating scale throughput numbers for clarity.`;

          actions = [
            { label: "Practice Communication", route: "/communication" }
          ];
        }
        // 9. Persona-based General Fallback
        else {
          if (persona === 'dsa') {
            responseText = `As your **Socratic DSA Tutor**, I won't give away the solution directly! Let's analyze your problem structure:\n\n1. What are the constraints on input size $N$?\n2. Does the problem exhibit optimal substructure or overlapping subproblems?\n\nTell me your initial thought process, and we'll refine the time complexity together.`;
          } else if (persona === 'story') {
            responseText = `As your **STAR Storyteller & Behavioral Coach**, let's frame your response effectively:\n\n- **Situation**: Define the engineering context and urgency.\n- **Task**: State your specific ownership role.\n- **Action**: Explain the exact technical decision you engineered.\n- **Result**: Highlight quantified scale improvement (e.g. +35% latency boost).`;
          } else if (persona === 'strat') {
            responseText = `As your **Placement Strategist**, let's review your timeline strategy:\n\nYou are on **Day ${day} of 90** targeting **${role}** at ${mentorContext?.user?.targetCompany || 'Tier-1 Product Companies'}.\nMaintain a steady pace of 90 minutes daily commitment. Prioritize high-impact skill gaps like Redis Caching and 2D Dynamic Programming.`;
          } else {
            responseText = `As your **Senior Staff Technical Mentor**, I've logged your query into your candidate telemetry stream.\n\nTo tailor my feedback precisely for **${role}**, let me know if you want to focus on:\n1. **Algorithm Optimization** (Time/Space Complexity)\n2. **System Design & Microservices Architecture**\n3. **Mock Interview Drills**`;
          }

          actions = [
            { label: "View Today's Tasks", route: "/tasks" },
            { label: "Analyze Skill Gaps", route: "/skill-gaps" }
          ];
        }

        resolve({
          response: responseText,
          text: responseText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          verified: true,
          codeSnippet,
          svgDiagram,
          checkpoint,
          actions
        });
      }, 600);
    });
  },

  // Onboarding Mock AI Synthesis Functions
  analyzeStudentProfile: async (onboardingData) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const profile = onboardingData?.profile || {};
        const career = onboardingData?.career || {};
        const skills = onboardingData?.skills || {};
        const integrations = onboardingData?.integrations || {};
        const preferences = onboardingData?.preferences || {};
        const goals = onboardingData?.goals || {};

        const role = career.targetRole || 'Full Stack Engineer';
        const companyTier = career.companyTier || 'Tier-1 Product (MAANG / Unicorns)';
        const targetCtc = goals.targetCtc || '14 - 24 LPA (Product Tier)';
        const selectedTechList = skills.selectedSkills || [];

        // 1. Calculate dynamic baseline score across all 6 steps
        let score = 55;

        // Step 1: Academic Profile completeness (+10 max)
        if (profile.name && profile.college && profile.degree) score += 10;
        else if (profile.name) score += 5;

        // Step 2 & 3: Target Role vs Self-Reported Skill Levels (+15 max)
        if (skills.dsaLevel?.includes('Advanced')) score += 6;
        else if (skills.dsaLevel?.includes('Intermediate')) score += 4;
        else score += 2;

        if (skills.frameworkLevel?.includes('Advanced') || skills.sysDesignLevel?.includes('Advanced')) score += 5;
        else if (skills.frameworkLevel?.includes('Intermediate') || skills.sysDesignLevel?.includes('Intermediate')) score += 3;
        else score += 1;

        if (selectedTechList.length >= 5) score += 4;
        else if (selectedTechList.length >= 2) score += 2;

        // Step 4: Telemetry & Resume Integrations (+15 max)
        if (integrations.githubConnected || integrations.githubHandle) score += 5;
        if (integrations.leetcodeConnected || integrations.leetcodeHandle) score += 5;
        if (integrations.resumeUploaded || integrations.resumeFileName) score += 5;

        // Step 5 & 6: Commitment & Placement Goal alignment (+5 max)
        if (parseInt(preferences.dailyGoalMinutes || '0', 10) >= 90) score += 3;
        if (goals.targetDrive) score += 2;

        // Cap score logically between 62 and 94
        score = Math.min(94, Math.max(62, score));

        // 2. Synthesize Role & Skill-based Day 1 Roadmap Task
        let day1Task = 'LC 207: Course Schedule (Graph Cycle Detection)';
        const primarySkill = selectedTechList[0] || '';

        if (role.includes('AI/ML') || role.includes('Machine Learning')) {
          day1Task = `LC 207: Course Schedule & ${primarySkill || 'PyTorch'} Tensor Math`;
        } else if (role.includes('DevOps') || role.includes('Cloud') || role.includes('AWS')) {
          day1Task = `Docker Container Setup & LC 207 (Network Graph Routing)`;
        } else if (role.includes('Cybersecurity') || role.includes('Security')) {
          day1Task = `OWASP Security Audit & LC 207 (Dependency Graphs)`;
        } else if (role.includes('Data')) {
          day1Task = `SQL Query Optimization & LC 207 (DAG Pipeline Scheduling)`;
        } else {
          day1Task = `LC 207: Course Schedule & ${primarySkill || 'React/Node'} REST Integration`;
        }

        // 3. Generate Tailored Key AI Recommendations from ALL 6 STEPS
        const aiRecommendations = [];

        // Skill level gap recommendation (Step 3)
        const dsaLevelStr = skills.dsaLevel || 'Intermediate';
        if (dsaLevelStr.includes('Beginner')) {
          aiRecommendations.push(`Upgrade DSA mastery from Beginner to Intermediate with daily ${preferences.dailyGoalMinutes || 90}-min Graph & Tree problem sets.`);
        } else {
          aiRecommendations.push(`Calibrate ${dsaLevelStr.split('(')[0].trim()} DSA proficiency for ${companyTier.split('(')[0].trim()} technical screening rounds.`);
        }

        // Integration / Telemetry recommendation (Step 4)
        const missingIntegrations = [];
        if (!integrations.githubHandle) missingIntegrations.push('GitHub');
        if (!integrations.leetcodeHandle) missingIntegrations.push('LeetCode');
        if (!integrations.resumeUploaded && !integrations.resumeFileName) missingIntegrations.push('ATS Resume');

        if (missingIntegrations.length > 0) {
          aiRecommendations.push(`Connect remaining telemetry (${missingIntegrations.join(', ')}) in Settings for real-time AST code auditing & ATS scoring.`);
        } else {
          aiRecommendations.push(`Telemetry active: GitHub (@${integrations.githubHandle}), LeetCode (@${integrations.leetcodeHandle}), & ATS Resume synced for automated audits.`);
        }

        // Role Specialization recommendation (Step 2 & 3)
        const topSkillsStr = selectedTechList.slice(0, 3).join(', ') || 'Core Technologies';
        if (role.includes('AI/ML')) {
          aiRecommendations.push(`Construct production LLM / Neural Network pipeline using ${topSkillsStr} targeting ${targetCtc.split('(')[0].trim()} roles.`);
        } else if (role.includes('DevOps') || role.includes('Cloud')) {
          aiRecommendations.push(`Construct multi-stage Docker & Terraform IaC pipeline using ${topSkillsStr} for cloud infrastructure readiness.`);
        } else if (role.includes('Cybersecurity')) {
          aiRecommendations.push(`Execute hands-on Penetration Testing & SIEM logging drills with ${topSkillsStr} for security compliance.`);
        } else {
          aiRecommendations.push(`Engineer scalable REST microservices architecture using ${topSkillsStr} to meet ${companyTier.split('(')[0].trim()} expectations.`);
        }

        // Timeline & Cadence recommendation (Step 5 & 6)
        if (goals.targetDrive) {
          aiRecommendations.push(`Execute daily ${preferences.dailyGoalMinutes || 90}-min study cadence to peak before ${goals.targetDrive.split('(')[0].trim()} campus placement drives.`);
        }

        resolve({
          baselineScore: score,
          candidateName: profile.name || 'Candidate',
          college: profile.college || 'Engineering College',
          degree: profile.degree || 'Computer Science',
          graduationYear: profile.graduationYear || '2026',
          targetRole: role,
          secondaryRole: career.secondaryRole || '',
          targetTier: companyTier,
          targetCtc: targetCtc,
          targetDrive: goals.targetDrive || 'Upcoming Campus Phase',
          mentorTone: preferences.mentorTone || 'Socratic Coach (Probing Questions)',
          dailyCommitment: preferences.dailyGoalMinutes || '90',
          selectedSkills: selectedTechList,
          dsaLevel: skills.dsaLevel || 'Intermediate',
          githubHandle: integrations.githubHandle || '',
          leetcodeHandle: integrations.leetcodeHandle || '',
          resumeFileName: integrations.resumeFileName || '',
          day1RoadmapTask: day1Task,
          recommendedPhases: [
            { phase: 1, name: 'Core DSA & Foundations', duration: 'Days 1-30' },
            { phase: 2, name: `Advanced ${role.split(' ')[0]} Architecture`, duration: 'Days 31-60' },
            { phase: 3, name: 'Mock Interviews & Placement Polish', duration: 'Days 61-90' }
          ],
          aiRecommendations
        });
      }, 1200);
    });
  },

  generateInitialSkillAnalysis: async (skills) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          strengths: ['Spring Boot Microservices', 'Binary Search & Trees', 'SQL Database Tuning'],
          remediations: ['Redis Invalidation Patterns', 'Kafka Consumer Groups']
        });
      }, 600);
    });
  },

  generateInitialRoadmap: async (onboardingData) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          day1Task: 'Solve LC 207: Course Schedule (Graph Cycle Detection)',
          day1Category: 'DSA',
          duration: '45 mins'
        });
      }, 600);
    });
  }
};
