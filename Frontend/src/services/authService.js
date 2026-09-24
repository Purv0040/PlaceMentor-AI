import { mockUser } from '../data/mockUser';

const MOCK_TOKEN_KEY = 'placementor_auth_token';
const MOCK_USER_KEY = 'placementor_user_data';

export const authService = {
  login: async ({ email, password }) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!email || !password) {
          reject(new Error('Email and password are required.'));
          return;
        }

        const user = {
          ...mockUser,
          email: email,
          name: email.split('@')[0].replace('.', ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'Alex Patel'
        };

        const token = 'mock_jwt_token_' + Date.now();
        localStorage.setItem(MOCK_TOKEN_KEY, token);
        localStorage.setItem(MOCK_USER_KEY, JSON.stringify(user));

        resolve({ success: true, token, user });
      }, 600);
    });
  },

  signup: async ({ name, email, password }) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!name || !email || !password) {
          reject(new Error('All fields are required.'));
          return;
        }

        const newUser = {
          ...mockUser,
          id: 'user-' + Date.now(),
          name: name,
          email: email
        };

        const token = 'mock_jwt_token_' + Date.now();
        localStorage.setItem(MOCK_TOKEN_KEY, token);
        localStorage.setItem(MOCK_USER_KEY, JSON.stringify(newUser));

        resolve({ success: true, token, user: newUser });
      }, 600);
    });
  },

  resetPassword: async (email) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!email) {
          reject(new Error('Please enter a valid college email address.'));
          return;
        }
        resolve({
          success: true,
          message: `Password reset instructions have been sent to ${email}.`
        });
      }, 500);
    });
  },

  logout: async () => {
    return new Promise((resolve) => {
      setTimeout(() => {
        localStorage.removeItem(MOCK_TOKEN_KEY);
        localStorage.removeItem(MOCK_USER_KEY);
        resolve({ success: true });
      }, 200);
    });
  },

  getCurrentUser: () => {
    const token = localStorage.getItem(MOCK_TOKEN_KEY);
    const userJson = localStorage.getItem(MOCK_USER_KEY);
    if (token && userJson) {
      try {
        return JSON.parse(userJson);
      } catch (e) {
        return mockUser;
      }
    }
    return mockUser; // Default mock user for demo
  },

  isAuthenticated: () => {
    return !!localStorage.getItem(MOCK_TOKEN_KEY) || true; // Dev default true if token present or fallback
  }
};
