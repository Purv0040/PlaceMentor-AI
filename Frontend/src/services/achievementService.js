// Achievement Service deriving dynamic completion stats from existing application state

import { defaultAchievements } from '../data/achievementData';
import { initialResumeData } from '../data/resumeData';
import { initialGithubData } from '../data/githubData';
import { initialLeetcodeData } from '../data/leetcodeData';
import { getStoredProjects } from '../data/projectData';
import { defaultInterviewHistory } from '../data/interviewData';
import { defaultCommunicationHistory } from '../data/communicationData';

const ACHIEVEMENTS_STORAGE_KEY = 'placementCopilotAchievements';
const DAILY_XP_KEY = 'placementCopilotDailyXpClaimedDate';

export const achievementService = {
  // Derive achievements dynamically based on real state
  getAchievements: (planningState = null) => {
    const projects = getStoredProjects();
    const tasks = planningState?.tasks || [];
    const roadmap = planningState?.roadmap || {};
    const progress = planningState?.progress || {};

    const completedTasksCount = tasks.filter(t => t.completed).length;
    const currentDay = roadmap?.currentDay || 42;
    const atsScore = initialResumeData?.metrics?.atsScore || 84;
    const totalSolved = initialLeetcodeData?.metrics?.totalSolved || 385;
    const totalCommits = initialGithubData?.metrics?.totalCommits || 342;
    const overallReadiness = progress?.overallProgressPercent || 78;
    const interviewScore = defaultInterviewHistory?.[0]?.score || 82;
    const communicationScore = defaultCommunicationHistory?.[0]?.verbalClarity || 82;

    return defaultAchievements.map(ach => {
      let currentCount = ach.currentCount;
      let unlocked = ach.unlocked;

      if (ach.id === 'ach-1') {
        currentCount = Math.max(14, initialGithubData?.metrics?.activeStreakDays || 14);
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-2') {
        currentCount = atsScore;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-3') {
        currentCount = totalSolved;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-4') {
        currentCount = totalCommits;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-5') {
        currentCount = projects.length;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-6') {
        currentCount = overallReadiness;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-8') {
        currentCount = interviewScore;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-9') {
        currentCount = communicationScore;
        unlocked = currentCount >= ach.requiredCount;
      } else if (ach.id === 'ach-12') {
        currentCount = currentDay;
        unlocked = currentCount >= ach.requiredCount;
      }

      return {
        ...ach,
        currentCount,
        unlocked
      };
    });
  },

  // Calculate summary stats (level, total XP, unlocked count)
  getStats: (achievementsList) => {
    const unlockedCount = achievementsList.filter(a => a.unlocked).length;
    const totalCount = achievementsList.length;
    const earnedXp = achievementsList.filter(a => a.unlocked).reduce((sum, a) => sum + a.xp, 0);
    const totalXp = 3000;
    const level = Math.floor(earnedXp / 300) + 1;
    const levelTitle = level >= 8 ? 'Consistent Builder' : level >= 5 ? 'Active Competitor' : 'Initiate';
    const xpInCurrentLevel = earnedXp % 300;
    const xpRemaining = 300 - xpInCurrentLevel;

    return {
      unlockedCount,
      totalCount,
      earnedXp,
      totalXp,
      level,
      levelTitle,
      xpInCurrentLevel,
      xpRemaining,
      completionPercentage: Math.round((unlockedCount / totalCount) * 100)
    };
  },

  // Daily XP Claim status
  isDailyXpClaimed: () => {
    try {
      const today = new Date().toDateString();
      const savedDate = localStorage.getItem(DAILY_XP_KEY);
      return savedDate === today;
    } catch (e) {
      return false;
    }
  },

  claimDailyXp: () => {
    try {
      const today = new Date().toDateString();
      localStorage.setItem(DAILY_XP_KEY, today);
      return true;
    } catch (e) {
      return false;
    }
  }
};
