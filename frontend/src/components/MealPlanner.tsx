"use client";

import React, { useEffect, useState, useMemo, useCallback } from "react";
import {
  generateMealPlan,
  swapMealSlot,
  compileGroceryList,
  MealPlanResponse,
  DayMealPlan,
  MealSlot,
  GroceryCategory,
  Recipe,
} from "@/lib/api";
import { useProfile } from "@/components/ProfileProvider";
import { GuidedCookMode } from "@/components/GuidedCookModeStrict";
import { WhyResult } from "@/components/WhyResult";

const STORAGE_KEY = "jivanya_active_meal_plan";
const GROCERY_CHECKED_KEY = "jivanya_grocery_checked";

const REGIONAL_OPTIONS = [
  { value: "all", label: "Pan-Indian / All Cuisines" },
  { value: "north_indian", label: "North Indian (Punjabi, Awadhi, Mughlai)" },
  { value: "south_indian", label: "South Indian (Tamil, Kerala, Andhra, Karnataka)" },
  { value: "maharashtrian", label: "Maharashtrian & Konkan" },
  { value: "bengali", label: "Bengali & Eastern" },
  { value: "gujarati", label: "Gujarati" },
  { value: "rajasthani", label: "Rajasthani" },
];

const DIET_OPTIONS = [
  { value: "all", label: "All Diets" },
  { value: "vegetarian", label: "Vegetarian" },
  { value: "vegan", label: "Vegan" },
  { value: "diabetic friendly", label: "Diabetic Friendly" },
  { value: "high protein vegetarian", label: "High-Protein Vegetarian" },
];

const MEAL_ICONS: Record<string, string> = {
  breakfast: "🍳",
  lunch: "🍛",
  dinner: "🍲",
  snack: "☕",
};

const MEAL_LABELS: Record<string, string> = {
  breakfast: "Breakfast",
  lunch: "Lunch",
  dinner: "Dinner",
  snack: "Evening Snack",
};

export function MealPlanner() {
  const { profile } = useProfile();

  const [plan, setPlan] = useState<MealPlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedDayIdx, setSelectedDayIdx] = useState<number>(0); // 0..6 or -1 for "Full Week"
  const [swappingSlotId, setSwappingSlotId] = useState<string | null>(null);

  // Preference filters
  const [regionalPref, setRegionalPref] = useState("all");
  const [dietPref, setDietPref] = useState("all");
  const [includeSnack, setIncludeSnack] = useState(true);

  // Modals & drawers
  const [viewingRecipe, setViewingRecipe] = useState<Recipe | null>(null);
  const [cookingRecipe, setCookingRecipe] = useState<Recipe | null>(null);
  const [showGroceryDrawer, setShowGroceryDrawer] = useState(false);
  const [groceryCategories, setGroceryCategories] = useState<GroceryCategory[]>([]);
  const [groceryLoading, setGroceryLoading] = useState(false);
  const [checkedGrocery, setCheckedGrocery] = useState<Record<string, boolean>>({});
  const [copyNotification, setCopyNotification] = useState(false);
  const [showClipboardPreview, setShowClipboardPreview] = useState(false);
  const [copiedText, setCopiedText] = useState("");

  // Sync profile defaults on initial load
  useEffect(() => {
    if (profile?.dietPreference && profile.dietPreference !== "no preference") {
      setDietPref(profile.dietPreference);
    }
  }, [profile]);

  // Load plan from localStorage or generate fresh
  const fetchPlan = useCallback(
    async (overrideParams?: { regional?: string; diet?: string; snack?: boolean }) => {
      setLoading(true);
      setError("");
      try {
        const res = await generateMealPlan({
          regional_preference: overrideParams?.regional ?? regionalPref,
          diet_preference: overrideParams?.diet ?? dietPref,
          no_onion: profile?.noOnion ?? false,
          no_garlic: profile?.noGarlic ?? false,
          exclude_allergies: profile ? [...profile.allergies, ...profile.exclusions] : [],
          include_snack: overrideParams?.snack ?? includeSnack,
        });
        setPlan(res);
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(res));
        } catch {
          // localStorage disabled
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to generate meal plan");
      } finally {
        setLoading(false);
      }
    },
    [regionalPref, dietPref, profile, includeSnack]
  );

  // On mount: try loading from localStorage first
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed?.days?.length === 7) {
          setPlan(parsed);
          return;
        }
      }
    } catch {
      // Ignore cache parse error
    }
    void fetchPlan();
  }, [fetchPlan]);

  // Load checked grocery items from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(GROCERY_CHECKED_KEY);
      if (saved) {
        setCheckedGrocery(JSON.parse(saved));
      }
    } catch {
      // Ignore
    }
  }, []);

  // Swap an individual meal slot
  async function handleSwap(slot: MealSlot, dayIdx: number) {
    if (!plan) return;
    setSwappingSlotId(slot.slot_id);
    try {
      // Gather all current recipe IDs in the week to avoid swapping with a dish already in the plan
      const allIds = plan.days.flatMap(d => d.meals.map(m => m.recipe.recipe_id));

      const newSlot = await swapMealSlot({
        slot_id: slot.slot_id,
        meal_type: slot.meal_type,
        current_recipe_id: slot.recipe.recipe_id,
        regional_preference: regionalPref,
        diet_preference: dietPref,
        no_onion: profile?.noOnion ?? false,
        no_garlic: profile?.noGarlic ?? false,
        exclude_allergies: profile ? [...profile.allergies, ...profile.exclusions] : [],
        exclude_recipe_ids: allIds,
      });

      // Update slot in state
      setPlan(prev => {
        if (!prev) return prev;
        const newDays = prev.days.map((d, dIdx) => {
          if (dIdx !== dayIdx) return d;
          const updatedMeals = d.meals.map(m => (m.slot_id === slot.slot_id ? newSlot : m));
          return {
            ...d,
            meals: updatedMeals,
          };
        });
        const updated = { ...prev, days: newDays };
        try {
          localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
        } catch {}
        return updated;
      });
    } catch (err) {
      alert("Could not swap meal slot: " + (err instanceof Error ? err.message : "Unknown error"));
    } finally {
      setSwappingSlotId(null);
    }
  }

  // Load and open grocery list drawer
  async function handleOpenGrocery() {
    if (!plan) return;
    setShowGroceryDrawer(true);
    setGroceryLoading(true);
    try {
      const allIds = Array.from(new Set(plan.days.flatMap(d => d.meals.map(m => m.recipe.recipe_id))));
      const res = await compileGroceryList(allIds);
      setGroceryCategories(res.categories);
    } catch (err) {
      alert("Failed to compile grocery list: " + (err instanceof Error ? err.message : "Offline"));
    } finally {
      setGroceryLoading(false);
    }
  }

  // Toggle checked grocery item
  function toggleGroceryItem(name: string) {
    setCheckedGrocery(prev => {
      const next = { ...prev, [name]: !prev[name] };
      try {
        localStorage.setItem(GROCERY_CHECKED_KEY, JSON.stringify(next));
      } catch {}
      return next;
    });
  }

  // Toggle all items in a specific category (Select All / Deselect All for Produce, Dairy, Grains, Spices)
  function toggleAllInCategory(cat: GroceryCategory) {
    const allChecked = cat.items.length > 0 && cat.items.every(item => Boolean(checkedGrocery[item]));
    setCheckedGrocery(prev => {
      const next = { ...prev };
      cat.items.forEach(item => {
        next[item] = !allChecked;
      });
      try {
        localStorage.setItem(GROCERY_CHECKED_KEY, JSON.stringify(next));
      } catch {}
      return next;
    });
  }

  // Toggle all items across all categories
  function toggleAllGroceries() {
    const allItems = groceryCategories.flatMap(c => c.items);
    const allChecked = allItems.length > 0 && allItems.every(item => Boolean(checkedGrocery[item]));
    setCheckedGrocery(prev => {
      const next = { ...prev };
      allItems.forEach(item => {
        next[item] = !allChecked;
      });
      try {
        localStorage.setItem(GROCERY_CHECKED_KEY, JSON.stringify(next));
      } catch {}
      return next;
    });
  }

  // Generate formatted shopping list for WhatsApp / Quick-Commerce (Blinkit/Zepto/Instamart)
  function getFormattedGroceryText(): string {
    let text = `🛒 *Jivanya Weekly Grocery List* (7-Day Indian Meal Plan)\n\n`;
    let totalItems = 0;
    groceryCategories.forEach(cat => {
      const needed = cat.items.filter(item => !checkedGrocery[item]);
      if (needed.length > 0) {
        text += `${cat.icon} *${cat.category_name}* (${needed.length}):\n`;
        needed.forEach(item => {
          text += `  • ${item}\n`;
          totalItems++;
        });
        text += `\n`;
      }
    });
    if (totalItems === 0) {
      text += `All items are already checked off in your pantry!\n`;
    } else {
      text += `Total items to get: ${totalItems}\nGenerated with Jivanya Food Intelligence.`;
    }
    return text;
  }

  // Copy shopping list formatted for WhatsApp / Quick-Commerce
  function copyGroceryToClipboard() {
    const text = getFormattedGroceryText();
    setCopiedText(text);

    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text).catch(() => {
        try {
          const ta = document.createElement("textarea");
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          document.execCommand("copy");
          document.body.removeChild(ta);
        } catch (_) {}
      });
    }

    setCopyNotification(true);
    setShowClipboardPreview(true);
    setTimeout(() => setCopyNotification(false), 3000);
  }

  // 1-Click WhatsApp Direct Share (no phone number setup needed)
  function shareViaWhatsApp() {
    const text = getFormattedGroceryText();
    const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank", "noopener,noreferrer");
  }

  const activeDay = useMemo(() => {
    if (!plan || selectedDayIdx < 0 || selectedDayIdx >= plan.days.length) return null;
    return plan.days[selectedDayIdx];
  }, [plan, selectedDayIdx]);

  return (
    <div className="meal-planner-container">
      {/* Top Header */}
      <div className="page-title meal-plan-header">
        <div>
          <p className="eyebrow">Weekly Culinary Intelligence</p>
          <h2>
            Automated 7-Day <em>Indian Meal Planner</em>
          </h2>
          <p>
            No more wondering <em>&ldquo;Aaj kya banaye?&rdquo;</em>. A reproducible recipe schedule
            aligned with your saved food boundaries and the available recipe corpus.
          </p>
        </div>
        <div className="meal-header-actions">
          <button
            type="button"
            className="button button-primary grocery-trigger-btn"
            onClick={handleOpenGrocery}
            disabled={!plan || loading}
          >
            🛒 Weekly Grocery List
          </button>
        </div>
      </div>

      {/* Preferences & Regeneration Bar */}
      <div className="card meal-controls-bar">
        <div className="meal-control-group">
          <label htmlFor="reg-pref">Regional Style:</label>
          <select
            id="reg-pref"
            className="select"
            value={regionalPref}
            onChange={e => {
              setRegionalPref(e.target.value);
              void fetchPlan({ regional: e.target.value });
            }}
          >
            {REGIONAL_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="meal-control-group">
          <label htmlFor="diet-pref">Dietary Target:</label>
          <select
            id="diet-pref"
            className="select"
            value={dietPref}
            onChange={e => {
              setDietPref(e.target.value);
              void fetchPlan({ diet: e.target.value });
            }}
          >
            {DIET_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="meal-control-group checkbox-group">
          <label className="snack-checkbox-label">
            <input
              type="checkbox"
              checked={includeSnack}
              onChange={e => {
                setIncludeSnack(e.target.checked);
                void fetchPlan({ snack: e.target.checked });
              }}
            />
            <span>Include 4 PM Snack ☕</span>
          </label>
        </div>

        <button
          type="button"
          className="button button-light regen-btn"
          onClick={() => void fetchPlan()}
          disabled={loading}
        >
          {loading ? "Planning Week…" : "Regenerate Week ↺"}
        </button>
      </div>

      {error && <p className="form-message" style={{ marginTop: 16 }}>{error}</p>}

      {plan && <div className="meal-week-summary-strip"><div className="summary-pill"><span className="summary-label">Recipes in plan</span><strong>{plan.total_unique_recipes} dishes</strong></div></div>}

      {/* 7-Day Selector Tabs */}
      {plan && (
        <div className="meal-day-tabs" role="tablist">
          {plan.days.map((day, idx) => (
            <button
              key={day.day_short}
              type="button"
              role="tab"
              aria-selected={selectedDayIdx === idx}
              className={`meal-day-tab ${selectedDayIdx === idx ? "active" : ""}`}
              onClick={() => setSelectedDayIdx(idx)}
            >
              <span className="tab-day-name">{day.day_short}</span>
            </button>
          ))}
          <button
            type="button"
            role="tab"
            aria-selected={selectedDayIdx === -1}
            className={`meal-day-tab full-week-tab ${selectedDayIdx === -1 ? "active" : ""}`}
            onClick={() => setSelectedDayIdx(-1)}
          >
            <span className="tab-day-name">Full Week</span>
            <span className="tab-day-metrics">All 7 Days</span>
          </button>
        </div>
      )}

      {/* Main Meal Cards Display */}
      {loading && !plan ? (
        <div className="empty-box" style={{ marginTop: 40 }}>
          <span>◌</span>
          <p>Curating your personalized 7-day Indian meal schedule…</p>
        </div>
      ) : selectedDayIdx >= 0 && activeDay ? (
        /* SINGLE DAY VIEW */
        <div className="meal-day-view">
          <div className="meal-day-header">
            <h3>{activeDay.day}&rsquo;s Menu</h3>
          </div>

          <div className="meal-cards-grid">
            {activeDay.meals.map(slot => (
              <article key={slot.slot_id} className="card meal-slot-card">
                <div className="meal-slot-topline">
                  <span className="meal-type-pill">
                    {MEAL_ICONS[slot.meal_type] || "🍽️"} {MEAL_LABELS[slot.meal_type] || slot.meal_type}
                  </span>
                  <div className="meal-slot-quick-meta">
                    {slot.recipe.total_minutes ? (
                      <span className="meal-time">⏱️ {slot.recipe.total_minutes}m</span>
                    ) : null}
                  </div>
                </div>

                <h4 className="meal-recipe-title">{slot.recipe.recipe_name}</h4>

                <p className="meal-recipe-meta">
                  {[slot.recipe.cuisine, slot.recipe.course, slot.recipe.diet].filter(Boolean).join(" · ")}
                </p>

                <div className="meal-slot-actions">
                  <button
                    type="button"
                    className="button button-primary button-small start-cook-btn"
                    onClick={() => setCookingRecipe(slot.recipe)}
                    title="Open the stored recipe instructions"
                  >
                    Start Cooking
                  </button>

                  <button
                    type="button"
                    className="button button-light button-small swap-btn"
                    onClick={() => handleSwap(slot, selectedDayIdx)}
                    disabled={swappingSlotId === slot.slot_id}
                    title="Swap with another dish from the library"
                  >
                    {swappingSlotId === slot.slot_id ? "Rolling…" : "Swap ↺"}
                  </button>

                  <button
                    type="button"
                    className="outline-link meal-view-link"
                    onClick={() => setViewingRecipe(slot.recipe)}
                  >
                    View Recipe →
                  </button>
                </div>
              </article>
            ))}
          </div>
        </div>
      ) : plan && selectedDayIdx === -1 ? (
        /* FULL WEEK COMPACT GRID */
        <div className="meal-full-week-view">
          {plan.days.map((day, dIdx) => (
            <div key={day.day_short} className="card full-week-day-column">
              <div className="full-week-day-title">
                <h4>{day.day}</h4>
              </div>

              <div className="full-week-slots">
                {day.meals.map(slot => (
                  <div key={slot.slot_id} className="full-week-slot-item">
                    <div className="full-week-slot-header">
                      <span>
                        {MEAL_ICONS[slot.meal_type]} {MEAL_LABELS[slot.meal_type]}
                      </span>
                      <button
                        type="button"
                        className="mini-swap-btn"
                        onClick={() => handleSwap(slot, dIdx)}
                        disabled={swappingSlotId === slot.slot_id}
                        title="Swap dish"
                      >
                        ↺
                      </button>
                    </div>
                    <strong
                      className="full-week-recipe-name"
                      onClick={() => setViewingRecipe(slot.recipe)}
                      title="Click to view recipe details"
                    >
                      {slot.recipe.recipe_name}
                    </strong>
                    <div className="full-week-slot-footer">
                      <small>{slot.recipe.total_minutes ? `${slot.recipe.total_minutes}m` : ""}</small>
                      <button
                        type="button"
                        className="outline-link mini-cook-link"
                        onClick={() => setCookingRecipe(slot.recipe)}
                      >
                        Cook 👩‍🍳
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {/* Grocery List Slide-over Drawer */}
      {showGroceryDrawer && (
        <div className="grocery-drawer-backdrop" onClick={() => setShowGroceryDrawer(false)}>
          <div className="grocery-drawer" onClick={e => e.stopPropagation()}>
            <div className="grocery-drawer-header">
              <div>
                <h3>🛒 Weekly Grocery Shopping List</h3>
                <p>Consolidated ingredients across all 7 days of your meal plan.</p>
              </div>
              <button
                type="button"
                className="outline-link"
                onClick={() => setShowGroceryDrawer(false)}
                aria-label="Close grocery list"
              >
                Close ×
              </button>
            </div>

            <div className="grocery-drawer-actions">
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "center" }}>
                <button
                  type="button"
                  className="button button-small"
                  style={{ background: "#25D366", color: "#fff", border: "none", fontWeight: 700 }}
                  onClick={shareViaWhatsApp}
                  title="Opens WhatsApp directly so you can send this list to family or yourself"
                >
                  💬 Share via WhatsApp
                </button>
                <button
                  type="button"
                  className="button button-primary button-small"
                  onClick={copyGroceryToClipboard}
                  title="Copies list to your computer clipboard so you can paste anywhere"
                >
                  {copyNotification ? "✓ Copied to Clipboard!" : "📋 Copy List (Clipboard)"}
                </button>
                <button
                  type="button"
                  className="button button-secondary button-small"
                  onClick={() => {
                    if (!copiedText) {
                      setCopiedText(getFormattedGroceryText());
                    }
                    setShowClipboardPreview(prev => !prev);
                  }}
                >
                  {showClipboardPreview ? "🙈 Hide Text" : "👀 View Text"}
                </button>
              </div>

              <span className="grocery-tip" style={{ color: "#555" }}>
                🔒 <strong>No account needed:</strong> Jivanya never asks for your phone number or Blinkit login. Clicking <em>Share via WhatsApp</em> opens WhatsApp directly on your device so you can choose any contact to send to.
              </span>

              {copyNotification && (
                <div className="clipboard-success-pill">
                  ✓ Copied to your system clipboard! Press <strong>Ctrl + V</strong> in WhatsApp, Blinkit search, or any notes app to paste.
                </div>
              )}

              {showClipboardPreview && (
                <div className="clipboard-preview-box">
                  <div className="clipboard-preview-header">
                    <span>📋 <strong>Current Clipboard Content:</strong></span>
                    <button
                      type="button"
                      className="clipboard-copy-again-btn"
                      onClick={() => {
                        const text = copiedText || getFormattedGroceryText();
                        navigator?.clipboard?.writeText?.(text);
                        setCopyNotification(true);
                        setTimeout(() => setCopyNotification(false), 2000);
                      }}
                    >
                      Copy Again
                    </button>
                  </div>
                  <textarea
                    className="clipboard-preview-textarea"
                    readOnly
                    rows={8}
                    value={copiedText || getFormattedGroceryText()}
                    onFocus={e => e.target.select()}
                  />
                  <div className="clipboard-preview-footer">
                    <span>💡 Tip: Click inside and press <strong>Ctrl + A</strong> then <strong>Ctrl + C</strong> if you prefer manual copy.</span>
                  </div>
                </div>
              )}

              <span className="grocery-tip">
                Tip: Check off items you already have in your pantry before copying/sharing!
              </span>
            </div>

            {groceryLoading ? (
              <div className="loading-row" style={{ marginTop: 30 }}>
                <span />
                <span />
                <span />
              </div>
            ) : groceryCategories.length > 0 ? (
              <div className="grocery-categories-list">
                <div className="grocery-global-controls">
                  <span className="grocery-global-stats">
                    {(() => {
                      const allItems = groceryCategories.flatMap(c => c.items);
                      const needed = allItems.filter(i => !checkedGrocery[i]).length;
                      return (
                        <>
                          Items to buy: <strong>{needed}</strong> / {allItems.length}
                        </>
                      );
                    })()}
                  </span>
                  <button
                    type="button"
                    className="grocery-global-select-btn"
                    onClick={toggleAllGroceries}
                  >
                    {groceryCategories.flatMap(c => c.items).length > 0 &&
                    groceryCategories.flatMap(c => c.items).every(i => Boolean(checkedGrocery[i]))
                      ? "✕ Deselect All Items"
                      : "✓ Select All Items"}
                  </button>
                </div>

                {groceryCategories.map(cat => {
                  const totalInCat = cat.items.length;
                  const checkedInCat = cat.items.filter(i => checkedGrocery[i]).length;
                  const isCatAllChecked = totalInCat > 0 && checkedInCat === totalInCat;
                  return (
                    <div key={cat.category_name} className="grocery-aisle-block">
                      <div className="aisle-header">
                        <div className="aisle-title-wrap">
                          <h4>
                            {cat.icon} {cat.category_name}
                          </h4>
                          <span className="aisle-counter">
                            {checkedInCat}/{totalInCat} on hand
                          </span>
                        </div>
                        <button
                          type="button"
                          className={`aisle-select-all-btn ${isCatAllChecked ? "selected" : ""}`}
                          onClick={() => toggleAllInCategory(cat)}
                          title={`Toggle all ${cat.category_name} items`}
                        >
                          {isCatAllChecked ? "✕ Deselect" : `✓ Select All`}
                        </button>
                      </div>
                      <div className="aisle-items-grid">
                        {cat.items.map(item => {
                          const isChecked = Boolean(checkedGrocery[item]);
                          return (
                            <label
                              key={item}
                              className={`grocery-item-chip ${isChecked ? "checked" : ""}`}
                            >
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => toggleGroceryItem(item)}
                              />
                              <span>{item}</span>
                            </label>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="empty-box">No ingredients found for the active plan.</p>
            )}
          </div>
        </div>
      )}

      {/* Recipe Details Modal */}
      {viewingRecipe && (
        <div
          className="jiv-modal-backdrop"
          onClick={() => setViewingRecipe(null)}
          role="dialog"
          aria-modal="true"
        >
          <div className="jiv-modal-container" onClick={e => e.stopPropagation()}>
            <div className="section-heading">
              <h3>{viewingRecipe.recipe_name}</h3>
              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                <button
                  type="button"
                  className="button button-primary button-small"
                  onClick={() => {
                    const r = viewingRecipe;
                    setViewingRecipe(null);
                    setCookingRecipe(r);
                  }}
                >
                  Start Cooking
                </button>
                <button className="outline-link" onClick={() => setViewingRecipe(null)}>
                  Close ×
                </button>
              </div>
            </div>

            <p style={{ color: "var(--muted)", marginTop: 4, fontSize: 13 }}>
              {[
                viewingRecipe.cuisine,
                viewingRecipe.course,
                viewingRecipe.total_minutes ? `${viewingRecipe.total_minutes} min` : null,
                viewingRecipe.servings ? `${viewingRecipe.servings} servings` : null,
              ]
                .filter(Boolean)
                .join(" · ")}
            </p>

            <div style={{ marginTop: 14 }}>
              <strong style={{ fontSize: 13, color: "var(--dark)" }}>
                Ingredients ({(viewingRecipe.ingredients || []).length}):
              </strong>
              <div className="tile-tags" style={{ marginTop: 6 }}>
                {(viewingRecipe.ingredients || []).map(item => (
                  <span className="tile-tag" key={item}>
                    {item}
                  </span>
                ))}
              </div>
            </div>

            <h4 style={{ marginTop: 22, marginBottom: 8, fontSize: 14 }}>Instructions</h4>
            <p className="detail-instructions" style={{ fontSize: 13, lineHeight: 1.65 }}>
              {viewingRecipe.instructions || "Instructions are not available for this record."}
            </p>

            <WhyResult />
          </div>
        </div>
      )}

      {/* Guided Cook Mode Overlay */}
      {cookingRecipe && (
        <GuidedCookMode
          recipe={cookingRecipe}
          onClose={() => setCookingRecipe(null)}
        />
      )}
    </div>
  );
}
