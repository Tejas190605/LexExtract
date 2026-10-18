import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginApi, registerApi, getMeApi, logoutApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('lexextract_token') || null);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Validate existing token on mount
  useEffect(() => {
    let isMounted = true;
    const restoreSession = async () => {
      const storedToken = localStorage.getItem('lexextract_token');
      if (storedToken) {
        try {
          const profile = await getMeApi();
          if (isMounted) {
            setUser(profile);
            setToken(storedToken);
          }
        } catch (err) {
          if (isMounted) {
            localStorage.removeItem('lexextract_token');
            setUser(null);
            setToken(null);
          }
        }
      }
      if (isMounted) {
        setIsLoading(false);
      }
    };

    restoreSession();
    return () => { isMounted = false; };
  }, []);

  const login = async (emailOrUsername, password) => {
    setAuthError(null);
    try {
      const data = await loginApi({ email_or_username: emailOrUsername, password });
      const accessToken = data.access_token;
      localStorage.setItem('lexextract_token', accessToken);
      setToken(accessToken);

      // Fetch user profile if not directly provided
      const profile = data.user || await getMeApi();
      setUser(profile);
      return { success: true, user: profile };
    } catch (err) {
      const detail = err.response?.data?.detail 
        || (!err.response 
          ? 'Unable to connect to the authentication server. Please check your network connection or verify the backend is running.' 
          : 'Unable to sign in with the provided credentials.');
      setAuthError(detail);
      return { success: false, error: detail };
    }
  };

  const register = async (regData) => {
    setAuthError(null);
    try {
      const newUser = await registerApi(regData);
      return { success: true, user: newUser };
    } catch (err) {
      const detail = err.response?.data?.detail 
        || (!err.response 
          ? 'Unable to connect to the authentication server. Please check your network connection or verify the backend is running.' 
          : 'Registration failed. Please verify your details.');
      setAuthError(detail);
      return { success: false, error: detail };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await logoutApi();
      }
    } catch (err) {
      // Ignore logout network errors
    } finally {
      localStorage.removeItem('lexextract_token');
      setUser(null);
      setToken(null);
      setAuthError(null);
    }
  };

  const value = {
    user,
    token,
    role: user?.role?.toUpperCase() || 'ANONYMOUS',
    isAuthenticated: Boolean(user && token),
    isLoading,
    authError,
    setAuthError,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
