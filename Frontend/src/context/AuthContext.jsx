import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => authService.getCurrentUser());
  const [isAuthenticated, setIsAuthenticated] = useState(() => authService.isAuthenticated());
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const verify = async () => {
      if (!authService.isAuthenticated()) {
        if (isMounted) {
          setUser(null);
          setIsAuthenticated(false);
          setIsLoading(false);
        }
        return;
      }

      try {
        const verifiedUser = await authService.verifySession();
        if (isMounted) {
          if (verifiedUser) {
            setUser(verifiedUser);
            setIsAuthenticated(true);
          } else {
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } catch (err) {
        if (isMounted) {
          setUser(authService.getCurrentUser());
          setIsAuthenticated(authService.isAuthenticated());
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    verify();

    return () => {
      isMounted = false;
    };
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

  const googleLogin = async (credential) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await authService.googleLogin(credential);
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
        googleLogin,
        resetPassword,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
