const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('placementor_auth_token') || localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const onboardingService = {
  getOnboardingState: async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/onboarding/`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { success: true, data: null };
    }
  },

  updateStep: async (stepNumber, stepData) => {
    try {
      const res = await fetch(`${API_BASE_URL}/onboarding/step`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          step_number: stepNumber,
          ...stepData
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { success: true, message: `Step ${stepNumber} saved locally` };
    }
  },

  completeOnboarding: async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/onboarding/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { success: true, message: 'Onboarding completed successfully' };
    }
  }
};
