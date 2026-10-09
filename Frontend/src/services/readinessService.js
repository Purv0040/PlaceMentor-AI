// Centralized Readiness Service connecting to v2.0 deterministic readiness endpoints

import { apiRequest } from "./api";
import { initialReadinessData } from "../data/readinessData";

export function transformBackendReadiness(backendData) {
  if (!backendData) return initialReadinessData;

  const cats = backendData.categories || {};
  const strengths = backendData.strengths || [];
  const priorityGaps = backendData.key_gaps || backendData.priority_gaps || [];
  const recommendations = backendData.recommendations || [];
  const roleAlignment = backendData.role_alignment || {};
  const staleData = backendData.stale_data || [];

  const overallScore = backendData.overall_score !== null && backendData.overall_score !== undefined
    ? Math.round(backendData.overall_score)
    : 0;

  // 7-Vector Diagnostic Configuration matching Backend v2.0 Contract
  const categoryConfigs = [
    { key: "Resume", altKey: "resume", name: "Resume Intelligence", target: 85, defaultWeight: "15%", route: "/resume" },
    { key: "DSA", altKey: "dsa", name: "DSA & Problem Solving", target: 85, defaultWeight: "20%", route: "/leetcode" },
    { key: "Projects", altKey: "projects", name: "Project Architecture", target: 80, defaultWeight: "20%", route: "/projects" },
    { key: "GitHub", altKey: "github", name: "GitHub Impact & Code", target: 80, defaultWeight: "10%", route: "/github" },
    { key: "CS Fundamentals", altKey: "cs_fundamentals", name: "CS Fundamentals", target: 75, defaultWeight: "15%", route: "/tasks" },
    { key: "Communication", altKey: "communication", name: "Communication Skills", target: 75, defaultWeight: "10%", route: "/communication" },
    { key: "Interview", altKey: "interview", name: "Mock Technical Interview", target: 75, defaultWeight: "10%", route: "/interviews" },
  ];

  const vectorScores = categoryConfigs.map((cfg) => {
    const cat = cats[cfg.key] || cats[cfg.altKey] || {};
    const hasScore = cat.score !== null && cat.score !== undefined;
    const score = hasScore ? Math.round(cat.score) : 0;
    
    // Status formatting
    let statusLabel = "Not Assessed";
    if (cat.status === "assessed" || cat.status === "scored") {
      statusLabel = score >= cfg.target ? "Strong" : "Assessed";
    } else if (cat.status === "provisional") {
      statusLabel = "Provisional";
    } else if (cat.status === "stale") {
      statusLabel = "Stale Evidence";
    }

    const weightPercent = cat.weight ? `${Math.round(cat.weight * 100)}%` : cfg.defaultWeight;

    return {
      name: cfg.name,
      key: cfg.key,
      score: score,
      hasScore,
      target: cfg.target,
      weight: weightPercent,
      status: statusLabel,
      rawStatus: cat.status || "not_assessed",
      confidence: cat.confidence || 0.0,
      reason: cat.reason || (hasScore ? `${score}/100 based on verified evidence` : "No evidence submitted yet"),
      rubricDetail: cat.rubric_detail || "",
      evidence: cat.evidence || [],
      missingData: cat.missing_data || [],
      recommendations: cat.recommendations || [],
      route: cfg.route
    };
  });

  // Radar chart data structure
  const radarData = vectorScores.map((v) => ({
    vector: v.name,
    Score: v.hasScore ? v.score : 0,
    Benchmark: v.target
  }));

  // Preparation dimensions cards
  const dimensionsSummary = [
    {
      id: "dim-resume",
      name: "Resume Intelligence",
      score: cats.Resume?.score ?? cats.resume?.score ?? null,
      status: cats.Resume?.status ?? cats.resume?.status ?? "not_assessed",
      route: "/resume",
      detail: (cats.Resume || cats.resume)?.evidence?.[0] || "ATS structure and keywords evaluated"
    },
    {
      id: "dim-dsa",
      name: "LeetCode & DSA",
      score: cats.DSA?.score ?? cats.dsa?.score ?? null,
      status: cats.DSA?.status ?? cats.dsa?.status ?? "not_assessed",
      route: "/leetcode",
      detail: (cats.DSA || cats.dsa)?.evidence?.[0] || "Algorithmic problem solving verified"
    },
    {
      id: "dim-projects",
      name: "Project Intelligence",
      score: cats.Projects?.score ?? cats.projects?.score ?? null,
      status: cats.Projects?.status ?? cats.projects?.status ?? "not_assessed",
      route: "/projects",
      detail: (cats.Projects || cats.projects)?.evidence?.[0] || "Code complexity and deployment checked"
    },
    {
      id: "dim-github",
      name: "GitHub Intelligence",
      score: cats.GitHub?.score ?? cats.github?.score ?? null,
      status: cats.GitHub?.status ?? cats.github?.status ?? "not_assessed",
      route: "/github",
      detail: (cats.GitHub || cats.github)?.evidence?.[0] || "Repository depth and stars synced"
    }
  ];

  // Actionable recommendations mapping
  const priorityRemediations = recommendations.map((recText, idx) => {
    let recCategory = "HIGH IMPACT";
    let actionRoute = "/tasks";

    const lower = typeof recText === "string" ? recText.toLowerCase() : "";
    if (lower.includes("resume") || lower.includes("ats")) {
      recCategory = "RESUME";
      actionRoute = "/resume";
    } else if (lower.includes("leetcode") || lower.includes("dsa") || lower.includes("graph") || lower.includes("hard")) {
      recCategory = "DSA";
      actionRoute = "/leetcode";
    } else if (lower.includes("project") || lower.includes("deploy") || lower.includes("readme")) {
      recCategory = "PROJECTS";
      actionRoute = "/projects";
    } else if (lower.includes("github") || lower.includes("commit") || lower.includes("repository")) {
      recCategory = "GITHUB";
      actionRoute = "/github";
    } else if (lower.includes("communication") || lower.includes("speaking") || lower.includes("star")) {
      recCategory = "COMMUNICATION";
      actionRoute = "/communication";
    } else if (lower.includes("mock") || lower.includes("interview")) {
      recCategory = "INTERVIEWS";
      actionRoute = "/interviews";
    }

    return {
      id: `rec-${idx}`,
      vector: recCategory,
      priority: idx === 0 ? "Critical" : "High",
      title: typeof recText === "string" ? recText : "Placement Remediation Task",
      description: typeof recText === "string" ? recText : "",
      actionRoute,
      actionLabel: "Execute Remediation →"
    };
  });

  return {
    ...initialReadinessData,
    id: backendData.id,
    overallScore,
    previousScore: backendData.previous_score,
    scoreDelta: backendData.score_delta,
    coveragePercentage: backendData.coverage_percentage ?? 0,
    readinessStatus: backendData.readiness_status || "assessed",
    scoreStatus: backendData.readiness_label || "Developing",
    lastSynced: backendData.updated_at ? new Date(backendData.updated_at).toLocaleString() : "Just now",
    targetBenchmark: backendData.target_role || "Software Engineer",
    confidenceIndex: `${Math.round((backendData.overall_confidence || 0.8) * 100)}%`,
    percentileRank: `Top ${Math.max(5, 100 - overallScore)}% Candidate Cohort`,
    radarData,
    vectorScores,
    dimensionsSummary,
    priorityRemediations: priorityRemediations.length > 0 ? priorityRemediations : initialReadinessData.priorityRemediations,
    strengths,
    priorityGaps,
    roleAlignment,
    staleData,
    calculationVersion: backendData.calculation_version || "2.0"
  };
}

export const readinessService = {
  getLatestReadiness: async () => {
    const res = await apiRequest('/readiness');
    if (res && (res.success || res.status === 'success') && res.data) {
      return transformBackendReadiness(res.data);
    }
    return transformBackendReadiness(null);
  },

  calculateReadiness: async (targetRoleOverride = null) => {
    const body = targetRoleOverride ? { target_role: targetRoleOverride } : {};
    const res = await apiRequest('/readiness/analyze', {
      method: 'POST',
      body: JSON.stringify(body)
    });
    if (res && (res.success || res.status === 'success') && res.data) {
      return transformBackendReadiness(res.data);
    }
    return readinessService.getLatestReadiness();
  },

  getSummary: async () => {
    const res = await apiRequest('/readiness/summary');
    if (res && (res.success || res.status === 'success') && res.data) {
      return res.data;
    }
    return null;
  },

  getHistory: async (limit = 10) => {
    const res = await apiRequest(`/readiness/history?limit=${limit}`);
    if (res && (res.success || res.status === 'success') && res.data) {
      return res.data;
    }
    return [];
  }
};
