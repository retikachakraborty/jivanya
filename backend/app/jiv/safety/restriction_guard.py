import re
from typing import Optional

from sqlalchemy.orm import Session

from app.api.recipes import (
    _expand_ingredient_terms,
    _ingredient_matches,
    _matches_any,
    _normalize,
    _diet_ingredient_conflict,
)
from app.jiv.schemas.chat import UserProfileSchema


class RestrictionGuard:
    """Deterministic hard-constraint evaluation and safety enforcement."""

    @staticmethod
    def evaluate_ingredient(
        db: Session,
        ingredient: str,
        profile: Optional[UserProfileSchema],
    ) -> dict[str, str | bool]:
        """
        Evaluate a single ingredient against profile constraints.
        Returns status ('SAFE', 'CONFIRMED CONFLICT', 'POSSIBLE CONFLICT', 'UNKNOWN'),
        allowed (bool), and an explainable reason.
        """
        raw = ingredient.strip().lower()
        if not raw:
            return {"ingredient": ingredient, "status": "UNKNOWN", "allowed": False, "reason": "Empty ingredient specified."}

        if not profile:
            return {"ingredient": ingredient, "status": "SAFE", "allowed": True, "reason": "No profile restrictions active."}

        # 1. Check Allergies (Hard constraint)
        if profile.allergies:
            expanded_allergies = _expand_ingredient_terms(db, profile.allergies)
            if _matches_any(raw, expanded_allergies):
                return {
                    "ingredient": ingredient,
                    "status": "CONFIRMED CONFLICT",
                    "allowed": False,
                    "reason": f"'{ingredient}' conflicts with your saved allergy list.",
                }

        # 2. Check Exclusions (Dislikes/Preferences)
        if profile.exclusions:
            expanded_exclusions = _expand_ingredient_terms(db, profile.exclusions)
            if _matches_any(raw, expanded_exclusions):
                return {
                    "ingredient": ingredient,
                    "status": "CONFIRMED CONFLICT",
                    "allowed": False,
                    "reason": f"'{ingredient}' is in your saved exclusion list.",
                }

        # 3. Check No-Onion
        if profile.no_onion and _ingredient_matches(raw, "onion"):
            return {
                "ingredient": ingredient,
                "status": "CONFIRMED CONFLICT",
                "allowed": False,
                "reason": f"'{ingredient}' contains onion, which conflicts with your no-onion preference.",
            }

        # 4. Check No-Garlic
        if profile.no_garlic and _ingredient_matches(raw, "garlic"):
            return {
                "ingredient": ingredient,
                "status": "CONFIRMED CONFLICT",
                "allowed": False,
                "reason": f"'{ingredient}' contains garlic, which conflicts with your no-garlic preference.",
            }

        # 5. Check Diet Preference (vegetarian / vegan)
        if profile.diet_preference and profile.diet_preference != "no preference":
            if _diet_ingredient_conflict(raw, profile.diet_preference):
                return {
                    "ingredient": ingredient,
                    "status": "CONFIRMED CONFLICT",
                    "allowed": False,
                    "reason": f"'{ingredient}' conflicts with your {profile.diet_preference} diet.",
                }

        return {
            "ingredient": ingredient,
            "status": "SAFE",
            "allowed": True,
            "reason": "Compatible with your saved food profile.",
        }

    @classmethod
    def filter_safe_items(
        cls,
        db: Session,
        ingredients: list[str],
        profile: Optional[UserProfileSchema],
    ) -> tuple[list[str], list[dict[str, str | bool]]]:
        """Separate requested ingredients into safe items and rejected items with reasons."""
        safe: list[str] = []
        rejected: list[dict[str, str | bool]] = []

        for ing in ingredients:
            res = cls.evaluate_ingredient(db, ing, profile)
            if res["allowed"]:
                safe.append(ing)
            else:
                rejected.append(res)

        return safe, rejected

    @classmethod
    def enforce_text_safety(
        cls,
        text: str,
        blocked_items: list[str],
        profile: Optional[UserProfileSchema],
    ) -> str:
        """
        Verify that LLM generated text does not falsely suggest or validate blocked items.
        If a violation is found, override with deterministic safety statement.
        """
        if not blocked_items or not profile:
            return text

        for item in blocked_items:
            # Check if LLM claimed the blocked item is safe, okay, or recommended
            norm_item = _normalize(item)
            patterns = [
                rf"\b{norm_item}\s+(?:is|are)\s+(?:fine|okay|safe|allowed|good)\b",
                rf"\b(?:you can|feel free to|try)\s+(?:eat|eating|have|having|using)?\s*{norm_item}\b",
            ]
            for pattern in patterns:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    return (
                        f"⚠️ Deterministic Safety Alert: '{item}' conflicts with your saved food profile "
                        f"(allergies / exclusions). Jiv cannot recommend this item."
                    )

        return text
