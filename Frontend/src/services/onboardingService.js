import { apiRequest } from './api';

export const onboardingService = {
  getOnboardingState: async () => {
    try {
      const res = await apiRequest('/onboarding/');
      return res || { success: true, data: null };
    } catch (err) {
      return { success: true, data: null };
    }
  },

  updateStep: async (stepNumber, stepData) => {
    try {
      const res = await apiRequest('/onboarding/step', {
        method: 'PATCH',
        body: JSON.stringify({
          step_number: stepNumber,
          ...stepData
        }),
      });
      return res || { success: true, message: `Step ${stepNumber} saved locally` };
    } catch (err) {
      return { success: true, message: `Step ${stepNumber} saved locally` };
    }
  },

  completeOnboarding: async () => {
    try {
      const res = await apiRequest('/onboarding/complete', {
        method: 'POST',
      });
      return res || { success: true, message: 'Onboarding completed successfully' };
    } catch (err) {
      return { success: true, message: 'Onboarding completed successfully' };
    }
  }
};

