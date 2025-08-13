import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { getCurrentUser, login as apiLogin, logout as apiLogout, User } from "@/api/auth";
import { clearTokens, getRefreshToken, hasTokens, setTokens } from "@/utils/tokens";

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!user;

  const refreshUser = async () => {
    try {
      setError(null);
      const u = await getCurrentUser();
      setUser(u);
    } catch (e: any) {
      // Если не удается получить пользователя — сбрасываем состояние
      setUser(null);
    }
  };

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiLogin({ username, password });
      // Токены уже установлены в api.login, но продублируем для надежности
      setTokens({ access: resp.access, refresh: resp.refresh });
      await refreshUser();
    } catch (e: any) {
      const message = e?.message || "Login failed";
      setError(message);
      clearTokens();
      setUser(null);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = getRefreshToken() || undefined;
      await apiLogout(r);
    } catch {
      // ignore
    } finally {
      setUser(null);
      setLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      try {
        if (hasTokens()) {
          await refreshUser();
        } else {
          setUser(null);
        }
      } finally {
        setLoading(false);
      }
    };
    void init();
  }, []);

  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      error,
      login,
      logout,
      refreshUser,
    }),
    [user, isAuthenticated, isLoading, error]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
