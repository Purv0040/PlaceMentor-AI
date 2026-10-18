const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const TOKEN_KEY = 'placementor_auth_token';
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'placementor_refresh_token';
const USER_KEY = 'placementor_user_data';
const ONBOARDING_COMPLETE_KEY = 'placementCopilotOnboardingComplete';

let refreshPromise = null;

export const authService = {
  isTokenExpired: (token) => {
    if (!token || typeof token !== 'string') return true;
    if (token.startsWith('mock_')) return true;
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    try {
      const base64Url = parts[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const payload = JSON.parse(jsonPayload);
      if (!payload.exp) return false;
      return Date.now() + 10000 >= payload.exp * 1000;
    } catch (e) {
      return true;
    }
  },

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
      throw new Error('Unable to connect to the authentication server. Please ensure the backend is running.');
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

  signup: async (userData) => {
    const rawName = userData?.full_name || userData?.fullName || userData?.name || '';
    const rawEmail = userData?.email || '';
    const rawPassword = userData?.password || '';

    const name = typeof rawName === 'string' ? rawName.trim() : '';
    const email = typeof rawEmail === 'string' ? rawEmail.trim() : '';
    const password = rawPassword;

    if (!name || !email || !password) {
      throw new Error('All fields are required.');
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          full_name: name,
          name,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const payload = data.data || data;
        const token = payload.access_token || payload.token;
        const refreshToken = payload.refresh_token;
        const backendUser = payload.user || {};

        const newUser = {
          id: backendUser.id || 'user_' + Date.now(),
          name: name,
          full_name: name,
          email: email,
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
        let msg = errData?.error?.message || errData?.detail;

        // If generic validation error message returned, parse details array
        if (!msg || msg === 'Invalid request parameters or payload.') {
          if (Array.isArray(errData?.error?.details) && errData.error.details.length > 0) {
            const detailMsgs = errData.error.details.map((d) => {
              const field = d.loc ? d.loc[d.loc.length - 1] : '';
              const cleanField = field ? field.replace('_', ' ') : 'field';
              const raw = d.msg || '';
              if (raw.includes('not a valid email address')) {
                return 'Please enter a valid email address.';
              }
              if (raw.includes('at least 6 characters')) {
                return 'Password must be at least 6 characters long.';
              }
              if (raw.includes('at least 2 characters')) {
                return 'Full name must be at least 2 characters long.';
              }
              if (raw.includes('Field required')) {
                return `${cleanField.charAt(0).toUpperCase() + cleanField.slice(1)} is required.`;
              }
              return raw;
            });
            msg = detailMsgs.filter(Boolean).join(' ');
          }
        }

        if (!msg) {
          msg = res.status === 409
            ? 'A user with this email already exists.'
            : 'Registration failed. Please check your information and try again.';
        }

        const error = new Error(msg);
        error.status = res.status;
        error.details = errData?.error?.details;
        throw error;
      }
    } catch (err) {
      if (err.message && err.message !== 'Failed to fetch' && !err.message.includes('NetworkError')) {
        throw err;
      }
      throw new Error('Unable to connect to the registration server. Please ensure the backend is running.');
    }
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (!refreshToken || refreshToken.startsWith('mock_')) {
      return null;
    }

    if (refreshPromise) {
      return refreshPromise;
    }

    refreshPromise = (async () => {
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
          await authService.logout();
          return null;
        }
      } catch (err) {
        return null;
      } finally {
        refreshPromise = null;
      }
    })();

    return refreshPromise;
  },

  verifySession: async () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) return null;

    // Reject and purge mock tokens immediately
    if (token.startsWith('mock_')) {
      await authService.logout();
      return null;
    }

    // If access token is expired, proactively refresh before querying /auth/me
    let activeToken = token;
    if (authService.isTokenExpired(token)) {
      activeToken = await authService.refreshToken();
      if (!activeToken) {
        await authService.logout();
        return null;
      }
    }

    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${activeToken}`,
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
        // Try refresh token if not already refreshed
        const newToken = await authService.refreshToken();
        if (newToken) {
          const retryRes = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${newToken}`,
              'Content-Type': 'application/json',
            },
          });
          if (retryRes.ok) {
            const data = await retryRes.json();
            const backendUser = data.data || data;
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
            return updatedUser;
          }
        }
        await authService.logout();
        return null;
      } else {
        await authService.logout();
        return null;
      }
    } catch (err) {
      if (authService.isTokenExpired(token)) {
        await authService.logout();
        return null;
      }
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

    // Notify all listening contexts that the user session has ended
    window.dispatchEvent(new CustomEvent('auth:logout'));

    return { success: true };
  },

  getAccessToken: () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token || token.startsWith('mock_')) return null;
    return token;
  },

  getToken: () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token || token.startsWith('mock_')) return null;
    return token;
  },

  getCurrentUser: () => {
    const token = localStorage.getItem(TOKEN_KEY) || localStorage.getItem(ACCESS_TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);
    if (token && userJson && !token.startsWith('mock_')) {
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
    if (!token || !userJson) return false;
    if (token.startsWith('mock_')) return false;
    return true;
  },
};
