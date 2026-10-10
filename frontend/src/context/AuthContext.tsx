import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextValue {
  isAuthenticated: boolean;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  isAuthenticated: false,
  token: null,
  login: () => {},
  logout: () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('fin4you_token');
  });
  const isAuthenticated = !!token;

  const login = (newToken: string) => {
    localStorage.setItem('fin4you_token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('fin4you_token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
