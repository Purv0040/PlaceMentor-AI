// Readiness Service aggregating real Backend API endpoints with local fallback support

import { apiRequest } from "./api";
import { initialReadinessData } from "../data/readinessData";

function transformBackendReadiness(backendData) {
  if (!backendData) return initialReadinessData;

  const cats = backendData.categories || {};
  const strengths = backendData.strengths || [];
  const priorityGaps = backendData.key_gaps || backendData.priority_gaps || [];
  const recommendations = backendData.recommendations || [];
  const roleAlignment = backendData.role_alignment || {};
  const staleData = backendData.stale_data || [];

  const overallScore = Math.round(backendData.overall_score || 0);

  // Vector scores for UI progress list
  const categoryMap = [
    { key: "dsa_leetcode", name: "DSA & LeetCode", target: 85, defaultScore: 75, weight: "20%" },
    { key: "projects", name: "Project Architecture", target: 80, defaultScore: 70, weight: "20%" },
    { key: "resume", name: "Resume & ATS Integrity", target: 85, defaultScore: 80, weight: "15%" },
    { key: "cs_fundamentals", name: "CS Fundamentals", target: 75, defaultScore: 65, weight: "15%" },
    { key: "github", name: "GitHub Impact & Code", target: 80, defaultScore: 70, weight: "10%" },
    { key: "communication", name: "Communication Skills", target: 75, defaultScore: 60, weight: "10%" },
    { key: "interview", name: "Mock Technical Interview", target: 75, defaultScore: 60, weight: "10%" },
  ];

  const vectorScores = categoryMap.map((meta) => {
    const c = cats[meta.key];
    const s = c && c.status === "scored" ? c.score : meta.defaultScore;
    const st = c ? (c.status === "scored" ? (s >= meta.target ? "Strong" : "Developing") : "Insufficient Data") : "Pending";
    return {
      name: meta.name,
      score: s,
      target: meta.target,
      weight: meta.weight,
      status: st
    };
  });

  // Radar chart data structure
  const radarData = vectorScores.map((v) => ({
    vector: v.name,
    Score: v.score,
    Benchmark: v.target
  }));

  // Preparation dimensions cards
  const dimensionsSummary = [
    {
      id: "dim-resume",
      name: "Resume Intelligence",
      score: cats.resume?.score || 80,
      status: cats.resume?.status === "scored" ? "ATS Audited" : "Data Pending",
      route: "/resume",
      detail: cats.resume?.evidence?.[0] || `${cats.resume?.score || 80}/100 · Resume structure evaluated`
    },
    {
      id: "dim-github",
      name: "GitHub Intelligence",
      score: cats.github?.score || 75,
      status: cats.github?.status === "scored" ? "Activity Synced" : "Data Pending",
      route: "/github",
      detail: cats.github?.evidence?.[0] || `${cats.github?.score || 75}/100 · Repository footprint verified`
    },
    {
      id: "dim-leetcode",
      name: "LeetCode Intelligence",
      score: cats.dsa_leetcode?.score || 78,
      status: cats.dsa_leetcode?.status === "scored" ? "Problem Metrics Synced" : "Data Pending",
      route: "/leetcode",
      detail: cats.dsa_leetcode?.evidence?.[0] || `${cats.dsa_leetcode?.score || 78}/100 · Problem solving index verified`
    },
    {
      id: "dim-projects",
      name: "Project Intelligence",
      score: cats.projects?.score || 75,
      status: cats.projects?.status === "scored" ? "Portfolio Audited" : "Data Pending",
      route: "/projects",
      detail: cats.projects?.evidence?.[0] || `${cats.projects?.score || 75}/100 · Code quality & features evaluated`
    }
  ];

  // Map AI priority recommendations
  const priorityRemediations = recommendations.map((rec, idx) => ({
    id: `rec-${idx}`,
    vector: rec.category ? rec.category.toUpperCase() : "HIGH IMPACT",
    priority: rec.priority || "High",
    title: rec.action || rec.title || "Remediation Task",
    description: rec.detail || rec.description || rec.impact || "",
    actionRoute: rec.category === "resume" ? "/resume" : rec.category === "dsa_leetcode" ? "/leetcode" : rec.category === "projects" ? "/projects" : rec.category === "github" ? "/github" : "/tasks",
    actionLabel: "Execute Remediation →"
  }));

  const defaultRemediations = initialReadinessData.priorityRemediations;

  return {
    ...initialReadinessData,
    id: backendData.id,
    overallScore,
    scoreStatus: backendData.readiness_label || "Developing",
    lastSynced: backendData.updated_at ? new Date(backendData.updated_at).toLocaleString() : "Just now",
    targetBenchmark: backendData.target_role || "Backend Developer",
    confidenceIndex: `${Math.round((backendData.overall_confidence || 0.8) * 100)}%`,
    percentileRank: `Top ${Math.max(5, 100 - overallScore)}% Candidate Cohort`,
    radarData,
    vectorScores,
    dimensionsSummary,
    priorityRemediations: priorityRemediations.length > 0 ? priorityRemediations : defaultRemediations,
    strengths,
    priorityGaps,
    roleAlignment,
    staleData
  };
}

export const readinessService = {
  getLatestReadiness: async () => {
    const res = await apiRequest('/readiness');
    if (res && res.status === 'success' && res.data) {
      return transformBackendReadiness(res.data);
    }
    return transformBackendReadiness(null);
  },

  calculateReadiness: async () => {
    const res = await apiRequest('/readiness/analyze', {
      method: 'POST',
      body: JSON.stringify({})
    });
    if (res && res.status === 'success' && res.data) {
      return transformBackendReadiness(res.data);
    }
    return readinessService.getLatestReadiness();
  },

  getSummary: async () => {
    const res = await apiRequest('/readiness/summary');
    if (res && res.status === 'success' && res.data) {
      return res.data;
    }
    return null;
  },

  getHistory: async () => {
    const res = await apiRequest('/readiness/history');
    if (res && res.status === 'success' && res.data) {
      return res.data;
    }
    return [];
  }
};
