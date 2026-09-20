"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { AuthLayout } from "@/components/AuthLayout";
import { Brand } from "@/components/Brand";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/navigation";

export default function SignIn() {
  const router = useRouter(); const { signIn, unavailable } = useAuth();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [loading, setLoading] = useState(false); const [message, setMessage] = useState("");
  useEffect(() => { const timer = window.setTimeout(() => { if (new URLSearchParams(window.location.search).get("error") === "confirmation") setMessage("We couldn’t confirm that email link. Try the link again or contact the project owner."); }, 0); return () => window.clearTimeout(timer); }, []);
  async function submit(event: React.FormEvent) { event.preventDefault(); setLoading(true); setMessage(""); const result = await signIn(email, password); setLoading(false); if (result.error) setMessage(result.error); else router.push("/app"); }
  return <AuthLayout topLink={<span>New here? <Link href="/auth/sign-up">Create profile</Link></span>}><Brand /><h2>Welcome back.</h2><p>Pick up where you left off, with food that feels like you.</p>{unavailable && <div className="form-message">Supabase Auth is not configured in this environment.</div>}{message && <div className="form-message">{message}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="signin-email">Email address</label><input id="signin-email" className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required /></div><div className="field"><label htmlFor="signin-password">Password</label><input id="signin-password" className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Your password" required /></div><div style={{ textAlign: "right", marginTop: -7, marginBottom: 17 }}><Link className="outline-link" href="/auth/forgot-password">Forgot password?</Link></div><button className="button button-primary auth-submit" disabled={loading || unavailable}>{loading ? "Checking…" : "Sign in"} <span>→</span></button></form><div className="auth-footer">No account yet? <Link href="/auth/sign-up">Create your food profile</Link></div></AuthLayout>;
}
