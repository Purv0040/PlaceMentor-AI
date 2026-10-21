// Skill Gap Service connecting Frontend UI to real Backend API endpoints with dynamic role calibration

import { apiRequest } from "./api";
import { initialSkillGapData, getRoleSkillGapData, COMMON_CATEGORIES } from "../data/skillGapData";

export function transformBackendSkillGaps(backendData, targetRole = null, userContext = null) {
  const roleFallback = getRoleSkillGapData(targetRole || backendData?.target_role, userContext);
  if (!backendData) return roleFallback;

  const priorityGaps = backendData.priority_gaps || [];
  const matrix2x2 = backendData.matrix2x2 || {};
  const backendCategoryCoverage = backendData.category_coverage || [];

  // Map priority gaps to UI expected format with explicit scope tagging
  const mappedGaps = priorityGaps.map((g, idx) => {
    const category = g.category || roleFallback.gaps[idx % roleFallback.gaps.length]?.category || "Core Competency";
    const isCommon = g.scope === "common" || COMMON_CATEGORIES.has(category);
    return {
      id: g.id || `gap-${idx + 1}`,
      skill: g.skill,
      category,
      scope: isCommon ? "common" : "role",
      currentLevel: g.current_level === "Advanced" ? 4 : g.current_level === "Intermediate" ? 3 : g.current_level === "Beginner" ? 2 : (g.current_level_num || 2),
      currentLevelText: g.current_level_text || `${g.current_level || 'Intermediate'} (Level ${g.current_level_num || 2}/4)`,
      requiredLevel: g.required_level === "Expert" ? 5 : g.required_level === "Advanced" ? 4 : g.required_level === "Intermediate" ? 3 : 3,
      requiredLevelText: g.required_level_text || `${g.required_level || 'Advanced'} (Level ${g.required_level_num || 3}/4)`,
      priority: g.priority || "High",
      reason: g.reason || `Essential benchmark competency for ${targetRole || backendData.target_role || 'target role'}.`,
      suggestedAction: g.suggested_action || "Advance proficiency via targeted projects and roadmap.",
      actionLabel: (g.action_label === "View Projects" || g.action_route === "/projects")
        ? "Add to Roadmap"
        : (g.action_label?.includes("LeetCode") || g.action_route === "/leetcode")
        ? "Start Practice Tasks"
        : (g.action_label || "Add to Roadmap"),
      actionRoute: (g.action_label === "View Projects" || g.action_route === "/projects")
        ? "/roadmap"
        : (g.action_label?.includes("LeetCode") || g.action_route === "/leetcode")
        ? "/tasks"
        : (g.action_route || "/roadmap")
    };
  });

function getCanonicalCategoryKey(name) {
  if (!name) return "other";
  const lower = name.toLowerCase().trim();
  if (lower.includes("machine learning") || lower.includes("deep learning") || lower.includes("neural")) return "machine learning";
  if (lower.includes("data science") || lower.includes("statistic") || lower.includes("analytics") || lower.includes("vector")) return "data science";
  if (lower.includes("algorithm") || lower.includes("dsa") || lower.includes("data structure")) return "dsa";
  if (lower.includes("database") || lower.includes("sql")) return "databases";
  if (lower.includes("devops") || lower.includes("mlops") || lower.includes("docker") || lower.includes("ci/cd") || lower.includes("kubernetes") || lower.includes("version control")) return "devops";
  if (lower.includes("program") || lower.includes("python") || lower.includes("java") || lower.includes("c++") || lower.includes("oop")) return "programming";
  if (lower.includes("backend") || lower.includes("api") || lower.includes("rest")) return "backend";
  if (lower.includes("frontend") || lower.includes("ui") || lower.includes("web") || lower.includes("html") || lower.includes("react")) return "frontend";
  if (lower.includes("security") || lower.includes("cyber") || lower.includes("threat")) return "security";
  if (lower.includes("cloud") || lower.includes("aws") || lower.includes("azure")) return "cloud";
  if (lower.includes("test") || lower.includes("qa") || lower.includes("quality")) return "testing";
  if (lower.includes("cs fundamental") || lower.includes("operating system") || lower.includes("network")) return "cs fundamentals";
  if (lower.includes("math")) return "mathematics";
  return lower;
}

function getCategoryDescription(catName, isCommon, targetRole) {
  const norm = getCanonicalCategoryKey(catName);
  switch (norm) {
    case "programming":
      return "Clean code, object-oriented design patterns, syntax, and memory model";
    case "machine learning":
      return "Supervised/unsupervised models, Scikit-learn, PyTorch, and deep neural architectures";
    case "data science":
      return "NumPy/Pandas vectorized math, statistical modeling, data visualization, and EDA";
    case "databases":
      return "Complex SQL queries, database indexing, schema design, and query optimization";
    case "devops":
      return "Docker containerization, Git branching workflows, CI/CD pipelines, and MLOps";
    case "dsa":
      return "Graphs, 2D Dynamic Programming, Trees, Greedy algorithms, and optimization";
    case "backend":
      return "RESTful APIs, microservices, async processing, and system architecture";
    case "frontend":
      return "Modern component architectures, state management, and responsive interfaces";
    case "security":
      return "Vulnerability assessment, network defense, SIEM, and cryptography";
    case "cloud":
      return "AWS/GCP infrastructure, IAM security, microservices, and serverless";
    case "testing":
      return "Unit testing, integration suites, Selenium automation, and CI test pipelines";
    case "cs fundamentals":
      return "Operating systems, computer networks, concurrency, and low-level design";
    case "mathematics":
      return "Linear algebra, calculus, probability theory, and optimization math";
    default:
      return isCommon
        ? "Universal engineering competency tested across all roles"
        : `Target role competency calibrated for ${targetRole || 'engineering'}`;
  }
}

  // Map category coverage: If backend measured evidence is available, that is our ground truth!
  // Enrich each backend category with role benchmark metadata and descriptions without duplication.
  const mergedCategories = [];

  if (backendCategoryCoverage && backendCategoryCoverage.length > 0) {
    // Collect fallback category metadata keyed by canonical key to preserve rich descriptions/colors
    const fallbackMetaMap = new Map();
    (roleFallback.categoryCoverage || []).forEach((fCat) => {
      const norm = getCanonicalCategoryKey(fCat.category);
      if (!fallbackMetaMap.has(norm)) {
        fallbackMetaMap.set(norm, fCat);
      }
    });

    const seenCanonicalKeys = new Set();

    backendCategoryCoverage.forEach((cat) => {
      const normKey = getCanonicalCategoryKey(cat.category);
      if (seenCanonicalKeys.has(normKey)) return;
      seenCanonicalKeys.add(normKey);

      const matchedFallback = fallbackMetaMap.get(normKey);
      const isCommon = cat.scope === "common" || (matchedFallback && matchedFallback.scope === "common") || COMMON_CATEGORIES.has(cat.category);
      const benchmarkTarget = cat.benchmark_target || cat.benchmarkTarget || (matchedFallback && matchedFallback.benchmarkTarget) || (isCommon ? 80 : 85);
      const cov = cat.coverage !== undefined ? cat.coverage : (matchedFallback ? matchedFallback.coverage : 0);
      const status = cat.status || (
        cov >= benchmarkTarget ? "Benchmark Met"
        : cov >= 40 ? "In Progress"
        : cov > 0 ? "Foundational"
        : "Remediation Needed"
      );

      const description = cat.description
        || (matchedFallback && matchedFallback.description)
        || getCategoryDescription(cat.category, isCommon, targetRole || backendData.target_role);

      mergedCategories.push({
        category: cat.category,
        coverage: cov,
        benchmarkTarget,
        scope: isCommon ? "common" : "role",
        color: cat.color || (matchedFallback && matchedFallback.color) || (isCommon ? "#4edea3" : "#8083ff"),
        status,
        description,
        total_skills: cat.total_skills || (matchedFallback && matchedFallback.total_skills) || 1,
        aligned_skills: cat.aligned_skills || (matchedFallback && matchedFallback.aligned_skills) || 0
      });
    });
  } else {
    // Offline / fallback mode
    mergedCategories.push(...(roleFallback.categoryCoverage || []));
  }

  // Map 2x2 matrix
  const mappedMatrix = {
    quickWins: (matrix2x2.quick_wins || []).map((m) => ({ skill: m.skill, category: m.category })),
    majorProjects: (matrix2x2.major_projects || []).map((m) => ({ skill: m.skill, category: m.category })),
    fillIns: (matrix2x2.fill_ins || []).map((m) => ({ skill: m.skill, category: m.category })),
    hardLongTerm: (matrix2x2.hard_long_term || []).map((m) => ({ skill: m.skill, category: m.category }))
  };

  if (mappedMatrix.quickWins.length === 0) mappedMatrix.quickWins = roleFallback.matrix2x2?.quickWins || [];
  if (mappedMatrix.majorProjects.length === 0) mappedMatrix.majorProjects = roleFallback.matrix2x2?.majorProjects || [];
  if (mappedMatrix.fillIns.length === 0) mappedMatrix.fillIns = roleFallback.matrix2x2?.fillIns || [];
  if (mappedMatrix.hardLongTerm.length === 0) mappedMatrix.hardLongTerm = roleFallback.matrix2x2?.hardLongTerm || [];

  const resolvedRole = targetRole || backendData.target_role || roleFallback.targetRole;

  return {
    ...roleFallback,
    id: backendData.id || `skillgap_${Date.now()}`,
    targetRole: resolvedRole,
    overallCoverage: backendData.overall_coverage !== undefined ? backendData.overall_coverage : roleFallback.overallCoverage,
    totalAudited: (backendData.total_audited && backendData.total_audited <= 25)
      ? backendData.total_audited
      : (backendData.summary?.total_required_skills || roleFallback.totalAudited || 12),
    gapsIdentifiedCount: mappedGaps.length > 0 ? mappedGaps.length : roleFallback.gapsIdentifiedCount,
    lastCalibrated: backendData.updated_at ? new Date(backendData.updated_at).toLocaleString() : "Real-time Telemetry Synced",
    confidenceIndex: backendData.confidence_index || roleFallback.confidenceIndex,
    categoryCoverage: mergedCategories.length > 0 ? mergedCategories : roleFallback.categoryCoverage,
    gaps: mappedGaps.length > 0 ? mappedGaps : roleFallback.gaps,
    matrix2x2: mappedMatrix,
    strengths: backendData.strengths || roleFallback.strengths || [],
    recommendations: backendData.recommendations || roleFallback.recommendations || []
  };
}

export const skillGapService = {
  getLatestSkillGaps: async (targetRole = null, userContext = null) => {
    const roleClean = targetRole || userContext?.targetRole || userContext?.career?.targetRole || 'AI/ML Engineer';
    try {
      const res = await apiRequest(`/skill-gaps?target_role=${encodeURIComponent(roleClean)}`);
      if (res && res.status === 'success' && res.data) {
        return transformBackendSkillGaps(res.data, roleClean, userContext);
      }
    } catch (e) {
      console.warn("Skill gaps fetch failed, evaluating role telemetry:", e);
    }

    // Try auto-analyzing for the specific target role
    try {
      const analyzeRes = await apiRequest('/skill-gaps/analyze', {
        method: 'POST',
        body: JSON.stringify({ target_role: roleClean })
      });
      if (analyzeRes && analyzeRes.status === 'success' && analyzeRes.data) {
        return transformBackendSkillGaps(analyzeRes.data, roleClean, userContext);
      }
    } catch (err) {
      console.warn("Skill gap automatic role analyze failed, using calibrated profile telemetry:", err);
    }

    return transformBackendSkillGaps(null, roleClean, userContext);
  },

  analyzeSkillGaps: async (targetRole = null, userContext = null) => {
    const roleClean = targetRole || userContext?.targetRole || userContext?.career?.targetRole || 'AI/ML Engineer';
    try {
      const res = await apiRequest('/skill-gaps/analyze', {
        method: 'POST',
        body: JSON.stringify({ target_role: roleClean })
      });
      if (res && res.status === 'success' && res.data) {
        return transformBackendSkillGaps(res.data, roleClean, userContext);
      }
    } catch (e) {
      console.warn("Skill gaps analyze failed, calculating client telemetry:", e);
    }
    return transformBackendSkillGaps(null, roleClean, userContext);
  },

  getSummary: async () => {
    try {
      const res = await apiRequest('/skill-gaps/summary');
      if (res && res.status === 'success' && res.data) {
        return res.data;
      }
    } catch (e) {
      console.warn("Skill gap summary fetch failed:", e);
    }
    return null;
  },

  getHistory: async () => {
    try {
      const res = await apiRequest('/skill-gaps/history');
      if (res && res.status === 'success' && res.data) {
        return res.data;
      }
    } catch (e) {
      console.warn("Skill gap history fetch failed:", e);
    }
    return [];
  }
};

