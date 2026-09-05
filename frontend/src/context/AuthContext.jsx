import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [officer, setOfficer] = useState(() => {
    const saved = localStorage.getItem('officer_data');
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      localStorage.removeItem('officer_data');
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('officer_token'));
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Validate current token on startup if one exists
    const initializeAuth = async () => {
      const savedToken = localStorage.getItem('officer_token');
      if (savedToken) {
        try {
          const data = await authService.getProfile();
          const currentOfficer = data.officer || data.user;
          if (data.status === 'success' && currentOfficer) {
            setOfficer(currentOfficer);
            localStorage.setItem('officer_data', JSON.stringify(currentOfficer));
          }
        } catch (err) {
          console.warn('Session expired or invalid token:', err);
          logout();
        }
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (officer_id, password) => {
    const res = await authService.login(officer_id, password);
    if (res.token && res.officer) {
      setToken(res.token);
      setOfficer(res.officer);
      localStorage.setItem('officer_token', res.token);
      localStorage.setItem('officer_data', JSON.stringify(res.officer));
      return res;
    }
    throw new Error(res.message || 'Login failed');
  };

  const logout = async () => {
    await authService.logout();
    setToken(null);
    setOfficer(null);
  };

  const value = {
    officer,
    token,
    isAuthenticated: !!token && !!officer,
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
