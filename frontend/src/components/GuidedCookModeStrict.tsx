"use client";

import { useMemo, useState } from "react";
import { Recipe } from "@/lib/api";

function storedSteps(instructions: string | null | undefined): string[] {
  if (!instructions?.trim()) return [];
  const lines = instructions.split(/\r?\n+/).map(line => line.trim()).filter(Boolean);
  if (lines.length > 1) return lines.map(line => line.replace(/^(?:step\s*\d+[:.-]?|\d+[:.-])\s*/i, "").trim()).filter(Boolean);
  return [instructions.trim()];
}

export function GuidedCookMode({ recipe, onClose }: { recipe: Recipe; onClose: () => void }) {
  const steps = useMemo(() => storedSteps(recipe.instructions), [recipe.instructions]);
  const [currentStep, setCurrentStep] = useState(0);
  const [checked, setChecked] = useState<Record<number, boolean>>({});
  return <div className="cook-mode-overlay" role="dialog" aria-modal="true">
    <div className="cook-mode-header"><div className="cook-header-title"><span className="cook-badge">👩‍🍳 Guided Cook Mode</span><h2>{recipe.recipe_name}</h2><small>{[recipe.cuisine, recipe.course].filter(Boolean).join(" · ")}</small></div><button type="button" className="cook-close-btn" onClick={onClose}>Exit ✕</button></div>
    <div className="cook-main-card"><h3>Ingredients</h3>{recipe.ingredients.length ? recipe.ingredients.map((ingredient, index) => <label className="cook-ingredient-row" key={`${ingredient}-${index}`}><input type="checkbox" checked={Boolean(checked[index])} onChange={() => setChecked(previous => ({ ...previous, [index]: !previous[index] }))} /><span>{ingredient}</span></label>) : <p>Ingredients are not available for this recipe record.</p>}<h3>Stored instructions</h3>{!steps.length ? <p>Stored instructions are not available for this recipe, so Guided Cook cannot provide cooking steps.</p> : <div className="cooking-stage"><p className="cook-step-text">Step {currentStep + 1} of {steps.length}</p><p className="cook-step-text">{steps[currentStep]}</p></div>}</div>
    {steps.length > 0 && <div className="cook-mode-footer"><button type="button" className="button button-light cook-nav-btn" disabled={currentStep === 0} onClick={() => setCurrentStep(step => step - 1)}>← Previous</button>{currentStep < steps.length - 1 ? <button type="button" className="button button-primary cook-nav-btn" onClick={() => setCurrentStep(step => step + 1)}>Next Step →</button> : <button type="button" className="button button-primary cook-nav-btn" onClick={onClose}>Finish</button>}</div>}
  </div>;
}
