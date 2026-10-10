const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const getAuthHeaders = () => {
  const token = localStorage.getItem('placementor_auth_token') || localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const projectService = {
  getProjects: async (includeArchived = false) => {
    const response = await fetch(`${API_BASE_URL}/projects?include_archived=${includeArchived}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  getProjectById: async (projectId) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  createProject: async (projectData) => {
    const response = await fetch(`${API_BASE_URL}/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(projectData),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Failed to create project');
    }
    return await response.json();
  },

  updateProject: async (projectId, projectData) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(projectData),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Failed to update project');
    }
    return await response.json();
  },

  deleteProject: async (projectId, softDelete = true) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}?soft_delete=${softDelete}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  },

  toggleFeatured: async (projectId, isFeatured) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/featured`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ is_featured: isFeatured }),
    });
    if (!response.ok) return null;
    return await response.json();
  },

  analyzeProject: async (projectId) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || err.message || 'Project AI analysis failed');
    }
    return await response.json();
  },

  getProjectAnalysis: async (projectId) => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/analysis`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    if (!response.ok) return null;
    return await response.json();
  }
};
