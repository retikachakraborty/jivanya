"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { supabase } from "@/lib/supabase";
import type { DietPreference, JivanyaProfile, ProfilePatch } from "@/lib/profile";

type ProfileContextValue = {
  profile: JivanyaProfile | null;
  profileLoading: boolean;
  profileError: string | null;
  saveProfile: (draft: ProfilePatch & { displayName: string }) => Promise<{ error: string | null }>;
  updateProfile: (patch: ProfilePatch) => Promise<{ error: string | null }>;
  reloadProfile: () => Promise<void>;
};
const ProfileContext = createContext<ProfileContextValue | undefined>(undefined);

type ProfileRow = { id: string; display_name: string | null; onboarding_completed: boolean; dietary_preference: string | null; no_onion: boolean; no_garlic: boolean; cuisine_preferences: string[] | null };
type IngredientRow = { ingredient: string };
const diet = (value: string | null): DietPreference => value === "vegetarian" || value === "vegan" || value === "diabetic friendly" ? value : "no preference";
const booleanValue = (value: boolean | string | number | null | undefined) => value === true || value === 1 || (typeof value === "string" && value.trim().toLowerCase() === "true");

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [profile, setProfile] = useState<JivanyaProfile | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState<string | null>(null);

  const reloadProfile = useCallback(async () => {
    if (!user || !supabase) { setProfile(null); setProfileLoading(false); return; }
    setProfileLoading(true); setProfileError(null);
    const { data: row, error } = await supabase.from("profiles").select("id,display_name,onboarding_completed,dietary_preference,no_onion,no_garlic,cuisine_preferences").eq("id", user.id).maybeSingle<ProfileRow>();
    if (error) { setProfile(null); setProfileError("Your profile tables are not available yet. Apply the local profile migration in Supabase first."); setProfileLoading(false); return; }
    if (!row) { setProfile(null); setProfileLoading(false); return; }
    const [allergiesResult, exclusionsResult] = await Promise.all([
      supabase.from("profile_allergies").select("ingredient").eq("user_id", user.id),
      supabase.from("profile_exclusions").select("ingredient").eq("user_id", user.id),
    ]);
    if (allergiesResult.error || exclusionsResult.error) {
      setProfile(null);
      setProfileError("Saved profile restrictions could not be loaded. Check your connection and try again.");
      setProfileLoading(false);
      return;
    }
    setProfile({ id: row.id, displayName: row.display_name || user.user_metadata.display_name || "", onboardingCompleted: booleanValue(row.onboarding_completed), dietPreference: diet(row.dietary_preference), allergies: (allergiesResult.data as IngredientRow[] | null)?.map((item) => item.ingredient.trim().toLowerCase()).filter(Boolean) ?? [], exclusions: (exclusionsResult.data as IngredientRow[] | null)?.map((item) => item.ingredient.trim().toLowerCase()).filter(Boolean) ?? [], noOnion: booleanValue(row.no_onion), noGarlic: booleanValue(row.no_garlic), cuisinePreferences: row.cuisine_preferences ?? [] });
    setProfileLoading(false);
  }, [user]);

  useEffect(() => { const timer = window.setTimeout(() => { void reloadProfile(); }, 0); return () => window.clearTimeout(timer); }, [reloadProfile]);

  const saveProfile = useCallback(async (draft: ProfilePatch & { displayName: string }) => {
    if (!user || !supabase) return { error: "You must be signed in before saving a profile." };
    const client = supabase;
    const values = (items: string[]) => [...new Set(items.map((ingredient) => ingredient.trim().toLowerCase()).filter(Boolean))];
    const allergies = values(draft.allergies ?? profile?.allergies ?? []);
    const exclusions = values(draft.exclusions ?? profile?.exclusions ?? []);
    const [previousAllergies, previousExclusions] = await Promise.all([
      client.from("profile_allergies").select("ingredient").eq("user_id", user.id),
      client.from("profile_exclusions").select("ingredient").eq("user_id", user.id),
    ]);
    if (previousAllergies.error || previousExclusions.error) {
      return { error: previousAllergies.error?.message ?? previousExclusions.error?.message ?? "Could not read saved restrictions." };
    }

    const completed = draft.onboardingCompleted ?? profile?.onboardingCompleted ?? false;
    const { error: profileError } = await client.from("profiles").upsert({
      id: user.id,
      display_name: draft.displayName.trim(),
      onboarding_completed: profile?.onboardingCompleted ?? false,
      dietary_preference: draft.dietPreference ?? profile?.dietPreference ?? "no preference",
      no_onion: draft.noOnion ?? profile?.noOnion ?? false,
      no_garlic: draft.noGarlic ?? profile?.noGarlic ?? false,
      cuisine_preferences: draft.cuisinePreferences ?? profile?.cuisinePreferences ?? [],
    }, { onConflict: "id" });
    if (profileError) return { error: profileError.message };

    const sync = async (
      table: "profile_allergies" | "profile_exclusions",
      next: string[],
      previous: { ingredient: string }[],
    ) => {
      if (next.length) {
        const inserted = await client.from(table).upsert(
          next.map((ingredient) => ({ user_id: user.id, ingredient })),
          { onConflict: "user_id,ingredient", ignoreDuplicates: true },
        );
        if (inserted.error) return inserted.error.message;
      }
      const removed = await Promise.all(previous
        .filter(({ ingredient }) => !next.includes(ingredient.trim().toLowerCase()))
        .map(({ ingredient }) => client.from(table).delete().eq("user_id", user.id).eq("ingredient", ingredient)));
      return removed.find((result) => result.error)?.error?.message ?? null;
    };

    const allergyError = await sync("profile_allergies", allergies, previousAllergies.data ?? []);
    if (allergyError) return { error: allergyError };
    const exclusionError = await sync("profile_exclusions", exclusions, previousExclusions.data ?? []);
    if (exclusionError) return { error: exclusionError };

    const { error: completionError } = await client.from("profiles").update({ onboarding_completed: completed }).eq("id", user.id);
    if (completionError) return { error: completionError.message };
    await reloadProfile();
    return { error: null };
  }, [profile, reloadProfile, user]);

  const updateProfile = useCallback((patch: ProfilePatch) => {
    if (!profile) return Promise.resolve({ error: "Create your food profile first." });
    return saveProfile({ ...profile, ...patch });
  }, [profile, saveProfile]);

  const value = useMemo(() => ({ profile, profileLoading, profileError, saveProfile, updateProfile, reloadProfile }), [profile, profileError, profileLoading, reloadProfile, saveProfile, updateProfile]);
  return <ProfileContext.Provider value={value}>{children}</ProfileContext.Provider>;
}
export function useProfile() { const context = useContext(ProfileContext); if (!context) throw new Error("useProfile must be used inside ProfileProvider"); return context; }
