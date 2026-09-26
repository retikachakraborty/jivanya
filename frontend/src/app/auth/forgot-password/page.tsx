"use client";
import Link from "next/link";
import { useState } from "react";
import { AuthLayout } from "@/components/AuthLayout";
import { useAuth } from "@/components/AuthProvider";

export default function ForgotPassword() {
  const { requestPasswordReset, unavailable } = useAuth(); const [email, setEmail] = useState(""); const [loading, setLoading] = useState(false); const [message, setMessage] = useState(""); const [error, setError] = useState("");
  async function submit(event: React.FormEvent) { event.preventDefault(); setLoading(true); setError(""); const result = await requestPasswordReset(email); setLoading(false); if (result.error) setError(result.error); else setMessage("If an account exists for that address, check your email for a reset link."); }
  return <AuthLayout topLink={<Link href="/auth/sign-in">← Back to sign in</Link>}><h2>Find your way back.</h2><p>We’ll send a Supabase password reset link to your email.</p>{unavailable && <div className="form-message">Supabase Auth is not configured in this environment.</div>}{message && <div className="form-message success-message">{message}</div>}{error && <div className="form-message">{error}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="reset-email">Email address</label><input id="reset-email" className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required /></div><button className="button button-primary auth-submit" disabled={loading || unavailable}>{loading ? "Sending…" : "Request reset link"} <span>→</span></button></form><div className="auth-footer"><Link href="/auth/sign-in">Remembered your password? Sign in</Link></div></AuthLayout>;
}
