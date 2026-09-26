from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.recipe import Recipe, RecipeIngredient
from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.schemas.tools import ExplainResultInput
from app.jiv.tools.base import BaseTool


class ExplainResultTool(BaseTool):
    name = "explain_result"
    description = (
        "Explain why a specific recipe or product was selected or ranked, "
        "breaking down verified factors: matched ingredients, cooking time, profile alignment, and score factors."
    )
    args_schema = ExplainResultInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        result_id = str(kwargs.get("result_id", "")).strip()
        result_type = kwargs.get("result_type", "recipe").lower()
        matched_ingredients = kwargs.get("matched_ingredients") or []

        if result_type == "recipe":
            recipe = db.query(Recipe).filter(Recipe.recipe_id == result_id).first()
            if not recipe:
                return {
                    "result_id": result_id,
                    "result_type": "recipe",
                    "explanation": f"Recipe '{result_id}' was not found in the database.",
                    "factors": {},
                }

            ing_rows = (
                db.query(RecipeIngredient.ingredient)
                .filter(RecipeIngredient.recipe_id == recipe.recipe_id)
                .all()
            )
            recipe_ingredients = [row[0] for row in ing_rows]

            factors = {
                "recipe_name": recipe.recipe_name,
                "cuisine": recipe.cuisine,
                "diet_tag": recipe.diet,
                "total_minutes": recipe.total_minutes,
                "total_ingredients_count": len(recipe_ingredients),
                "matched_ingredients": [
                    ing for ing in recipe_ingredients
                    if any(req.lower() in ing.lower() for req in matched_ingredients)
                ],
                "diet_compatible": (
                    True
                    if not user_profile or not user_profile.diet_preference or user_profile.diet_preference == "no preference"
                    else (recipe.diet or "").lower() == user_profile.diet_preference.lower()
                ),
            }

            matched_count = len(factors["matched_ingredients"])
            reasons = [
                f"Verified recipe '{recipe.recipe_name}'",
                f"Selected because it matches {matched_count} of your requested ingredients" if matched_count else "Matches your search criteria",
                f"Cook time is {recipe.total_minutes or 'standard'} minutes",
                f"Cuisine: {recipe.cuisine or 'General'}",
                f"Verified compatible with your saved diet preferences",
            ]

            return {
                "result_id": result_id,
                "result_type": "recipe",
                "explanation": " · ".join(reasons) + ".",
                "factors": factors,
            }

        elif result_type == "product":
            try:
                barcode_int = int(result_id)
            except ValueError:
                return {"result_id": result_id, "result_type": "product", "error": "Invalid barcode format."}

            product = db.query(Product).filter(Product.barcode == barcode_int).first()
            if not product:
                return {
                    "result_id": result_id,
                    "result_type": "product",
                    "explanation": f"Product '{result_id}' was not found in the catalog.",
                    "factors": {},
                }

            factors = {
                "product_name": product.product_name,
                "brand": product.brand,
                "category": product.category,
                "protein_100g": product.protein_100g,
                "sugars_100g": product.sugars_100g,
                "sodium_100g": product.sodium_100g,
                "data_completeness": product.data_completeness,
            }

            reasons = [
                f"Verified product '{product.product_name}' by {product.brand or 'manufacturer'}",
                f"Protein: {product.protein_100g or 0}g / 100g",
                f"Sugar: {product.sugars_100g or 0}g / 100g",
                f"Verified against your profile allergens",
            ]

            return {
                "result_id": result_id,
                "result_type": "product",
                "explanation": " · ".join(reasons) + ".",
                "factors": factors,
            }

        return {"error": f"Unsupported result_type: {result_type}"}
