import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

import {
  api,
  ApiError,
  AuthPayload,
  AuthResponse,
  setAuthToken,
  UserProfile
} from '../lib/api/client';

interface AuthContextValue {
  user: UserProfile | null;
  token: string | null;
  loading: boolean;
  login: (payload: AuthPayload) => Promise<UserProfile>;
  register: (payload: AuthPayload) => Promise<UserProfile>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const STORAGE_KEY = 'diet-planner.accessToken';

const readInitialToken = () => {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(STORAGE_KEY);
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const initialToken = readInitialToken();
  const [token, setTokenState] = useState<string | null>(() => initialToken);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [initializing, setInitializing] = useState<boolean>(Boolean(initialToken));
  const [pendingAuth, setPendingAuth] = useState(false);
  const skipProfileFetchRef = useRef(false);

  const setToken = useCallback((value: string | null) => {
    setTokenState(value);
    if (typeof window !== 'undefined') {
      if (value) {
        window.localStorage.setItem(STORAGE_KEY, value);
      } else {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  const clearSession = useCallback(() => {
    setAuthToken(null);
    setToken(null);
    setUser(null);
  }, [setToken]);

  useEffect(() => {
    if (!token) {
      clearSession();
      setInitializing(false);
      return;
    }

    setAuthToken(token);
    if (skipProfileFetchRef.current) {
      skipProfileFetchRef.current = false;
      setInitializing(false);
      return;
    }

    let cancelled = false;
    const fetchProfile = async () => {
      setInitializing(true);
      try {
        const profile = await api.fetchProfile();
        if (!cancelled) {
          setUser(profile);
        }
      } catch {
        if (!cancelled) {
          clearSession();
        }
      } finally {
        if (!cancelled) {
          setInitializing(false);
        }
      }
    };

    fetchProfile();

    return () => {
      cancelled = true;
    };
  }, [token, clearSession]);

  const authenticate = useCallback(
    async (fn: (payload: AuthPayload) => Promise<AuthResponse>, payload: AuthPayload) => {
      setPendingAuth(true);
      try {
        const response = await fn(payload);
        skipProfileFetchRef.current = true;
        setAuthToken(response.access_token);
        setToken(response.access_token);
        const profile = await api.fetchProfile();
        setUser(profile);
        return profile;
      } catch (error) {
        clearSession();
        if (error instanceof ApiError) {
          throw error;
        }
        throw new ApiError(500, 'Unable to authenticate');
      } finally {
        setPendingAuth(false);
      }
    },
    [clearSession, setToken]
  );

  const login = useCallback(
    (payload: AuthPayload) => authenticate(api.login, payload),
    [authenticate]
  );

  const register = useCallback(
    (payload: AuthPayload) => authenticate(api.register, payload),
    [authenticate]
  );

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loading: initializing || pendingAuth,
      login,
      register,
      logout
    }),
    [user, token, initializing, pendingAuth, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
