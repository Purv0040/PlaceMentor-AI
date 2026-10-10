const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('placementor_auth_token') || localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const githubService = {
  connect: async (username) => {
    const response = await fetch(`${API_BASE_URL}/github/connect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ github_username: username }),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Failed to connect GitHub account');
    }
    return await response.json();
  },

  getProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/github`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  syncProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/github/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'GitHub sync failed');
    }
    return await response.json();
  },

  getRepositories: async (page = 1, limit = 50) => {
    const response = await fetch(`${API_BASE_URL}/github/repositories?page=${page}&limit=${limit}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  analyzeProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/github/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'GitHub AI analysis failed');
    }
    return await response.json();
  },

  getAnalysis: async () => {
    const response = await fetch(`${API_BASE_URL}/github/analysis`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  disconnect: async () => {
    const response = await fetch(`${API_BASE_URL}/github`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  }
};
