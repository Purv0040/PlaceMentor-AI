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
        currentDay: roadmap?.currentDay || 42,
        totalDays: roadmap?.totalDays || 90,
        currentPhase: roadmap?.currentPhaseName || 'Phase 2: Advanced Microservices & System Design',
        completionPercent: roadmap?.completionPercentage || 46,
        lastAdapted: roadmap?.lastAdapted || 'Today (AI Calibrated)'
      },
      todayTasks: {
        total: tasks.length,
        completed: tasks.filter(t => t.completed).length,
        remaining: tasks.filter(t => !t.completed).length,
        pendingTaskList: tasks.filter(t => !t.completed).map(t => ({
          id: t.id,
          title: t.title,
          category: t.category,
          duration: t.duration,
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

  askMentor: async (message, conversationId = null, targetRole = null, studentName = null) => {
    try {
      return await apiRequest('/mentor/ask', {
        method: 'POST',
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          target_role: targetRole,
          student_name: studentName
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

  generateMentorResponse: async (userMessage, mentorContext) => {
    // Try real backend API first with current student context
    const targetRole = mentorContext?.user?.targetRole || null;
    const studentName = mentorContext?.user?.name || null;
    const apiRes = await mentorService.askMentor(userMessage, null, targetRole, studentName);
    if (apiRes && apiRes.answer) {
      return {
        text: apiRes.answer,
        verified: apiRes.verified === true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actions: (apiRes.suggested_actions || []).map(a => ({
          label: a.label || a.title || "View Details",
          route: a.route || "/dashboard"
        }))
      };
    }
    // Fallback to local AI service synthesizer if backend offline
    return await aiService.generateMentorResponse(userMessage, mentorContext);
  }
};
