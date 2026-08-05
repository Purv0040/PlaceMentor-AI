import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor attaching JWT to authenticated requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token') || localStorage.getItem('placeMentor_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export interface LoginPayload {
  email: string;
  password?: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password?: string;
}

export interface AuthResponse {
  access_token?: string;
  token?: string;
  user?: {
    name?: string;
    email?: string;
    id?: string;
  };
}

export const authApi = {
  login: async (credentials: LoginPayload): Promise<AuthResponse> => {
    try {
      const response = await api.post('/auth/login', credentials);
      return response.data;
    } catch (err) {
      // Try fallback endpoint /login if /auth/login fails
      try {
        const response = await api.post('/login', credentials);
        return response.data;
      } catch {
        throw err;
      }
    }
  },
  register: async (userData: RegisterPayload): Promise<AuthResponse> => {
    try {
      const response = await api.post('/auth/register', userData);
      return response.data;
    } catch (err) {
      try {
        const response = await api.post('/register', userData);
        return response.data;
      } catch {
        throw err;
      }
    }
  },
};

export interface DomainItem {
  id: string;
  title: string;
  description: string;
  icon?: string;
  popularBadge?: boolean;
}

export const domainApi = {
  getDomains: async (): Promise<DomainItem[]> => {
    const response = await api.get('/domains');
    return response.data;
  },
};

export interface ReportAnalysisPayload {
  domain: string;
  academicDetails: {
    studentName: string;
    email: string;
    branch: string;
    collegeName: string;
  };
  profileLinks: {
    githubUrl: string;
    leetcodeUrl: string;
    hackerRankUrl: string;
    linkedinUrl?: string;
    resumeFileName?: string;
    resumeText?: string;
    resumeMode?: 'file' | 'text';
  };
}

export const reportApi = {
  createReport: async (payload: ReportAnalysisPayload) => {
    const response = await api.post('/reports', payload);
    return response.data;
  },
  getSkillRoadmap: async (reportId: string | number, skillName: string, reason?: string) => {
    const response = await api.post(`/reports/${reportId}/roadmap`, {
      skill: skillName,
      reason,
    });
    return response.data;
  },
  downloadReport: async (reportId: string | number) => {
    const response = await api.get(`/reports/${reportId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
