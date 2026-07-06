"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api, login as apiLogin, setToken } from "./api";
import { UserOut } from "./types";
import { DEFAULT_DEMO_ACCOUNT, DEMO_PASSWORD } from "./demo-accounts";

interface AuthContextValue {
  user: UserOut | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  switchRole: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function login(email: string, password: string) {
    const data = await apiLogin(email, password);
    setToken(data.access_token);
    setUser(data.user);
  }

  useEffect(() => {
    async function bootstrap() {
      const stored = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      if (stored) {
        try {
          const me = await api.get<UserOut>("/api/v1/auth/me");
          setUser(me);
          setLoading(false);
          return;
        } catch {
          setToken(null);
        }
      }

      // This is a public portfolio demo: there is no sign-in wall. Every
      // visitor is silently authenticated as a demo account (switchable via
      // the role picker in the top bar) so the app is viewable with zero
      // friction, while the backend still sits behind auth/rate limits.
      try {
        await login(DEFAULT_DEMO_ACCOUNT.email, DEMO_PASSWORD);
      } catch {
        setError("Could not reach the Roadway AI backend. Please try again shortly.");
      } finally {
        setLoading(false);
      }
    }
    bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function switchRole(email: string) {
    await login(email, DEMO_PASSWORD);
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, login, switchRole }}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
