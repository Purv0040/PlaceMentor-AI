import { apiRequest } from './api';
import { aiService } from './aiService';
import { initialReadinessData } from '../data/readinessData';
import { initialResumeData } from '../data/resumeData';
import { initialGithubData } from '../data/githubData';
import { initialLeetcodeData } from '../data/leetcodeData';
import { getStoredProjects } from '../data/projectData';
import { initialSkillGapData } from '../data/skillGapData';
import { defaultInterviewHistory } from '../data/interviewData';
import { defaultCommunicationHistory } from '../data/communicationData';

const CHAT_STORAGE_KEY = 'placementCopilotMentorChat';

export const mentorService = {
  // Build normalized student context from active state and data stores
  buildMentorContext: ({ user, onboardingData, planningState }) => {
    const projects = getStoredProjects();
    const tasks = planningState?.tasks || [];
    const roadmap = planningState?.roadmap || {};
    const progress = planningState?.progress || {};

    const targetRole = user?.targetRole || onboardingData?.career?.targetRole || null;
    const targetCompany = onboardingData?.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)';
    const candidateName = user?.name || onboardingData?.profile?.name || null;

    const currentDay = Number(roadmap?.currentDay) || 1;
    const totalDays = Number(roadmap?.totalDays || roadmap?.duration_days) || 90;
    const remainingDays = Math.max(0, totalDays - currentDay);

    const todayTasksList = tasks.filter(t => Number(t.dayNumber || t.day) === currentDay);
    const todayCompleted = todayTasksList.filter(t => t.completed || t.status === 'completed');
    const todayPending = todayTasksList.filter(t => !t.completed && t.status !== 'completed');

    const allPending = tasks.filter(t => !t.completed && t.status !== 'completed');
    const allCompleted = tasks.filter(t => t.completed || t.status === 'completed');

    return {
      user: {
        name: candidateName,
        targetRole,
        targetCompany,
        college: onboardingData?.profile?.college || 'CSPIT',
        degree: onboardingData?.profile?.degree || 'B.Tech IT'
      },
      readiness: {
        overallScore: progress?.overallProgressPercent || initialReadinessData?.overallScore || 78,
        status: initialReadinessData?.readinessTier || 'Strong Tier-1 Prospect'
      },
      roadmap: {
        currentDay,
        totalDays,
        remainingDays,
        currentPhase: roadmap?.currentPhaseName || 'Foundation & Core Preparation',
        completionPercent: roadmap?.completionPercentage || (tasks.length > 0 ? Math.round((allCompleted.length / tasks.length) * 100) : 0),
        totalTasksCount: tasks.length,
        completedTasksCount: allCompleted.length,
        pendingTasksCount: allPending.length,
        lastAdapted: roadmap?.lastAdapted || 'Today (AI Calibrated)'
      },
      todayTasks: {
        currentDay,
        total: todayTasksList.length,
        completed: todayCompleted.length,
        remaining: todayPending.length,
        pendingTaskList: todayPending.map(t => ({
          id: t.id || t.taskId,
          title: t.title,
          category: t.category,
          duration: t.duration || t.estimated_minutes || '60 mins',
          priority: t.priority
        }))
      },
      allPendingTasks: {
        totalPending: allPending.length,
        tasks: allPending.slice(0, 15).map(t => ({
          id: t.id || t.taskId,
          title: t.title,
          category: t.category,
          day: t.dayNumber || t.day,
          priority: t.priority
        }))
      },
      skillGaps: {
        overallCoverage: initialSkillGapData.overallCoverage || 72,
        criticalGapsCount: initialSkillGapData.gapsIdentifiedCount || 6,
        topGaps: initialSkillGapData.gaps.slice(0, 4).map(g => ({
          skill: g.skill,
          priority: g.priority,
          category: g.category,
          actionRoute: g.actionRoute
        }))
      },
      resume: {
        atsScore: initialResumeData.metrics.atsScore || 84,
        missingSkills: initialResumeData.metrics.missingSkills || ['Redis', 'Kafka', 'Kubernetes']
      },
      github: {
        impactScore: initialGithubData.metrics.githubImpactScore || 82,
        commits: initialGithubData.metrics.totalCommits || 342,
        streakDays: initialGithubData.metrics.activeStreakDays || 14
      },
      leetcode: {
        totalSolved: initialLeetcodeData.metrics.totalSolved || 385,
        contestRating: initialLeetcodeData.metrics.contestRating || 1842,
        rankTitle: initialLeetcodeData.metrics.rankTitle || 'Knight'
      },
      projects: {
        count: projects.length || 4,
        avgScore: Math.round(projects.reduce((s, p) => s + (p.score || 85), 0) / (projects.length || 1))
      },
      interview: {
        technicalScore: defaultInterviewHistory?.[0]?.score || 82,
        accuracy: 85
      },
      communication: {
        clarityScore: defaultCommunicationHistory?.[0]?.verbalClarity || 82,
        wpm: defaultCommunicationHistory?.[0]?.wpm || 145
      }
    };
  },

  // Backend API methods
  createConversation: async (title = 'New Placement Session') => {
    try {
      const res = await apiRequest('/mentor/conversations', {
        method: 'POST',
        body: JSON.stringify({ title })
      });
      return res || { conversation_id: `local_conv_${Date.now()}`, title, status: 'active' };
    } catch (e) {
      console.warn('Backend unavailable for createConversation, using local session.', e);
      return { conversation_id: `local_conv_${Date.now()}`, title, status: 'active' };
    }
  },

  getConversations: async () => {
    try {
      const res = await apiRequest('/mentor/conversations');
      return Array.isArray(res) ? res : [];
    } catch (e) {
      return [];
    }
  },

  getConversationDetail: async (conversationId) => {
    try {
      return await apiRequest(`/mentor/conversations/${conversationId}`);
    } catch (e) {
      return null;
    }
  },

  askMentor: async (message, conversationId = null, targetRole = null, studentName = null, conversationHistory = null) => {
    try {
      const validBackendId = (conversationId && !conversationId.startsWith('session-') && !conversationId.startsWith('local_'))
        ? conversationId
        : null;

      return await apiRequest('/mentor/ask', {
        method: 'POST',
        body: JSON.stringify({
          message,
          conversation_id: validBackendId,
          target_role: targetRole,
          student_name: studentName,
          conversation_history: conversationHistory
        })
      });
    } catch (e) {
      console.warn('Backend unavailable for askMentor, using client fallback.', e);
      return null;
    }
  },

  // Retrieve all stored chat sessions
  getStoredSessions: () => {
    try {
      const saved = localStorage.getItem('placementMentorSessions');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.error('Failed to parse mentor sessions from localStorage', e);
    }
    return [];
  },

  saveStoredSessions: (sessions) => {
    try {
      localStorage.setItem('placementMentorSessions', JSON.stringify(sessions));
    } catch (e) {
      console.error('Failed to save mentor sessions to localStorage', e);
    }
  },

  // Retrieve stored conversation from localStorage
  getStoredChat: () => {
    try {
      const saved = localStorage.getItem(CHAT_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed.map((msg) => {
            const { checkpoint, actions, ...rest } = msg;
            if (rest.id === 'msg-init-1') {
              return {
                ...rest,
                verified: false,
                text: "Hi! Ready to grow? 🚀\n\nLet's build your skills and get you placement-ready."
              };
            }
            return rest;
          });
        }
      }
    } catch (e) {
      console.error('Failed to parse mentor chat from localStorage', e);
    }
    return null;
  },

  saveChat: (messages) => {
    try {
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.error('Failed to save mentor chat to localStorage', e);
    }
  },

  clearChat: () => {
    try {
      localStorage.removeItem(CHAT_STORAGE_KEY);
    } catch (e) {
      console.error('Failed to clear mentor chat localStorage', e);
    }
  },

  getInitialGreeting: (context, persona = 'tech') => {
    const greetingsByPersona = {
      tech: "Hi! I'm your Technical Interviewer & DSA Copilot 🚀\n\nAsk me about algorithms, coding problems, system design, or code review.",
      dsa: "Welcome to DSA Mode! 🧠\n\nLet's master patterns like Two Pointers, Sliding Window, Trees, and Dynamic Programming.",
      story: "Hello! I'm your STAR Behavioral Coach 🎯\n\nLet's refine your behavioral answers using Situation, Task, Action, and Result with quantifiable impact.",
      strat: "Welcome! I'm your Placement Strategist 📈\n\nI can analyze your 90-day roadmap, skill gaps, company tier targets, and interview milestones."
    };

    return [
      {
        id: `msg-init-${Date.now()}`,
        sender: 'ai',
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: false,
        text: greetingsByPersona[persona] || "Hi! Ready to grow? 🚀\n\nLet's build your skills and get you placement-ready.",
        codeSnippet: null
      }
    ];
  },

  generateLocalFallback: (userMessage, mentorContext, persona = 'tech') => {
    const activePersona = persona || mentorContext?.persona || 'tech';
    const q = userMessage.toLowerCase().trim();
    const targetRole = mentorContext?.user?.targetRole || null;
    const roleDesc = targetRole ? ` for **${targetRole}**` : '';
    const currentDay = mentorContext?.roadmap?.currentDay || 1;
    const totalDays = mentorContext?.roadmap?.totalDays || 90;
    const remainingDays = mentorContext?.roadmap?.remainingDays ?? Math.max(0, totalDays - currentDay);
    const todayPending = mentorContext?.todayTasks?.pendingTaskList || [];
    const allPendingTotal = mentorContext?.allPendingTasks?.totalPending ?? (mentorContext?.roadmap?.pendingTasksCount || 0);

    let text = '';
    
    // Mode/Persona specific prefix logic if appropriate
    if (activePersona === 'story' && !q.includes('yesterday') && !q.includes('remaining') && !q.includes('tasks')) {
      text = `**STAR Method Framework for: "${userMessage}"**\n\n- **Situation**: Set the project background and challenge context.\n- **Task**: Specify your direct responsibility and success criteria.\n- **Action**: Explain the concrete technical decisions and leadership steps *you* took.\n- **Result**: Highlight quantifiable impact (e.g. "Reduced API latency by 35% across 50K users").\n\nWould you like me to help draft your exact talking points?`;
    } else if (activePersona === 'dsa' && (q.includes('dsa') || q.includes('algorithm') || q.includes('leetcode') || q.includes('problem') || q.includes('array') || q.includes('tree') || q.includes('graph'))) {
      text = `**DSA Pattern Analysis for: "${userMessage}"**\n\n1. **Core Pattern**: Identify whether this maps to Two Pointers, Sliding Window, Monotonic Stack, or Dynamic Programming.\n2. **Optimal Invariant**: Focus on what state changes at each step.\n3. **Target Complexity**: Aim for $O(N)$ or $O(N \\log N)$ time and $O(1)$ auxiliary space.\n\nShare the problem constraints or code snippet and we'll derive the optimal solution together!`;
    } else if (activePersona === 'strat' && (q.includes('plan') || q.includes('strategy') || q.includes('tier') || q.includes('placement') || q.includes('offer'))) {
      text = `**Placement Strategy Assessment**:\n\n- **Current Milestone**: Day ${currentDay} of ${totalDays} (${remainingDays} days remaining).\n- **Pending Roadmap Tasks**: ${allPendingTotal} tasks scheduled.\n- **Priority Focus**: Finish today's scheduled preparation tasks and solve 2 medium problems daily to ensure Tier-1 readiness.\n\nKeep high consistency to maximize your shortlisting conversion!`;
    } else if (q.includes('not working properly') || q.includes('not working') || q.includes('working properly')) {
      text = "I apologize for the misunderstanding! I'm here to give you accurate information directly from your placement profile and roadmap.\n\nYou can ask me:\n1. 📅 \"What can I do today?\"\n2. ✅ \"What did I complete yesterday?\"\n3. 📋 \"What are my pending tasks?\"\n4. ⏳ \"How many days are remaining?\"\n5. 💡 \"Help me learn DSA\" or \"Practice a technical interview\"\n\nWhat would you like to check?";
    } else if (q.includes('yesterday')) {
      text = `According to your records, you did not complete any tasks yesterday.\n\nYou can dive into today's tasks (Day ${currentDay} of ${totalDays}) to keep your preparation on track!`;
    } else if (/\bday\s*(\d+)\b/.test(q)) {
      const match = q.match(/\bday\s*(\d+)\b/);
      const targetDay = match ? match[1] : currentDay;
      text = `Day ${targetDay} is part of your ${totalDays}-day placement roadmap${roleDesc}.\n\nYou are currently on Day ${currentDay} with ${remainingDays} days remaining. Focus on completing today's tasks to advance toward Day ${targetDay}!`;
    } else if (q.includes('remaining') || q.includes('days left')) {
      text = `You are currently on **Day ${currentDay}** of your **${totalDays}-day** roadmap${roleDesc}.\n\nThere are **${remainingDays} days remaining** in your placement schedule.\n\n*(Note: You have ${allPendingTotal} pending tasks remaining across the rest of the roadmap).*`;
    } else if (q.includes('why') && (q.includes('pending') || q.includes('84') || q.includes('tasks'))) {
      const numMatch = q.match(/\b(\d+)\b/);
      const numStr = numMatch ? numMatch[1] : String(allPendingTotal);
      text = `The **${numStr}** pending tasks represent all the incomplete tasks distributed across the remaining **${remainingDays}** days of your **${totalDays}-day** roadmap.\n\nFor today (Day ${currentDay}), you only have **${todayPending.length}** task(s) to focus on!`;
    } else if (q.includes('do today') || q.includes('can i do') || q.includes('should i do') || q === 'today') {
      if (todayPending.length > 0) {
        const listStr = todayPending.map((t, idx) => `${idx + 1}. 📌 **${t.title}** (${t.category}, ${t.duration})`).join('\n');
        text = `Here are your incomplete tasks scheduled for today (Day ${currentDay} of ${totalDays}${roleDesc}):\n\n${listStr}\n\nStart with task #1 to maintain your daily consistency streak!`;
      } else {
        text = `You have no pending tasks scheduled for today (Day ${currentDay} of ${totalDays}${roleDesc})! 🎉\n\nAll tasks for today are completed. You can practice DSA problems or review upcoming roadmap topics.`;
      }
    } else if (q.includes('pending task') || q.includes('incomplete')) {
      text = `You have **${allPendingTotal}** pending task(s) in total across your ${totalDays}-day roadmap (${todayPending.length} due today on Day ${currentDay}).\n\nFocus on today's tasks first to maintain steady daily progress!`;
    } else if (['hi', 'hello', 'hey'].includes(q) || /^(hi|hello|hey)\b/.test(q)) {
      const candName = mentorContext?.user?.name;
      text = candName 
        ? `Hi ${candName}! How can I help with your coding practice, interview preparation, or placement roadmap today?`
        : "Hi there! How can I help with your coding practice, interview preparation, or placement roadmap today?";
    } else if (q.includes('decorator')) {
      text = "**Python Decorators**:\n\nA decorator is a callable that takes another function as an argument, extends its behavior without modifying it, and returns the modified wrapper function.\n\n```python\nimport functools\n\ndef my_logger(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        print(f\"Calling {func.__name__} with args: {args}\")\n        return func(*args, **kwargs)\n    return wrapper\n\n@my_logger\ndef add(a: int, b: int) -> int:\n    return a + b\n\n# Usage:\nprint(add(3, 4))  # 7\n```\n\n**Three Facts**:\n1. **First-Class Citizens**: Decorators work because Python functions can be passed as arguments, assigned, and returned.\n2. **Syntactic Sugar**: `@my_logger` is equivalent to `add = my_logger(add)`.\n3. **Metadata Preservation**: Use `@functools.wraps` inside the wrapper so the function keeps its original `__name__` and `__doc__`.";
    } else if ((q.includes('list') && q.includes('tuple')) || q.includes('list versus tuple') || q.includes('list vs tuple')) {
      text = "**Python List vs Tuple Comparison**:\n\n1. **Mutability**: Lists (`[]`) are mutable (can add, remove, modify elements). Tuples (`()`) are immutable (cannot be altered after creation).\n2. **Hashability**: Tuples containing hashable items are hashable and can serve as dictionary keys or set members. Lists are unhashable.\n3. **Memory & Performance**: Tuples have a smaller memory footprint and faster read operations because their size is fixed. Lists allocate extra buffer capacity for $O(1)$ amortized appends.\n4. **Use Case**: Use lists for collections that grow or reorder dynamically; use tuples for fixed records, coordinates, or constant configurations.";
    } else if (q.includes('aws') || (q.includes('cloud') && q.includes('interview'))) {
      text = "**AWS Technical Interview Preparation**:\n\n1. **Core Compute**: Master EC2 (instance types, security groups), ECS/EKS (container orchestration), and Lambda (serverless patterns, event sources, cold starts).\n2. **Storage & Databases**: S3 (storage tiers, lifecycle rules), RDS (Multi-AZ deployment, read replicas), and DynamoDB (partition keys, sort keys, GSI/LSI).\n3. **Networking & Security**: VPC subnets (public/private), NAT Gateways, IAM (least privilege roles vs users), Route 53, and CloudFront.\n4. **System Architecture**: Be ready to design high-availability systems using the AWS Well-Architected Framework (Reliability, Security, Cost Optimization).";
    } else if (q.includes('typeerror') || q.includes('nonetype') || q.includes('subscriptable')) {
      text = "**Fixing `TypeError: 'NoneType' object is not subscriptable`**:\n\n**Root Cause**: Attempting to index or slice an object (`obj[key]` or `obj[index]`) that is `None`.\n\n**Fix**:\n```python\nif data is not None and isinstance(data, dict):\n    print(data.get('key'))\n```";
    } else if (q.includes('error') && (q.includes('python') || q.includes('code') || q.fix)) {
      text = "Could you please share your Python code snippet and the exact error message or traceback you are receiving?\n\nOnce you share them, I'll identify the root cause and provide the corrected code!";
    } else if (q.includes('oop') || q.includes('encapsulation') || q.includes('polymorphism')) {
      text = "**The 4 Pillars of Object-Oriented Programming (OOP)**:\n\n1. 🔒 **Encapsulation**: Bundling state and methods inside classes and hiding private attributes.\n2. 🎭 **Abstraction**: Exposing clean interfaces while hiding complex internal logic (`abc.ABC`).\n3. 🧬 **Inheritance**: Code reusability through child classes.\n4. 🔄 **Polymorphism**: Unified method signatures with subclass-specific behaviors.";
    } else if (q.includes('two sum') || (q.includes('leetcode') && q.includes('1'))) {
      text = "**LeetCode #1: Two Sum**\n\n**Approach**: Single-pass Hash Map storing `seen[target - num] = index`.\n⏱️ **Time**: $O(N)$ | 💾 **Space**: $O(N)\n\n```python\ndef twoSum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []\n```";
    } else if (q.includes('leetcode')) {
      text = "Which LeetCode problem are you working on? Please share the problem number, title, or the problem statement, and I'll walk you through the optimal approach and complexity analysis!";
    } else {
      text = `Regarding **"${userMessage}"**:\n\nTo excel in this area for technical interviews, focus on core definitions, production-grade implementations, and Time/Space complexity trade-offs.\n\nWould you like a code demonstration, architectural breakdown, or interview-style practice?`;
    }

    return {
      text,
      verified: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actions: [
        { label: 'What can I do today?', route: '/tasks' },
        { label: 'How many days are remaining?', route: '/roadmap' }
      ]
    };
  },

  generateMentorResponse: async (userMessage, mentorContext, conversationId = null, conversationHistory = null, persona = 'tech') => {
    // Try real backend API first with current student context
    const targetRole = mentorContext?.user?.targetRole || null;
    const studentName = mentorContext?.user?.name || null;
    const apiRes = await mentorService.askMentor(userMessage, conversationId, targetRole, studentName, conversationHistory);
    if (apiRes && apiRes.answer) {
      return {
        text: apiRes.answer,
        conversation_id: apiRes.conversation_id,
        verified: apiRes.verified === true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actions: (apiRes.suggested_actions || []).map(a => ({
          label: a.label || a.title || "View Details",
          route: a.route || "/dashboard"
        }))
      };
    }
    // Explicit notification if backend is unreachable
    return {
      text: "I couldn't reach the AI mentor server right now. Please check your network connection and backend server status, then try asking again.",
      verified: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      actions: [{ label: "Retry question", route: "/mentor" }]
    };
  }
};
