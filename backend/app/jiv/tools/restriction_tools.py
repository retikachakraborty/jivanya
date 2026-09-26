from typing import Any, Optional

from sqlalchemy.orm import Session

from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.schemas.tools import CheckRestrictionsInput
from app.jiv.safety.restriction_guard import RestrictionGuard
from app.jiv.tools.base import BaseTool


class CheckRestrictionsTool(BaseTool):
    name = "check_restrictions"
    description = (
        "Deterministically check food ingredients against the user's saved profile restrictions, "
        "including allergies, exclusions, no-onion, no-garlic, and dietary preferences. "
        "Returns explicit SAFE, CONFIRMED CONFLICT, POSSIBLE CONFLICT, or UNKNOWN statuses."
    )
    args_schema = CheckRestrictionsInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        ingredient_ids = kwargs.get("ingredient_ids", [])
        if not ingredient_ids:
            return {
                "overall_status": "UNKNOWN",
                "is_safe": False,
                "ingredients": [],
                "summary": "No ingredients were provided to check.",
            }

        evaluations = []
        has_confirmed_conflict = False
        has_possible_conflict = False
        has_unknown = False

        for item in ingredient_ids:
            res = RestrictionGuard.evaluate_ingredient(db, item, user_profile)
            evaluations.append(res)
            status = res["status"]
            if status == "CONFIRMED CONFLICT":
                has_confirmed_conflict = True
            elif status == "POSSIBLE CONFLICT":
                has_possible_conflict = True
            elif status == "UNKNOWN":
                has_unknown = True

        if has_confirmed_conflict:
            overall_status = "CONFIRMED CONFLICT"
            is_safe = False
        elif has_possible_conflict:
            overall_status = "POSSIBLE CONFLICT"
            is_safe = False
        elif has_unknown:
            overall_status = "UNKNOWN"
            is_safe = False
        else:
            overall_status = "SAFE"
            is_safe = True

        return {
            "overall_status": overall_status,
            "is_safe": is_safe,
            "ingredients": evaluations,
            "summary": (
                f"Evaluation: {overall_status}. "
                + (
                    "Contains hard constraint conflicts with your saved profile."
                    if not is_safe
                    else "All checked ingredients are compatible with your saved profile."
                )
            ),
        }
