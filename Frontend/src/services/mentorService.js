// Centralized Mentor Service to build normalized student context and handle conversation persistence

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

    const targetRole = user?.targetRole || onboardingData?.career?.targetRole || 'Backend Developer';
    const targetCompany = onboardingData?.career?.companyTier || 'Tier-1 Product (MAANG / Unicorns)';
    const candidateName = user?.name || onboardingData?.profile?.name || 'Alex Patel';

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

  // Retrieve stored conversation from localStorage
  getStoredChat: () => {
    try {
      const saved = localStorage.getItem(CHAT_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (e) {
      console.error('Failed to parse mentor chat from localStorage', e);
    }
    return null;
  },

  // Save conversation array to localStorage
  saveChat: (messages) => {
    try {
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.error('Failed to save mentor chat to localStorage', e);
    }
  },

  // Clear conversation state and localStorage
  clearChat: () => {
    try {
      localStorage.removeItem(CHAT_STORAGE_KEY);
    } catch (e) {
      console.error('Failed to clear mentor chat localStorage', e);
    }
  },

  // Generate initial greeting message tailored to student context
  getInitialGreeting: (context) => {
    const name = context.user.name || 'Candidate';
    const role = context.user.targetRole || 'Backend Developer';
    const day = context.roadmap.currentDay || 42;
    const pendingCount = context.todayTasks.remaining || 2;
    const topTask = context.todayTasks.pendingTaskList?.[0]?.title || "LeetCode #210 (Course Schedule II)";

    return [
      {
        id: 'msg-init-1',
        sender: 'ai',
        role: 'assistant',
        persona: 'tech',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        verified: true,
        text: `Hello **${name}**! I am your AI Placement Copilot. I've audited your current candidate telemetry for **${role}**.\n\nToday is **Day ${day}** of your 90-Day Roadmap. You have **${pendingCount} pending tasks** scheduled for today, starting with "*${topTask}*".\n\nHow would you like to proceed? We can review graph algorithm edge cases, analyze your skill gaps, or practice system design trade-offs.`,
        codeSnippet: null,
        checkpoint: {
          title: "Interactive Checkpoint:",
          subtitle: "Would you like to trace Kahn's Topological Sort on a 5-node graph or review your Redis Caching gap?",
          options: [
            { label: "Trace 5-Node Graph", prompt: "Explain Kahn's Topological Sort algorithm step by step" },
            { label: "Review Skill Gaps", prompt: "What are my biggest skill gaps?" }
          ]
        },
        actions: [
          { label: "View Today's Tasks", route: "/tasks" },
          { label: "Analyze Skill Gaps", route: "/skill-gaps" }
        ]
      }
    ];
  },

  // Main wrapper for response generation
  generateMentorResponse: async (userMessage, mentorContext, persona = 'tech') => {
    return await aiService.generateMentorResponse(userMessage, mentorContext, persona);
  }
};
