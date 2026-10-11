const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('placementor_auth_token') || localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const leetcodeService = {
  connect: async (username) => {
    const response = await fetch(`${API_BASE_URL}/leetcode/connect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ username }),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Failed to connect LeetCode account');
    }
    return await response.json();
  },

  getProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  syncProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'LeetCode sync failed');
    }
    return await response.json();
  },

  getStatistics: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/statistics`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  getActivity: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/activity`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  analyzeProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'LeetCode AI analysis failed');
    }
    return await response.json();
  },

  getAnalysis: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/analysis`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  disconnect: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  getDailyPlan: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/daily-plan`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  toggleDailyTask: async (taskId) => {
    const response = await fetch(`${API_BASE_URL}/leetcode/daily-plan/${taskId}/toggle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Failed to update task status');
    }
    return await response.json();
  },

  getActivityHistory: async (days = 30) => {
    const response = await fetch(`${API_BASE_URL}/leetcode/history?days=${days}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  getFocusAreas: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/focus-areas`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  getReadinessBreakdown: async () => {
    const response = await fetch(`${API_BASE_URL}/leetcode/readiness-breakdown`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  }
};
