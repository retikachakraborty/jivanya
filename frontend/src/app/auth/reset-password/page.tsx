"use client";
import Link from "next/link";
import { useState } from "react";
import { AuthLayout } from "@/components/AuthLayout";
import { useAuth } from "@/components/AuthProvider";
import { useRouter } from "next/navigation";

export default function ResetPassword() {
  const router = useRouter(); const { updatePassword, unavailable } = useAuth(); const [password, setPassword] = useState(""); const [loading, setLoading] = useState(false); const [message, setMessage] = useState(""); const [error, setError] = useState("");
  async function submit(event: React.FormEvent) { event.preventDefault(); if (password.length < 8) { setError("Use a password with at least 8 characters."); return; } setLoading(true); setError(""); const result = await updatePassword(password); setLoading(false); if (result.error) setError(result.error); else { setMessage("Your password was updated. You can sign in with it now."); setTimeout(() => router.push("/auth/sign-in"), 900); } }
  return <AuthLayout topLink={<Link href="/auth/sign-in">← Back to sign in</Link>}><h2>Set a new password.</h2><p>Choose a new password for your Jivanya account.</p>{message && <div className="form-message success-message">{message}</div>}{error && <div className="form-message">{error}</div>}<form onSubmit={submit}><div className="field"><label htmlFor="new-password">New password</label><input id="new-password" className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} minLength={8} required /></div><button className="button button-primary auth-submit" disabled={loading || unavailable}>{loading ? "Updating…" : "Update password"} <span>→</span></button></form></AuthLayout>;
}
