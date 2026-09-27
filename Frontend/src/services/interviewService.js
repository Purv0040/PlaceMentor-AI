import { apiRequest } from './api';

export const interviewService = {
  startInterview: async (config = {}) => {
    const payload = {
      interview_type: (config.modality || config.interview_type || 'technical').toLowerCase().replace(/[^a-z0-9_]/g, '_'),
      difficulty: (config.difficulty || 'medium').toLowerCase(),
      question_count: config.questionCount || config.question_count || 5,
      target_role: config.role || config.target_role || null,
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
};
