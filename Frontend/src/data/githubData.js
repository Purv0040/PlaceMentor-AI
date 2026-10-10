// Initial default state for GitHub Intelligence
export const initialGithubData = {
  isConnected: false,
  handle: "",
  profileUrl: "https://github.com",
  lastSynced: "Never",
  
  metrics: {
    githubImpactScore: 0,
    scorePercentile: "",
    totalCommits: 0,
    activeStreakDays: 0,
    longestStreakDays: 0,
    repoQualityIndex: 0,
    languageCount: 0,
    reposAnalyzedCount: 0,
    starsEarned: 0
  },

  languages: [],
  weeklyCadence: [],
  repositories: [],
  aiInsights: [],
  impactBreakdown: null,
  strengths: [],
  improvements: []
};
