import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import { authApi, RegisterPayload } from "@/api/auth";
import type { User } from "@/types";
import { tokenStorage } from "@/utils/tokenStorage";
import { userStorage } from "@/utils/userStorage";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, rememberMe: boolean) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = tokenStorage.getAccess();
    const cachedUser = userStorage.get();
    if (token && cachedUser) {
      setUserState(cachedUser);
    }
    setIsLoading(false);
  }, []);

  const setUser = (next: User | null) => {
    setUserState(next);
    if (next) {
      userStorage.set(next);
    } else {
      userStorage.clear();
    }
  };

  const login = async (email: string, password: string, rememberMe: boolean) => {
    const { data } = await authApi.login(email, password, rememberMe);
    tokenStorage.setTokens(data.access, data.refresh);
    setUser(data.user);
    return data.user;
  };

  const register = async (payload: RegisterPayload) => {
    await authApi.register(payload);
  };

  const logout = async () => {
    const refresh = tokenStorage.getRefresh();
    try {
      if (refresh) await authApi.logout(refresh);
    } catch {
      // Best-effort server-side revocation — clear local session regardless.
    }
    tokenStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, isLoading, login, register, logout, setUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
