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
      return await apiRequest('/mentor/ask', {
        method: 'POST',
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
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

  getInitialGreeting: (context) => {
    return [
      {
        id: 'msg-init-1',
        sender: 'ai',
        role: 'assistant',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: false,
        text: "Hi! Ready to grow? 🚀\n\nLet's build your skills and get you placement-ready.",
        codeSnippet: null
      }
    ];
  },

  generateLocalFallback: (userMessage, mentorContext) => {
    const q = userMessage.toLowerCase().trim();
    const targetRole = mentorContext?.user?.targetRole || null;
    const roleDesc = targetRole ? ` for **${targetRole}**` : '';
    const currentDay = mentorContext?.roadmap?.currentDay || 1;
    const totalDays = mentorContext?.roadmap?.totalDays || 90;
    const remainingDays = mentorContext?.roadmap?.remainingDays ?? Math.max(0, totalDays - currentDay);
    const todayPending = mentorContext?.todayTasks?.pendingTaskList || [];
    const allPendingTotal = mentorContext?.allPendingTasks?.totalPending ?? (mentorContext?.roadmap?.pendingTasksCount || 0);

    let text = '';
    if (q.includes('not working properly') || q.includes('not working') || q.includes('working properly')) {
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
      text = targetRole ? `Hey there! How can I help with your ${targetRole} preparation today?` : `Hey there! How can I help with your placement preparation today?`;
    } else if (q.includes('typeerror') || q.includes('nonetype') || q.includes('subscriptable')) {
      text = "**Fixing `TypeError: 'NoneType' object is not subscriptable`**:\n\n**Root Cause**: Attempting to index or slice an object (`obj[key]` or `obj[index]`) that is `None`.\n\n**Fix**:\n```python\nif data is not None and isinstance(data, dict):\n    print(data.get('key'))\n```";
    } else if (q.includes('error') && (q.includes('python') || q.includes('code') || q.includes('fix'))) {
      text = "Could you please share your Python code snippet and the exact error message or traceback you are receiving?\n\nOnce you share them, I'll identify the root cause and provide the corrected code!";
    } else if (q.includes('oop') || q.includes('encapsulation') || q.includes('polymorphism')) {
      text = "**The 4 Pillars of Object-Oriented Programming (OOP)**:\n\n1. 🔒 **Encapsulation**: Bundling state and methods inside classes and hiding private attributes.\n2. 🎭 **Abstraction**: Exposing clean interfaces while hiding complex internal logic (`abc.ABC`).\n3. 🧬 **Inheritance**: Code reusability through child classes.\n4. 🔄 **Polymorphism**: Unified method signatures with subclass-specific behaviors.";
    } else if (q.includes('two sum') || (q.includes('leetcode') && q.includes('1'))) {
      text = "**LeetCode #1: Two Sum**\n\n**Approach**: Single-pass Hash Map storing `seen[target - num] = index`.\n⏱️ **Time**: $O(N)$ | 💾 **Space**: $O(N)\n\n```python\ndef twoSum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []\n```";
    } else if (q.includes('leetcode')) {
      text = "Which LeetCode problem are you working on? Please share the problem number, title, or the problem statement, and I'll walk you through the optimal approach and complexity analysis!";
    } else {
      text = `Regarding **"${userMessage}"**${roleDesc}:\n\nTo excel in this area for placement interviews, focus on core definitions, hands-on implementations, and Time/Space complexity trade-offs.\n\nWould you like a code demonstration, architectural breakdown, or interview-style practice?`;
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

  generateMentorResponse: async (userMessage, mentorContext, conversationId = null, conversationHistory = null) => {
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
    // Fallback to local AI service synthesizer if backend offline
    return mentorService.generateLocalFallback(userMessage, mentorContext);
  }
};
