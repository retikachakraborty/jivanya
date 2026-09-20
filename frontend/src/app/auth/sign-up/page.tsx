"use client";
import Link from "next/link";
import { useState } from "react";
import { AuthLayout } from "@/components/AuthLayout";
import { Brand } from "@/components/Brand";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/navigation";

export default function SignUp() {
  const router = useRouter(); const { signUp, unavailable } = useAuth();
  const [name, setName] = useState(""); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [loading, setLoading] = useState(false); const [message, setMessage] = useState("");
  async function submit(event: React.FormEvent) { event.preventDefault(); if (password.length < 8) { setMessage("Use a password with at least 8 characters."); return; } setLoading(true); setMessage(""); const result = await signUp(email, password, name); setLoading(false); if (result.error) setMessage(result.error); else if (result.needsEmailConfirmation) setMessage("Check your email to confirm your account, then sign in to continue."); else router.push("/onboarding"); }
  return <AuthLayout topLink={<span>Already have an account? <Link href="/auth/sign-in">Sign in</Link></span>}><Brand /><h2>Start with you.</h2><p>A few preferences help Jivanya keep recommendations personal and safe.</p>{unavailable && <div className="form-message">Supabase Auth is not configured in this environment.</div>}{message && <div className="form-message">{message}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="signup-name">Your name</label><input id="signup-name" className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="What should we call you?" required /></div><div className="field"><label htmlFor="signup-email">Email address</label><input id="signup-email" className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required /></div><div className="field"><label htmlFor="signup-password">Create a password</label><input id="signup-password" className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" required minLength={8} /></div><button className="button button-primary auth-submit" disabled={loading || unavailable}>{loading ? "Creating…" : "Continue to food profile"} <span>→</span></button></form><div className="auth-footer">Already have a profile? <Link href="/auth/sign-in">Sign in instead</Link></div></AuthLayout>;
}
