import { apiRequest } from './api';

export const communicationService = {
  analyzeCommunication: async (question, answerText) => {
    const res = await apiRequest('/communication/analyze', {
      method: 'POST',
      body: JSON.stringify({
        question,
        answer: answerText,
      }),
    });
    return res;
  },

  getCommunicationSummary: async () => {
    return await apiRequest('/communication/summary');
  },

  getCommunicationHistory: async () => {
    const res = await apiRequest('/communication/history');
    return Array.isArray(res) ? res : [];
  },

  getAnalysisById: async (analysisId) => {
    return await apiRequest(`/communication/${analysisId}`);
  },
};
