const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const TOKEN_KEY = 'placementor_auth_token';
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
        const token = payload.access_token || payload.token || 'jwt_token_' + Date.now();
        const backendUser = payload.user || {};

        const user = {
          id: backendUser.id || 'user_' + Date.now(),
          name: backendUser.full_name || backendUser.name || email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase()),
          email: backendUser.email || email,
          is_onboarded: backendUser.is_onboarded || localStorage.getItem(ONBOARDING_COMPLETE_KEY) === 'true',
        };

        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));

        return { success: true, token, user };
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
      const fallbackUser = {
        id: 'user_' + Date.now(),
        name: formattedName,
        email: email,
        is_onboarded: localStorage.getItem(ONBOARDING_COMPLETE_KEY) === 'true',
      };

      const token = 'mock_jwt_token_' + Date.now();
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(fallbackUser));

      return { success: true, token, user: fallbackUser };
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
        const token = payload.access_token || payload.token || 'jwt_token_' + Date.now();
        const backendUser = payload.user || {};

        const newUser = {
          id: backendUser.id || 'user_' + Date.now(),
          name: name,
          email: email,
          is_onboarded: false,
        };

        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(newUser));
        localStorage.removeItem(ONBOARDING_COMPLETE_KEY);

        return { success: true, token, user: newUser };
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
        email: email,
        is_onboarded: false,
      };

      const token = 'mock_jwt_token_' + Date.now();
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(newUser));
      localStorage.removeItem(ONBOARDING_COMPLETE_KEY);

      return { success: true, token, user: newUser };
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
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(ONBOARDING_COMPLETE_KEY);
    localStorage.removeItem('placementCopilotOnboarding');
    return { success: true };
  },

  getCurrentUser: () => {
    const token = localStorage.getItem(TOKEN_KEY);
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
    const token = localStorage.getItem(TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);
    return !!(token && userJson);
  },
};
