import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => authService.getCurrentUser());
  const [isAuthenticated, setIsAuthenticated] = useState(() => authService.isAuthenticated());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
      setIsAuthenticated(true);
    } else {
      setUser(null);
      setIsAuthenticated(false);
    }
  }, []);

  const login = async (credentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await authService.login(credentials);
      setUser(res.user);
      setIsAuthenticated(true);
      setIsLoading(false);
      return res;
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      throw err;
    }
  };

  const signup = async (userData) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await authService.signup(userData);
      setUser(res.user);
      setIsAuthenticated(true);
      setIsLoading(false);
      return res;
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      throw err;
    }
  };

  const resetPassword = async (email) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await authService.resetPassword(email);
      setIsLoading(false);
      return res;
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      throw err;
    }
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        isAuthenticated,
        isLoading,
        error,
        setError,
        login,
        signup,
        resetPassword,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
