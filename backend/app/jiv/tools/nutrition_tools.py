from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.nutrition import FoodItem, IngredientAlias
from app.schemas.nutrition import FoodItemResponse
from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.schemas.tools import LookupNutritionInput
from app.jiv.tools.base import BaseTool


class LookupNutritionTool(BaseTool):
    name = "lookup_nutrition"
    description = (
        "Look up verified scientific nutritional composition from the Indian Food Composition Tables (IFCT 2017). "
        "Returns energy, protein, carbohydrates, fats, fiber, and micronutrients per 100g."
    )
    args_schema = LookupNutritionInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        food_id = kwargs.get("food_id")
        ingredient_name = kwargs.get("ingredient_name")

        target = (food_id or ingredient_name or "").strip().lower()
        if not target:
            return {"status": "INSUFFICIENT_DATA", "matched_food": None, "message": "No food code or ingredient name provided."}

        food: Optional[FoodItem] = None

        # 1. Direct food_id match (e.g. A001, B015)
        if food_id:
            food = db.query(FoodItem).filter(FoodItem.food_id.ilike(target)).first()

        # 2. Check alias mapping table
        canonical = target
        if not food:
            alias_match = db.query(IngredientAlias).filter(IngredientAlias.alias == target).first()
            if alias_match:
                canonical = alias_match.canonical.lower()

        # 3. Match FoodItem by canonical or target name
        if not food:
            food = db.query(FoodItem).filter(FoodItem.food_name.ilike(f"%{canonical}%")).first()

        # 4. Fallback search
        if not food and canonical != target:
            food = db.query(FoodItem).filter(FoodItem.food_name.ilike(f"%{target}%")).first()

        if not food:
            return {
                "status": "NO_DATABASE_MATCH",
                "searched_query": target,
                "canonical_name": canonical if canonical != target else None,
                "matched_food": None,
                "message": f"Food '{target}' was not found in the verified IFCT 2017 database.",
            }

        data = FoodItemResponse.model_validate(food).model_dump()
        return {
            "status": "FOUND",
            "searched_query": target,
            "canonical_name": canonical,
            "matched_food": data,
            "message": f"Retrieved verified IFCT 2017 nutritional data for '{food.food_name}'.",
        }
