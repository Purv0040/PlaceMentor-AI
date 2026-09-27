const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('placementor_auth_token') || localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const resumeService = {
  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/resume/upload`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
      },
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Upload failed');
    }
    return await response.json();
  },

  getResumes: async () => {
    const response = await fetch(`${API_BASE_URL}/resume`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) return null;
    return await response.json();
  },

  getResumeDetail: async (resumeId) => {
    const response = await fetch(`${API_BASE_URL}/resume/${resumeId}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) return null;
    return await response.json();
  },

  analyzeResume: async (resumeId) => {
    const response = await fetch(`${API_BASE_URL}/resume/${resumeId}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Analysis failed');
    }
    return await response.json();
  },

  getResumeAnalysis: async (resumeId) => {
    const response = await fetch(`${API_BASE_URL}/resume/${resumeId}/analysis`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) return null;
    return await response.json();
  },

  activateResume: async (resumeId) => {
    const response = await fetch(`${API_BASE_URL}/resume/${resumeId}/activate`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) return null;
    return await response.json();
  },

  deleteResume: async (resumeId) => {
    const response = await fetch(`${API_BASE_URL}/resume/${resumeId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });

    if (!response.ok) return null;
    return await response.json();
  },
};
