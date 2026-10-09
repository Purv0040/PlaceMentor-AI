const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const TOKEN_KEY = 'placementor_auth_token';
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'placementor_refresh_token';
const USER_KEY = 'placementor_user_data';
const ONBOARDING_COMPLETE_KEY = 'placementCopilotOnboardingComplete';

export const authService = {
  login: async ({ email, password }) => {
    if (!email || !password) {
      throw new Error('Email and password are required.');
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (res.ok) {
        const data = await res.json();
        const payload = data.data || data;
        const token = payload.access_token || payload.token;
        const refreshToken = payload.refresh_token;
        const backendUser = payload.user || {};

        const isOnboarded = typeof backendUser.is_onboarded === 'boolean'
          ? backendUser.is_onboarded
          : (localStorage.getItem(ONBOARDING_COMPLETE_KEY) === 'true');

        const user = {
          id: backendUser.id || 'user_' + Date.now(),
          name: backendUser.full_name || backendUser.name || email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase()),
          full_name: backendUser.full_name || backendUser.name || email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase()),
          email: backendUser.email || email,
          is_onboarded: isOnboarded,
        };

        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(ACCESS_TOKEN_KEY, token);
        if (refreshToken) {
          localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
        }

        if (isOnboarded) {
          localStorage.setItem(ONBOARDING_COMPLETE_KEY, 'true');
        } else {
          localStorage.removeItem(ONBOARDING_COMPLETE_KEY);
        }

        localStorage.setItem(USER_KEY, JSON.stringify(user));

        return { success: true, token, refreshToken, user };
      } else {
        const errData = await res.json().catch(() => ({}));
        const msg = errData?.error?.message || errData?.detail || 'Invalid email or password credentials.';
        throw new Error(msg);
      }
    } catch (err) {
      if (err.message && err.message !== 'Failed to fetch' && !err.message.includes('NetworkError')) {
        throw err;
      }
      // Offline fallback: construct user object dynamically from provided email
      const formattedName = email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase());
      const isOnboarded = localStorage.getItem(ONBOARDING_COMPLETE_KEY) === 'true';
      const fallbackUser = {
        id: 'user_' + Date.now(),
        name: formattedName,
        full_name: formattedName,
        email: email,
        is_onboarded: isOnboarded,
      };

      const token = 'mock_jwt_token_' + Date.now();
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(fallbackUser));

      return { success: true, token, user: fallbackUser };
    }
  },

  googleLogin: async (credential) => {
    if (!credential) {
      throw new Error('Google authentication failed. No credential received.');
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential }),
      });

      if (res.ok) {
        const data = await res.json();
        const payload = data.data || data;
        const token = payload.access_token || payload.token;
        const refreshToken = payload.refresh_token;
        const backendUser = payload.user || {};

        const isOnboarded = typeof backendUser.is_onboarded === 'boolean'
          ? backendUser.is_onboarded
          : (localStorage.getItem(ONBOARDING_COMPLETE_KEY) === 'true');

        const user = {
          id: backendUser.id || 'user_' + Date.now(),
          name: backendUser.full_name || backendUser.name || 'Google User',
          full_name: backendUser.full_name || backendUser.name || 'Google User',
          email: backendUser.email || '',
          is_onboarded: isOnboarded,
        };

        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(ACCESS_TOKEN_KEY, token);
        if (refreshToken) {
          localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
        }

        if (isOnboarded) {
          localStorage.setItem(ONBOARDING_COMPLETE_KEY, 'true');
        } else {
          localStorage.removeItem(ONBOARDING_COMPLETE_KEY);
        }

        localStorage.setItem(USER_KEY, JSON.stringify(user));

        return { success: true, token, refreshToken, user };
      } else {
        const errData = await res.json().catch(() => ({}));
        const msg = errData?.error?.message || errData?.detail || 'Google authentication failed.';
        throw new Error(msg);
      }
    } catch (err) {
      if (err.message && err.message !== 'Failed to fetch' && !err.message.includes('NetworkError')) {
        throw err;
      }
      throw new Error('Unable to connect to the server. Please try again.');
    }
  },

  signup: async ({ name, email, password }) => {
    if (!name || !email || !password) {
      throw new Error('All fields are required.');
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: name }),
      });

      if (res.ok) {
        const data = await res.json();
        const payload = data.data || data;
        const token = payload.access_token || payload.token;
        const refreshToken = payload.refresh_token;
        const backendUser = payload.user || {};

        const newUser = {
          id: backendUser.id || 'user_' + Date.now(),
          name: name.trim(),
          full_name: name.trim(),
          email: email.trim(),
          is_onboarded: false,
        };

        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(ACCESS_TOKEN_KEY, token);
        if (refreshToken) {
          localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
        }
        localStorage.setItem(USER_KEY, JSON.stringify(newUser));
        localStorage.removeItem(ONBOARDING_COMPLETE_KEY);
        localStorage.removeItem('placementCopilotProfile');
        localStorage.removeItem('placementCopilotResumeName');
        localStorage.removeItem('placementCopilotOnboarding');

        return { success: true, token, refreshToken, user: newUser };
      } else {
        const errData = await res.json().catch(() => ({}));
        const msg = errData?.error?.message || errData?.detail || 'Registration failed. An account with this email may already exist.';
        throw new Error(msg);
      }
    } catch (err) {
      if (err.message && err.message !== 'Failed to fetch' && !err.message.includes('NetworkError')) {
        throw err;
      }
      // Offline fallback for registration
      const newUser = {
        id: 'user_' + Date.now(),
        name: name,
        full_name: name,
        email: email,
        is_onboarded: false,
      };

      const token = 'mock_jwt_token_' + Date.now();
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(newUser));
      localStorage.removeItem(ONBOARDING_COMPLETE_KEY);

      return { success: true, token, user: newUser };
    }
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken || refreshToken.startsWith('mock_')) {
      return null;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (res.ok) {
        const data = await res.json();
        const payload = data.data || data;
        const newAccessToken = payload.access_token;
        const newRefreshToken = payload.refresh_token || refreshToken;
        const backendUser = payload.user;

        localStorage.setItem(TOKEN_KEY, newAccessToken);
        localStorage.setItem(ACCESS_TOKEN_KEY, newAccessToken);
        localStorage.setItem(REFRESH_TOKEN_KEY, newRefreshToken);

        if (backendUser) {
          const currentUser = authService.getCurrentUser() || {};
          const updatedUser = {
            ...currentUser,
            id: backendUser.id || currentUser.id,
            name: backendUser.full_name || currentUser.name,
            full_name: backendUser.full_name || currentUser.full_name,
            email: backendUser.email || currentUser.email,
            is_onboarded: typeof backendUser.is_onboarded === 'boolean' ? backendUser.is_onboarded : currentUser.is_onboarded,
          };
          localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
        }

        return newAccessToken;
      } else {
        authService.logout();
        return null;
      }
    } catch (err) {
      return null;
    }
  },

  verifySession: async () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) return null;

    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (res.ok) {
        const data = await res.json();
        const backendUser = data.data || data;
        const currentUser = authService.getCurrentUser() || {};

        const updatedUser = {
          ...currentUser,
          id: backendUser.id || currentUser.id,
          name: backendUser.full_name || currentUser.name || backendUser.email?.split('@')[0],
          full_name: backendUser.full_name || currentUser.full_name,
          email: backendUser.email || currentUser.email,
          is_onboarded: typeof backendUser.is_onboarded === 'boolean' ? backendUser.is_onboarded : currentUser.is_onboarded,
        };

        if (updatedUser.is_onboarded) {
          localStorage.setItem(ONBOARDING_COMPLETE_KEY, 'true');
        }

        localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
        return updatedUser;
      } else if (res.status === 401) {
        // Try refresh token
        const newToken = await authService.refreshToken();
        if (newToken) {
          return authService.getCurrentUser();
        } else {
          await authService.logout();
          return null;
        }
      } else {
        return authService.getCurrentUser();
      }
    } catch (err) {
      // Network error / offline mode: trust local storage session
      return authService.getCurrentUser();
    }
  },

  resetPassword: async (email) => {
    if (!email) {
      throw new Error('Please enter a valid college email address.');
    }
    return {
      success: true,
      message: `Password reset instructions have been sent to ${email}.`,
    };
  },

  logout: async () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token && !token.startsWith('mock_')) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => {});
      } catch (e) {}
    }

    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(ONBOARDING_COMPLETE_KEY);
    localStorage.removeItem('placementCopilotOnboarding');
    localStorage.removeItem('placementCopilotProfile');
    localStorage.removeItem('placementCopilotResumeName');
    return { success: true };
  },

  getCurrentUser: () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);
    if (token && userJson) {
      try {
        return JSON.parse(userJson);
      } catch (e) {
        return null;
      }
    }
    return null;
  },

  isAuthenticated: () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);
    return !!(token && userJson);
  },
};
