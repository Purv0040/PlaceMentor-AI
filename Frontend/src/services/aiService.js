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

  // Unified AI Mentor response generation automatically routing across technical, DSA, behavioral, and placement strategy
  generateMentorResponse: async (userMessage, mentorContext = null) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const query = typeof userMessage === 'string' ? userMessage.toLowerCase().trim() : '';
        const role = mentorContext?.user?.targetRole || null;
        const name = mentorContext?.user?.name || null;
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

        const roleText = role ? ` for **${role}**` : '';
        const greetingPrefix = name ? `Hello **${name}**!` : 'Hello!';

        // 0. Friendly Greeting (Brief & natural, avoiding repeating welcome or dumping capabilities)
        if (query === 'hi' || query === 'hello' || query === 'hey' || query.startsWith('hi ') || query.startsWith('hello ') || query.startsWith('hey ') || query === 'hi there' || query === 'greetings') {
          responseText = role
            ? `Hey there! How can I help with your ${role} preparation today?`
            : "Hey there! How can I help with your placement preparation today?";
          actions = [
            { label: "Help me learn DSA", route: "/leetcode" },
            { label: "Practice a technical interview", route: "/mock-interview" },
            { label: "Help me plan my preparation", route: "/roadmap" }
          ];
        }
        // 1. Technical Interview Practice (Explicit match)
        else if (query.includes("practice a technical interview") || query.includes("technical interview practice") || query.includes("practice interview")) {
          responseText = `Let's practice a technical interview question${roleText}!\n\n**Problem: Design an In-Memory Key-Value Store with TTL (Time-To-Live)**\n\n- **Requirements**:\n  1. \`set(key, value, ttl)\`: Store a key with an expiration timestamp in milliseconds.\n  2. \`get(key)\`: Return value if not expired, otherwise return \`null\`.\n  3. \`count()\`: Return the number of active, non-expired keys.\n\nBefore writing code, explain:\n1. What data structures would you use for $O(1)$ lookups and efficient expired key cleanup?\n2. How would you handle passive vs active cleanup of expired keys?\n\nShare your thought process and initial approach!`;
          actions = [
            { label: "Start Mock Interview", route: "/mock-interview" },
            { label: "Practice DSA", route: "/leetcode" }
          ];
        }
        // 2. Placement Strategy, Daily Planning & Tasks / Plan My Preparation
        else if (query.includes("today") || query.includes("task") || query.includes("schedule") || query.includes("work on") || query.includes("daily") || query.includes("plan") || query.includes("what can i do") || query.includes("what i can do")) {
          const firstTask = tasks[0]?.title || "Solve LC #210 (Course Schedule II)";
          const firstTaskCat = tasks[0]?.category || "DSA & Algorithms";
          const firstTaskDur = tasks[0]?.duration || "45 mins";

          responseText = `${greetingPrefix} Today is **Day ${day}** of your 90-Day Placement Roadmap${roleText}.\n\nYou have **${tasks.length || 2} pending tasks** scheduled for today:\n\n1. 📌 **${firstTask}** (${firstTaskCat}, ${firstTaskDur})\n${tasks[1] ? `2. 📌 **${tasks[1].title}** (${tasks[1].category})\n` : ''}\nCompleting the **${firstTaskCat}** task first directly addresses your preparation goals.`;

          actions = [
            { label: "View Today's Tasks", route: "/tasks" },
            { label: "Open 90-Day Roadmap", route: "/roadmap" }
          ];
        }
        // 3. Skill Gaps & Weakness Diagnosis
        else if (query.includes("gap") || query.includes("weakness") || query.includes("learn") || query.includes("improve skill") || query.includes("priority")) {
          const topGaps = mentorContext?.skillGaps?.topGaps || [];
          const topGap1 = topGaps[0]?.skill || "Redis Distributed Caching";
          const topGap2 = topGaps[1]?.skill || "Dynamic Programming (2D & Tree DP)";
          const topGap3 = topGaps[2]?.skill || "Kubernetes Orchestration";

          responseText = `Based on your diagnostic audit${roleText}, your overall skill coverage is **${mentorContext?.skillGaps?.overallCoverage || 72}%**.\n\nYour top critical skill gaps identified by our diagnostic engine are:\n\n- 🔴 **${topGap1}** (Critical - High-throughput systems)\n- 🟡 **${topGap2}** (High - Frequently tested in screening rounds)\n- 🟡 **${topGap3}** (High - Cloud microservices evidence)\n\nClosing **${topGap1}** will boost your System Architecture score by **+15%**.`;

          actions = [
            { label: "View Skill Gaps", route: "/skill-gaps" },
            { label: "Add to Roadmap", route: "/roadmap" }
          ];
        }
        // 4. Placement Readiness & Overall Progress
        else if (query.includes("readiness") || query.includes("how am i doing") || query.includes("progress") || query.includes("status") || query.includes("score")) {
          responseText = `Here is your real-time candidate readiness breakdown${roleText}:\n\n- 🎯 **Overall Readiness**: **${score}/100** (${mentorContext?.readiness?.status || 'Strong Tier-1 Prospect'})\n- 🧩 **LeetCode**: **${solved} Solved** (${mentorContext?.leetcode?.rankTitle || 'Knight'} Rank, ${mentorContext?.leetcode?.contestRating || 1842} Rating)\n- 💻 **GitHub Impact**: **${githubScore}/100** (${mentorContext?.github?.commits || 342} Commits, ${mentorContext?.github?.streakDays || 14}-day streak)\n- 📄 **ATS Resume**: **${ats}/100** (STAR bullet compliance)\n- 🗺️ **Roadmap Progress**: **${mentorContext?.roadmap?.completionPercent || 46}%** (Day ${day}/90)\n\nYour strongest vector is **Projects & Coding Velocity**, while **Redis Distributed Caching** is your highest-priority gap.`;

          actions = [
            { label: "Placement Readiness", route: "/placement-readiness" },
            { label: "90-Day Roadmap", route: "/roadmap" }
          ];
        }
        // 5. Resume & Profile Optimization
        else if (query.includes("resume") || query.includes("ats") || query.includes("cv") || query.includes("bullet")) {
          const roleKeywords = role ? ` for ${role}` : '';
          responseText = `Your resume currently scores **${ats}/100** on ATS compliance.\n\nKey optimization recommendations:\n1. **Quantify impact**: Add explicit metric gains to your project bullet points (e.g. "*Engineered PlaceMentor AI REST backend with sub-200ms latency and high concurrency*").\n2. **Keyword alignment**: Ensure explicit mentions of core technologies to pass automated ATS filters${roleKeywords}.`;

          actions = [
            { label: "Review Resume", route: "/resume" },
            { label: "Review Projects", route: "/projects" }
          ];
        }
        // 6. GitHub & Technical Projects
        else if (query.includes("github") || query.includes("git") || query.includes("project") || query.includes("repo") || query.includes("ast")) {
          responseText = `Your GitHub profile shows strong commit cadence:\n\n- 🌟 **Impact Score**: **${githubScore}/100** (Top 12% among peer candidates)\n- 🔥 **Active Streak**: **${mentorContext?.github?.streakDays || 14} days** with ${mentorContext?.github?.commits || 342} total commits\n- 📂 **Portfolio Projects**: **${mentorContext?.projects?.count || 4} audited projects** (Avg architectural score: ${mentorContext?.projects?.avgScore || 88}/100)\n\nTo raise your GitHub score above 90, consider adding containerization manifests (Docker Compose / Minikube) to your main repository.`;

          actions = [
            { label: "GitHub Intelligence", route: "/github" },
            { label: "Review Projects", route: "/projects" }
          ];
        }
        // 7. DSA Learning & Coding Help / Help Me Learn DSA
        else if (query.includes("kahn") || query.includes("topological") || query.includes("graph") || query.includes("dsa") || query.includes("dp") || query.includes("leetcode") || query.includes("hint") || query.includes("binary search") || query.includes("tree") || query.includes("array") || query.includes("complexity") || query.includes("algorithm")) {
          if (query.includes("kahn") || query.includes("topological")) {
            responseText = `Let's tackle this DSA problem! Examining **Kahn's Topological Sort algorithm** for **LeetCode #210 (Course Schedule II)** with **O(V + E)** runtime complexity:\n\nIn Kahn's algorithm:\n1. Compute the in-degree for all vertices.\n2. Add all vertices with \`inDegree == 0\` to a Queue.\n3. Poll nodes from queue, append to topological sequence, and decrement neighbor in-degrees.\n4. If the count of processed nodes equals total vertices $V$, no cycle exists! If less than $V$, a cycle was detected.\n\nHere is the C++ cycle reconstruction DFS implementation for reference:`;

            codeSnippet = {
              filename: "cycle_reconstruction_dfs.cpp",
              language: "cpp",
              code: `// State 0: Unvisited, 1: Visiting (Gray), 2: Visited (Black)\nbool reconstructCycleDFS(int u, const vector<vector<int>>& adj, vector<int>& state, vector<int>& parent, vector<int>& cycle) {\n    state[u] = 1; // Mark Gray\n    for (int v : adj[u]) {\n        if (state[v] == 1) {\n            // Cycle found! Backtrack along parent chain\n            cycle.push_back(v);\n            for (int curr = u; curr != v; curr = parent[curr]) {\n                cycle.push_back(curr);\n            }\n            cycle.push_back(v);\n            reverse(cycle.begin(), cycle.end());\n            return true;\n        } else if (state[v] == 0) {\n            parent[v] = u;\n            if (reconstructCycleDFS(v, adj, state, parent, cycle)) return true;\n        }\n    }\n    state[u] = 2; // Mark Black\n    return false;\n}`
            };

            svgDiagram = true;
          } else {
            responseText = `Here is your high-yield strategy to **learn and master DSA**${roleText}:\n\n1. **Core Patterns First**: Focus on patterns rather than memorizing questions (Sliding Window, Two Pointers, Monotonic Stack, BFS/DFS, Top-K Heap, DP).\n2. **Daily Consistency**: Practice 2 Medium-level problems daily on LeetCode.\n3. **Interview Habit**: Always state Time and Space complexity before writing code, and verify edge cases (empty inputs, single elements, negative values).\n\nWhich topic would you like to start with: Arrays & Hashing, Two Pointers, Trees, or Graphs?`;
          }

          actions = [
            { label: "Practice LeetCode", route: "/leetcode" },
            { label: "Start Mock Interview", route: "/mock-interview" }
          ];
        }
        // 8. HR & Behavioral Interview Preparation (STAR Method)
        else if (query.includes("behavioral") || query.includes("star") || query.includes("hr") || query.includes("conflict") || query.includes("leadership") || query.includes("tell me about") || query.includes("strength") || query.includes("culture")) {
          responseText = `For HR and behavioral rounds, always structure your responses using the **STAR Method**:\n\n- **S — Situation**: Set the engineering context in 1-2 sentences. What was the critical deadline, architecture constraint, or team challenge?\n- **T — Task**: Clearly articulate your direct responsibility. Avoid "we"—say *"I was responsible for optimizing the query latency."*\n- **A — Action**: Describe the specific engineering decision you executed. What tools, profiling benchmarks, or collaboration strategies did you apply?\n- **R — Result**: Quantify the outcome (e.g. *"-38% p99 latency drop, zero downtime migration, or project delivered 4 days ahead of campus drive deadline"*).\n\nWould you like to simulate a common question like *"Tell me about a time you had a technical disagreement with a team member"*?`;

          actions = [
            { label: "Communication Lab", route: "/communication" },
            { label: "Mock Interview", route: "/mock-interview" }
          ];
        }
        // 9. Technical Interview Preparation & System Design
        else if (query.includes("system design") || query.includes("architecture") || query.includes("rate limit") || query.includes("cache") || query.includes("microservice") || query.includes("database") || query.includes("sql") || query.includes("nosql") || query.includes("concurrency") || query.includes("interview")) {
          responseText = `When preparing for **Technical & System Design Interviews**${roleText}:\n\n1. **Requirements Clarification**: Scope Functional requirements (APIs, read/write ratios) and Non-Functional requirements (latency p99 < 50ms, 99.99% availability, CAP trade-offs).\n2. **Back-of-Envelope Math**: Calculate QPS (e.g., 10M daily active users * 10 reqs = 1,150 QPS write, 11,500 QPS read), storage/bandwidth estimates.\n3. **High-Level Design**: Client → DNS/CDN → API Gateway/Load Balancer → Stateless Application Cluster → Distributed Cache (Redis) → Primary/Replica DB.\n4. **Deep Dive Bottlenecks**: Single points of failure, partition tolerance, and message queuing (Kafka/RabbitMQ) for asynchronous processing.\n\nYour current Technical Interview readiness score is **${mentorContext?.interview?.technicalScore || 82}%**.`;

          actions = [
            { label: "Start Mock Interview", route: "/mock-interview" },
            { label: "Analyze Skill Gaps", route: "/skill-gaps" }
          ];
        }
        // 10. Verbal Communication & Delivery Coaching
        else if (query.includes("communication") || query.includes("speak") || query.includes("pitch") || query.includes("wpm")) {
          responseText = `Your verbal communication diagnostic score is **${mentorContext?.communication?.clarityScore || 82}%**.\n\n- ⏱️ **Speaking Pace**: **${mentorContext?.communication?.wpm || 145} WPM** (Optimal 130-160 WPM interview cadence)\n- 💡 **Tip**: When explaining architectural trade-offs, pause 1-2 seconds after stating scale throughput numbers for clarity.`;

          actions = [
            { label: "Practice Communication", route: "/communication" }
          ];
        }
        // 11. General Mentor Fallback (Answers according to user query, avoiding capability dumping)
        else {
          responseText = `Regarding **"${userMessage}"**${roleText}:\n\nI can help break down this topic, discuss key architectural and algorithmic trade-offs, and recommend targeted practice problems.\n\nWould you like an algorithmic code example, an architectural breakdown, or an interview-style practice question?`;

          actions = [
            { label: "Help me learn DSA", route: "/leetcode" },
            { label: "Practice a technical interview", route: "/mock-interview" },
            { label: "Help me plan my preparation", route: "/roadmap" }
          ];
        }

        resolve({
          response: responseText,
          text: responseText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          verified: false,
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

        // 1. Dynamic baseline score computation across all 6 onboarding steps (Target range: 32 - 96)
        let score = 0;

        // Step 1: Academic profile completeness (Max 8 pts)
        if (profile.name) score += 2;
        if (profile.college) score += 2;
        if (profile.degree) score += 2;
        if (profile.graduationYear) score += 2;

        // Step 3: Technical Skills Self-Assessment (Max 40 pts)
        // DSA Level (4 to 22 pts)
        const dsa = skills.dsaLevel || 'Intermediate';
        if (dsa.includes('Expert') || dsa.includes('Master')) score += 22;
        else if (dsa.includes('Advanced') || dsa.includes('Hard')) score += 17;
        else if (dsa.includes('Intermediate')) score += 11;
        else score += 5; // Beginner

        // System Design / Domain 2 (2 to 8 pts)
        const sys = skills.sysDesignLevel || 'Beginner';
        if (sys.includes('Advanced')) score += 8;
        else if (sys.includes('Intermediate')) score += 5;
        else score += 2;

        // Database / Domain 3 (2 to 6 pts)
        const db = skills.databaseLevel || 'Intermediate';
        if (db.includes('Advanced')) score += 6;
        else if (db.includes('Intermediate')) score += 4;
        else score += 2;

        // Framework / Domain 4 (2 to 6 pts)
        const fw = skills.frameworkLevel || 'Intermediate';
        if (fw.includes('Advanced')) score += 6;
        else if (fw.includes('Intermediate')) score += 4;
        else score += 2;

        // Step 2: Role-Specific Competency Fit (Max 16 pts, Min -12 pts)
        const roleCompetencyMap = {
          'AI/ML': ['python', 'pytorch', 'tensorflow', 'machine learning', 'deep learning', 'scikit-learn', 'pandas', 'numpy', 'mlops', 'llm', 'opencv', 'keras', 'nlp'],
          'Cybersecurity': ['networking', 'linux', 'siem', 'threat detection', 'penetration testing', 'owasp', 'cryptography', 'security', 'wireshark', 'soc', 'firewall'],
          'DevOps': ['aws', 'docker', 'kubernetes', 'ci/cd', 'terraform', 'linux', 'cloudwatch', 'jenkins', 'prometheus', 'ansible', 'cloud', 'git'],
          'Full Stack': ['react', 'node.js', 'javascript', 'typescript', 'mongodb', 'express', 'html/css', 'sql', 'next.js', 'postgresql', 'tailwind', 'redux', 'git'],
          'Backend': ['python', 'fastapi', 'java', 'sql', 'postgresql', 'system design', 'docker', 'rest api', 'redis', 'c++', 'spring boot', 'microservices', 'git']
        };

        const targetRoleKey = Object.keys(roleCompetencyMap).find(k =>
          role.toLowerCase().includes(k.toLowerCase())
        );
        const requiredCompetencies = targetRoleKey ? roleCompetencyMap[targetRoleKey] : ['python', 'data structures', 'sql', 'git'];

        const matchedCount = selectedTechList.filter(sk => {
          const s = String(sk).toLowerCase();
          return requiredCompetencies.some(req => s.includes(req) || req.includes(s));
        }).length;

        if (matchedCount >= 4) {
          score += 15;
        } else if (matchedCount >= 2) {
          score += 10;
        } else if (matchedCount === 1) {
          score += 4;
        } else {
          // Zero skills matching chosen target role -> major penalty!
          score -= 10;
        }

        // Selected Skills Breadth bonus (Max 4 pts)
        if (selectedTechList.length >= 6) score += 4;
        else if (selectedTechList.length >= 3) score += 2;

        // Step 4: Telemetry & Integrations (Max 16 pts)
        const cleanGh = (integrations.githubHandle || '').trim();
        const cleanLc = (integrations.leetcodeHandle || '').trim();
        const hasResume = !!(integrations.resumeUploaded || integrations.resumeFileName);

        if (integrations.githubConnected || cleanGh) score += 5;
        if (integrations.leetcodeConnected || cleanLc) score += 5;
        if (hasResume) score += 6;

        // Step 5: Study Hours Commitment (Max 10 pts)
        const mins = parseInt(preferences.dailyGoalMinutes || '90', 10);
        if (mins >= 180) score += 10;
        else if (mins >= 120) score += 7;
        else if (mins >= 90) score += 5;
        else if (mins >= 45) score += 3;
        else score += 1;

        // Step 2 & 6: Target Ambition vs Current Skill Alignment (Tier benchmark factor & calibration)
        if (companyTier.includes('IT Services') || companyTier.includes('Campus Recruiters')) {
          score += 12; // Accessible baseline
          if (dsa.includes('Intermediate') || dsa.includes('Advanced')) score += 4;
        } else if (companyTier.includes('Tier-2') || companyTier.includes('Mid-Size')) {
          score += 6;
          if (dsa.includes('Beginner')) score -= 6;
          else if (dsa.includes('Advanced') || dsa.includes('Expert')) score += 5;
        } else {
          // Tier-1 Product / MAANG (High threshold)
          if (dsa.includes('Beginner')) score -= 16;
          else if (dsa.includes('Intermediate')) score -= 5;
          else if (dsa.includes('Advanced') || dsa.includes('Expert')) score += 8;

          if (sys.includes('Beginner')) score -= 4;
        }

        // Clamp dynamically between 32 and 96
        score = Math.min(96, Math.max(32, Math.round(score)));

        // 2. Synthesize Role & Skill-based Day 1 Roadmap Task
        let day1Task = 'LC 207: Course Schedule (Graph Cycle Detection)';
        const primarySkill = selectedTechList[0] || '';

        if (role.includes('AI/ML') || role.includes('Machine Learning')) {
          day1Task = `LC 207: Course Schedule & ${primarySkill || 'PyTorch'} Neural Math`;
        } else if (role.includes('DevOps') || role.includes('Cloud') || role.includes('AWS')) {
          day1Task = `Docker Container Setup & LC 207 (Network Graph Routing)`;
        } else if (role.includes('Cybersecurity') || role.includes('Security')) {
          day1Task = `OWASP Security Audit & LC 207 (Dependency Graphs)`;
        } else if (role.includes('Data')) {
          day1Task = `SQL Query Optimization & LC 207 (DAG Pipeline Scheduling)`;
        } else {
          day1Task = `LC 207: Course Schedule & ${primarySkill || 'Python'} REST Services`;
        }

        // 3. Generate Tailored Key AI Recommendations from ALL 6 STEPS
        const aiRecommendations = [];

        // Bullet 1: Skill level gap & tier calibration (Step 2 & 3)
        const dsaLevelStr = skills.dsaLevel || 'Intermediate';
        const tierName = companyTier.split('(')[0].trim();
        if (dsaLevelStr.includes('Beginner')) {
          aiRecommendations.push(`Upgrade DSA mastery from Beginner to Intermediate with daily ${preferences.dailyGoalMinutes || 90}-min Graph & Tree problem sets.`);
        } else if (dsaLevelStr.includes('Advanced') || dsaLevelStr.includes('Hard')) {
          aiRecommendations.push(`Calibrate Advanced DSA proficiency for ${tierName} technical screening rounds.`);
        } else {
          aiRecommendations.push(`Calibrate ${dsaLevelStr.split('(')[0].trim()} DSA proficiency for ${tierName} technical screening rounds.`);
        }

        // Bullet 2: Telemetry & Integrations (Step 4)
        const cleanGhHandle = (integrations.githubHandle || '')
          .replace(/^https?:\/\/(www\.)?github\.com\//i, '')
          .replace(/^@/, '')
          .replace(/\/.*$/, '')
          .trim();
        const cleanLcHandle = (integrations.leetcodeHandle || '')
          .replace(/^https?:\/\/(www\.)?leetcode\.com\/(u\/)?/i, '')
          .replace(/^@/, '')
          .replace(/\/.*$/, '')
          .trim();
        const gh = cleanGhHandle ? `@${cleanGhHandle}` : 'Connected';
        const lc = cleanLcHandle ? `@${cleanLcHandle}` : 'Connected';
        if (cleanGhHandle || cleanLcHandle || integrations.resumeUploaded || integrations.resumeFileName) {
          aiRecommendations.push(`Telemetry active: GitHub (${gh}), LeetCode (${lc}), & ATS Resume synced for automated audits.`);
        } else {
          aiRecommendations.push(`Telemetry active: GitHub, LeetCode, and ATS Resume ready for automated pipeline synchronization.`);
        }

        // Bullet 3: Role & Architecture using user's actual selected skills (Step 2, 3, 6)
        const topSkillsList = selectedTechList.length > 0
          ? selectedTechList.slice(0, 3).join(', ')
          : 'Python, Java, Data Structures';
        
        if (role.includes('AI/ML')) {
          aiRecommendations.push(`Construct production LLM & neural network pipelines using ${topSkillsList} to meet ${tierName} expectations.`);
        } else if (role.includes('DevOps') || role.includes('Cloud')) {
          aiRecommendations.push(`Construct multi-stage Docker & Terraform IaC infrastructure using ${topSkillsList} for ${tierName} cloud readiness.`);
        } else if (role.includes('Cybersecurity')) {
          aiRecommendations.push(`Execute hands-on Penetration Testing & SIEM logging drills with ${topSkillsList} to meet ${tierName} security standards.`);
        } else {
          aiRecommendations.push(`Engineer scalable REST microservices architecture using ${topSkillsList} to meet ${tierName} expectations.`);
        }

        // Bullet 4: Timeline & Study Cadence (Step 5 & 6)
        const driveStr = goals.targetDrive ? goals.targetDrive.split('(')[0].trim() : 'August 2026';
        const cadenceMinutes = preferences.dailyGoalMinutes || '45';
        aiRecommendations.push(`Execute daily ${cadenceMinutes}-min study cadence to peak before ${driveStr} campus placement drives.`);

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
  },

  generateMentorResponse: async (userMessage, mentorContext) => {
    return {
      text: `Regarding "${userMessage}": I'm here to help guide your placement roadmap, DSA practice, resume, and interview prep. Check your Today's Tasks to stay on track!`,
      verified: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actions: [
        { label: "What can I do today?", route: "/tasks" },
        { label: "How many days are remaining?", route: "/roadmap" }
      ]
    };
  }
};
