"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

type AuthContextValue = {
  session: Session | null;
  user: User | null;
  loading: boolean;
  unavailable: boolean;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signUp: (email: string, password: string, displayName: string) => Promise<{ error: string | null; needsEmailConfirmation: boolean }>;
  signOut: () => Promise<{ error: string | null }>;
  requestPasswordReset: (email: string) => Promise<{ error: string | null }>;
  updatePassword: (password: string) => Promise<{ error: string | null }>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const errorMessage = (error: unknown) => error instanceof Error ? error.message : "Supabase Auth is unavailable right now.";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!supabase) { window.setTimeout(() => setLoading(false), 0); return; }
    let mounted = true;
    void supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setSession(data.session);
      setLoading(false);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setLoading(false);
    });
    return () => { mounted = false; listener.subscription.unsubscribe(); };
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    session,
    user: session?.user ?? null,
    loading,
    unavailable: !supabase,
    signIn: async (email, password) => {
      if (!supabase) return { error: "Supabase Auth is not configured in this environment." };
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      return { error: error?.message ?? null };
    },
    signUp: async (email, password, displayName) => {
      if (!supabase) return { error: "Supabase Auth is not configured in this environment.", needsEmailConfirmation: false };
      const { data, error } = await supabase.auth.signUp({ email, password, options: { data: { display_name: displayName }, emailRedirectTo: `${window.location.origin}/auth/callback` } });
      return { error: error?.message ?? null, needsEmailConfirmation: !data.session && Boolean(data.user) };
    },
    signOut: async () => {
      if (!supabase) return { error: "Supabase Auth is not configured in this environment." };
      const { error } = await supabase.auth.signOut();
      return { error: error?.message ?? null };
    },
    requestPasswordReset: async (email) => {
      if (!supabase) return { error: "Supabase Auth is not configured in this environment." };
      const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo: new URL("/auth/callback?next=%2Fauth%2Freset-password", window.location.origin).toString() });
      return { error: error?.message ?? null };
    },
    updatePassword: async (password) => {
      if (!supabase) return { error: "Supabase Auth is not configured in this environment." };
      const { error } = await supabase.auth.updateUser({ password });
      return { error: error?.message ?? null };
    },
  }), [loading, session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

export { errorMessage };
