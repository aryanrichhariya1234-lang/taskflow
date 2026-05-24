"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { User } from "@/types";
import { apiGet } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  setToken: (t: string) => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  token: null,
  loading: true,
  login: () => {},
  logout: () => {},
  setToken: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async (t: string) => {
    try {
      const data = await apiGet<User>("/auth/me", t);
      setUser(data);
    } catch {
      // token invalid
      localStorage.removeItem("tf_token");
      setTokenState(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem("tf_token");
    if (stored) {
      setTokenState(stored);
      fetchUser(stored);
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const setToken = (t: string) => {
    localStorage.setItem("tf_token", t);
    setTokenState(t);
    fetchUser(t);
  };

  const login = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
    window.location.href = `${apiUrl}/auth/google`;
  };

  const logout = () => {
    localStorage.removeItem("tf_token");
    setTokenState(null);
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, setToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
