import { apiRequest } from './api';

export const interviewService = {
  startInterview: async (config = {}) => {
    const rawModality = String(config.modality || config.interview_type || 'system_design').toLowerCase();
    let normalizedType = 'system_design';
    if (rawModality.includes('dsa') || rawModality.includes('drill') || rawModality.includes('tech') || rawModality.includes('algo')) {
      normalizedType = 'dsa';
    } else if (rawModality.includes('behavioral') || rawModality.includes('hr') || rawModality.includes('star')) {
      normalizedType = 'behavioral';
    } else if (rawModality.includes('combined') || rawModality.includes('tier') || rawModality.includes('full')) {
      normalizedType = 'combined';
    } else if (rawModality.includes('design') || rawModality.includes('architecture') || rawModality.includes('system')) {
      normalizedType = 'system_design';
    }

    const payload = {
      interview_type: normalizedType,
      difficulty: (config.difficulty || 'medium').toLowerCase(),
      question_count: config.questionCount || config.question_count || 5,
      target_role: config.role || config.target_role || null,
      modality: config.modality || 'System Architecture & Design',
    };
    const res = await apiRequest('/interviews', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    return res;
  },

  getCurrentQuestion: async (interviewId) => {
    return await apiRequest(`/interviews/${interviewId}/current`);
  },

  submitAnswer: async (interviewId, answerText) => {
    return await apiRequest(`/interviews/${interviewId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer: answerText }),
    });
  },

  completeInterview: async (interviewId) => {
    return await apiRequest(`/interviews/${interviewId}/complete`, {
      method: 'POST',
    });
  },

  getInterviewHistory: async () => {
    const res = await apiRequest('/interviews/history');
    return Array.isArray(res) ? res : [];
  },

  getInterviewById: async (interviewId) => {
    return await apiRequest(`/interviews/${interviewId}`);
  },

  getInterviewQuestions: async (interviewId) => {
    return await apiRequest(`/interviews/${interviewId}/questions`);
  },
};
