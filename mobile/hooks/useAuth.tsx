/**
 * hooks/useAuth.ts
 * Global auth state using React Context + SecureStore.
 * Wrap the app root in <AuthProvider> then call useAuth() anywhere.
 */
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { authApi, User } from '../lib/api';
import { clearToken, loadCurrentUser, saveToken } from '../lib/auth';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isSignedIn: boolean;
  signIn: (email: string, otp: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Boot: check for stored token
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const currentUser = await loadCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Failed to load the current user during auth initialization.', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    void initializeAuth();
  }, []);

  const signIn = useCallback(async (email: string, otp: string) => {
    const { data } = await authApi.verifyOtp(email, otp);
    await saveToken(data.access_token);
    const { data: me } = await authApi.getMe();
    setUser(me);
  }, []);

  const signOut = useCallback(async () => {
    await clearToken();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const { data } = await authApi.getMe();
    setUser(data);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isSignedIn: !!user, signIn, signOut, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
