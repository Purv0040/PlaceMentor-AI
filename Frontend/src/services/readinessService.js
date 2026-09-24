// Readiness Service aggregating Phase 5 preparation metrics into 7-vector readiness scores

import { initialReadinessData } from "../data/readinessData";
import { initialResumeData } from "../data/resumeData";
import { initialGithubData } from "../data/githubData";
import { initialLeetcodeData } from "../data/leetcodeData";
import { getStoredProjects } from "../data/projectData";

export const readinessService = {
  calculateReadiness: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const projects = getStoredProjects();
        const avgProjectScore = projects.length > 0
          ? Math.round(projects.reduce((sum, p) => sum + (p.score || 85), 0) / projects.length)
          : 85;

        const resumeScore = initialResumeData.metrics.atsScore || 84;
        const githubScore = initialGithubData.metrics.githubImpactScore || 82;
        const leetcodeScore = initialLeetcodeData.metrics.readinessScore || 79;
        
        // Holistic weighted score calculation
        const weightedOverall = Math.round(
          (84 * 0.25) + // DSA
          (76 * 0.20) + // Sys Design
          (avgProjectScore * 0.20) + // Projects
          (82 * 0.15) + // CS Fund
          (resumeScore * 0.10) + // Resume
          (leetcodeScore * 0.05) + // LeetCode
          (75 * 0.05)   // Soft Skills
        );

        resolve({
          ...initialReadinessData,
          overallScore: weightedOverall,
          dimensionsSummary: [
            {
              id: "dim-resume",
              name: "Resume Intelligence",
              score: resumeScore,
              status: "ATS Verified",
              route: "/resume",
              detail: `${resumeScore}/100 · STAR format bullet compliance verified`
            },
            {
              id: "dim-github",
              name: "GitHub Intelligence",
              score: githubScore,
              status: "Production Grade",
              route: "/github",
              detail: `${githubScore}/100 · ${initialGithubData.metrics.totalCommits} commits, ${initialGithubData.metrics.activeStreakDays}-day streak`
            },
            {
              id: "dim-leetcode",
              name: "LeetCode Intelligence",
              score: leetcodeScore,
              status: `${initialLeetcodeData.metrics.rankTitle} Rank (${initialLeetcodeData.metrics.contestRating})`,
              route: "/leetcode",
              detail: `${initialLeetcodeData.metrics.totalSolved} solved · Contest Rating ${initialLeetcodeData.metrics.contestRating}`
            },
            {
              id: "dim-projects",
              name: "Project Intelligence",
              score: avgProjectScore,
              status: "System Architect",
              route: "/projects",
              detail: `${avgProjectScore}/100 · ${projects.length} portfolio projects audited`
            },
          ]
        });
      }, 400);
    });
  }
};
