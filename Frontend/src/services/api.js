import { authService } from './authService';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiRequest = async (endpoint, options = {}, isRetry = false) => {
  const token = localStorage.getItem('placementor_auth_token') || localStorage.getItem('access_token');
  const defaultHeaders = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    let response;
    try {
      response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    } catch (networkErr) {
      // If localhost failed (e.g. IPv6 resolution on Windows), try 127.0.0.1 fallback
      if (API_BASE_URL.includes('localhost:8000')) {
        const fallbackUrl = API_BASE_URL.replace('localhost:8000', '127.0.0.1:8000');
        response = await fetch(`${fallbackUrl}${endpoint}`, config);
      } else if (!API_BASE_URL.startsWith('http')) {
        // Fallback to direct backend if proxy is inactive
        response = await fetch(`http://127.0.0.1:8000/api/v1${endpoint}`, config);
      } else {
        throw networkErr;
      }
    }

    if (response.status === 401) {
      if (!isRetry) {
        const newToken = await authService.refreshToken();
        if (newToken) {
          return await apiRequest(endpoint, options, true);
        }
      }
      // If session is expired and unrefreshable, return null cleanly without noisy throw
      return null;
    }

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.warn(`[API Warning] ${endpoint}: ${error.message}.`);
    return null;
  }
};
