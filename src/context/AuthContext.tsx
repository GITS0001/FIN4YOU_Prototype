import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import { apiClient } from '../api/client';

export interface AuthUser {
  id?: string | number;
  email?: string;
  full_name?: string;
}

interface AuthContextValue {
  isAuthenticated: boolean;
  token: string | null;
  user: AuthUser | null;
  isLoading: boolean;
  login: (token: string, user?: AuthUser) => void;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  isAuthenticated: false,
  token: null,
  user: null,
  isLoading: true,
  login: () => {},
  logout: async () => {},
  refreshProfile: async () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('fin4you_token'));
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const saved = localStorage.getItem('fin4you_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Validate and restore session on app mount
  const restoreSession = useCallback(async () => {
    setIsLoading(true);
    const storedToken = localStorage.getItem('fin4you_token');

    // 1. Check Supabase session first if available
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        localStorage.setItem('fin4you_token', session.access_token);
        setToken(session.access_token);
        const suUser: AuthUser = {
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.user_metadata?.full_name || session.user.user_metadata?.name || session.user.email?.split('@')[0],
        };
        setUser(suUser);
        localStorage.setItem('fin4you_user', JSON.stringify(suUser));
        setIsLoading(false);
        return;
      }
    } catch (e) {
      console.warn('Supabase getSession check skipped:', e);
    }

    // 2. If stored token exists (from native login or previous session)
    if (storedToken) {
      try {
        const res = await apiClient.get('/api/users/profile', {
          headers: { Authorization: `Bearer ${storedToken}` }
        });
        if (res.data) {
          const profileUser: AuthUser = {
            id: res.data.user_id,
            email: res.data.email,
            full_name: res.data.full_name || res.data.email?.split('@')[0] || 'User',
          };
          setUser(profileUser);
          localStorage.setItem('fin4you_user', JSON.stringify(profileUser));
          setToken(storedToken);
        }
      } catch (err: any) {
        if (err.status === 401 || err.response?.status === 401) {
          localStorage.removeItem('fin4you_token');
          localStorage.removeItem('fin4you_user');
          setToken(null);
          setUser(null);
        } else {
          setToken(storedToken);
        }
      }
    } else {
      setToken(null);
      setUser(null);
    }

    setIsLoading(false);
  }, []);

  useEffect(() => {
    restoreSession();

    // Listen to Supabase auth events but DO NOT wipe native tokens on empty session event!
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.access_token) {
        localStorage.setItem('fin4you_token', session.access_token);
        setToken(session.access_token);
        const suUser: AuthUser = {
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0],
        };
        setUser(suUser);
        localStorage.setItem('fin4you_user', JSON.stringify(suUser));
      } else if (event === 'SIGNED_OUT') {
        localStorage.removeItem('fin4you_token');
        localStorage.removeItem('fin4you_user');
        setToken(null);
        setUser(null);
      }
    });

    return () => subscription.unsubscribe();
  }, [restoreSession]);

  const login = (newToken: string, newUser?: AuthUser) => {
    localStorage.setItem('fin4you_token', newToken);
    setToken(newToken);
    if (newUser) {
      setUser(newUser);
      localStorage.setItem('fin4you_user', JSON.stringify(newUser));
    } else {
      apiClient.get('/api/users/profile', { headers: { Authorization: `Bearer ${newToken}` } })
        .then(res => {
          if (res.data) {
            const u: AuthUser = {
              id: res.data.user_id,
              email: res.data.email,
              full_name: res.data.full_name || res.data.email?.split('@')[0] || 'User',
            };
            setUser(u);
            localStorage.setItem('fin4you_user', JSON.stringify(u));
          }
        })
        .catch(() => {});
    }
  };

  const logout = async () => {
    try {
      await supabase.auth.signOut();
    } catch {}
    localStorage.removeItem('fin4you_token');
    localStorage.removeItem('fin4you_user');
    setToken(null);
    setUser(null);
  };

  const refreshProfile = async () => {
    const curToken = token || localStorage.getItem('fin4you_token');
    if (!curToken) return;
    try {
      const res = await apiClient.get('/api/users/profile', { headers: { Authorization: `Bearer ${curToken}` } });
      if (res.data) {
        const u: AuthUser = {
          id: res.data.user_id,
          email: res.data.email,
          full_name: res.data.full_name || res.data.email?.split('@')[0] || 'User',
        };
        setUser(u);
        localStorage.setItem('fin4you_user', JSON.stringify(u));
      }
    } catch {}
  };

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, user, isLoading, login, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
