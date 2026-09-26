"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Brand } from "./Brand";
import { useAuth } from "./AuthProvider";
import { useProfile } from "./ProfileProvider";

const items = [["⌂", "Home", "/app"], ["◒", "Recipes", "/app/recipes"], ["📅", "Meal Plan", "/app/meal-plan"], ["◌", "Nutrition", "/app/nutrition"], ["▧", "Products", "/app/products"], ["✦", "Jiv", "/app/jiv"], ["○", "Profile", "/app/profile"]] as const;

function Gate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const { profile, profileLoading } = useProfile();
  useEffect(() => {
    if (!authLoading && !user) router.replace("/auth/sign-in");
    else if (!authLoading && !profileLoading && user && (!profile || !profile.onboardingCompleted)) router.replace("/onboarding");
  }, [authLoading, profile, profileLoading, router, user]);
  if (authLoading || profileLoading || !user || !profile?.onboardingCompleted) return <main className="route-loading"><div className="loading-row"><span /><span /><span /></div><p>Preparing your Jivanya kitchen…</p></main>;
  return <>{children}</>;
}

export function AppShell({ children, active }: { children: React.ReactNode; active: string }) {
  const { user } = useAuth();
  const { profile } = useProfile();
  return <Gate><div className="app-bg app-shell"><aside className="sidebar" aria-label="Primary navigation"><Brand compact /><nav className="side-nav">{items.map(([icon, label, href]) => <Link className={active === label ? "active" : ""} href={href} key={label}><span className="nav-icon">{icon}</span><span>{label}</span></Link>)}</nav><div className="sidebar-bottom"><div className="side-profile"><span className="avatar">{profile?.displayName?.charAt(0) || user?.email?.charAt(0).toUpperCase() || "?"}</span><span>{profile?.displayName || user?.email || "Profile"}</span></div></div></aside><div className="main-area"><header className="topbar"><h1>{active}</h1><span className="topbar-note">A calmer way to choose what’s next <span aria-hidden>✦</span></span></header>{children}</div></div></Gate>;
}
