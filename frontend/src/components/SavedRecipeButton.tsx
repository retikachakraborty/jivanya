"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/components/AuthProvider";
import { supabase } from "@/lib/supabase";

export function SavedRecipeButton({ recipeId, onSavedChange }: { recipeId: string; onSavedChange?: (saved: boolean) => void }) {
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    if (!user || !supabase) return () => { active = false; };
    void supabase.from("saved_recipes").select("recipe_id").eq("user_id", user.id).eq("recipe_id", recipeId).maybeSingle()
      .then(({ data }) => { if (active) setSaved(Boolean(data)); });
    return () => { active = false; };
  }, [recipeId, user]);

  async function toggle() {
    if (!user || !supabase) return;
    setBusy(true);
    const result = saved
      ? await supabase.from("saved_recipes").delete().eq("user_id", user.id).eq("recipe_id", recipeId)
      : await supabase.from("saved_recipes").upsert({ user_id: user.id, recipe_id: recipeId }, { onConflict: "user_id,recipe_id" });
    if (!result.error) {
      const nextSaved = !saved;
      setSaved(nextSaved);
      onSavedChange?.(nextSaved);
    }
    setBusy(false);
  }

  if (!user) return null;
  return <button type="button" className="outline-link" disabled={busy} onClick={() => void toggle()} aria-pressed={saved}>
    {saved ? "♥ Saved" : "♡ Save recipe"}
  </button>;
}
