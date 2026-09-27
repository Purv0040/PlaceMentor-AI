// Skill Gap Service connecting Frontend UI to real Backend API endpoints with fallback support

import { apiRequest } from "./api";
import { initialSkillGapData } from "../data/skillGapData";

function transformBackendSkillGaps(backendData) {
  if (!backendData) return initialSkillGapData;

  const summary = backendData.summary || {};
  const priorityGaps = backendData.priority_gaps || [];
  const matrix2x2 = backendData.matrix2x2 || {};
  const categoryCoverage = backendData.category_coverage || [];

  // Map priority gaps to UI expected format
  const mappedGaps = priorityGaps.map((g, idx) => ({
    id: g.id || `gap-${idx + 1}`,
    skill: g.skill,
    category: g.category,
    currentLevel: g.current_level === "Advanced" ? 4 : g.current_level === "Intermediate" ? 3 : g.current_level === "Beginner" ? 2 : 1,
    currentLevelText: g.current_level_text || `${g.current_level} (Level ${g.current_level_num || 1}/4)`,
    requiredLevel: g.required_level === "Expert" ? 5 : g.required_level === "Advanced" ? 4 : g.required_level === "Intermediate" ? 3 : 2,
    requiredLevelText: g.required_level_text || `${g.required_level} (Level ${g.required_level_num || 2}/4)`,
    priority: g.priority || "High",
    reason: g.reason || "Important benchmark requirement for target role.",
    suggestedAction: g.suggested_action || "Advance proficiency via targeted projects and roadmap.",
    actionLabel: g.action_label || "Add to Roadmap",
    actionRoute: g.action_route || "/roadmap"
  }));

  // Map 2x2 matrix
  const mappedMatrix = {
    quickWins: (matrix2x2.quick_wins || []).map((m) => ({ skill: m.skill, category: m.category })),
    majorProjects: (matrix2x2.major_projects || []).map((m) => ({ skill: m.skill, category: m.category })),
    fillIns: (matrix2x2.fill_ins || []).map((m) => ({ skill: m.skill, category: m.category })),
    hardLongTerm: (matrix2x2.hard_long_term || []).map((m) => ({ skill: m.skill, category: m.category }))
  };

  // Fallback defaults if empty
  if (mappedMatrix.quickWins.length === 0) {
    mappedMatrix.quickWins = initialSkillGapData.matrix2x2.quickWins;
  }
  if (mappedMatrix.majorProjects.length === 0) {
    mappedMatrix.majorProjects = initialSkillGapData.matrix2x2.majorProjects;
  }
  if (mappedMatrix.fillIns.length === 0) {
    mappedMatrix.fillIns = initialSkillGapData.matrix2x2.fillIns;
  }
  if (mappedMatrix.hardLongTerm.length === 0) {
    mappedMatrix.hardLongTerm = initialSkillGapData.matrix2x2.hardLongTerm;
  }

  return {
    ...initialSkillGapData,
    id: backendData.id,
    targetRole: backendData.target_role || "Backend Developer",
    overallCoverage: backendData.overall_coverage !== undefined ? backendData.overall_coverage : 72,
    totalAudited: backendData.total_audited || 25,
    gapsIdentifiedCount: mappedGaps.length,
    lastCalibrated: backendData.updated_at ? new Date(backendData.updated_at).toLocaleString() : "Just now (Automated)",
    confidenceIndex: backendData.confidence_index || "95.0%",
    categoryCoverage: categoryCoverage.length > 0 ? categoryCoverage : initialSkillGapData.categoryCoverage,
    gaps: mappedGaps.length > 0 ? mappedGaps : initialSkillGapData.gaps,
    matrix2x2: mappedMatrix,
    strengths: backendData.strengths || [],
    recommendations: backendData.recommendations || []
  };
}

export const skillGapService = {
  getLatestSkillGaps: async () => {
    const res = await apiRequest('/skill-gaps');
    if (res && res.status === 'success' && res.data) {
      return transformBackendSkillGaps(res.data);
    }
    return transformBackendSkillGaps(null);
  },

  analyzeSkillGaps: async (targetRole = null) => {
    const res = await apiRequest('/skill-gaps/analyze', {
      method: 'POST',
      body: JSON.stringify(targetRole ? { target_role: targetRole } : {})
    });
    if (res && res.status === 'success' && res.data) {
      return transformBackendSkillGaps(res.data);
    }
    return skillGapService.getLatestSkillGaps();
  },

  getSummary: async () => {
    const res = await apiRequest('/skill-gaps/summary');
    if (res && res.status === 'success' && res.data) {
      return res.data;
    }
    return null;
  },

  getHistory: async () => {
    const res = await apiRequest('/skill-gaps/history');
    if (res && res.status === 'success' && res.data) {
      return res.data;
    }
    return [];
  }
};
