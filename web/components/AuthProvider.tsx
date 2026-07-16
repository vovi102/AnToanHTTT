"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest, ApiError } from "../lib/api";
import type { User } from "../lib/types";

const TOKEN_KEY = "novabank_token";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  ready: boolean;
  login: (username: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  request: <T>(path: string, options?: RequestInit) => Promise<T>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const saved = sessionStorage.getItem(TOKEN_KEY);
    if (!saved) {
      setReady(true);
      return;
    }
    apiRequest<User>("/auth/me", saved)
      .then((current) => {
        setToken(saved);
        setUser(current);
      })
      .catch(() => sessionStorage.removeItem(TOKEN_KEY))
      .finally(() => setReady(true));
  }, []);

  const expireSession = () => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    router.replace("/login?reason=expired");
  };

  const value = useMemo<AuthContextValue>(() => ({
    user,
    token,
    ready,
    async login(username, password) {
      const result = await apiRequest<{ token: string; user: User }>("/auth/login", null, {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      sessionStorage.setItem(TOKEN_KEY, result.token);
      setToken(result.token);
      setUser(result.user);
      return result.user;
    },
    async logout() {
      if (token) {
        await apiRequest("/auth/logout", token, { method: "POST" }).catch(() => undefined);
      }
      sessionStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
      router.replace("/login");
    },
    async request<T>(path: string, options: RequestInit = {}) {
      try {
        return await apiRequest<T>(path, token, options);
      } catch (error) {
        if (error instanceof ApiError && error.status === 401) expireSession();
        throw error;
      }
    },
  }), [ready, router, token, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
