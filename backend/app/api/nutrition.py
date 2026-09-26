from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.nutrition import FoodItem, IngredientAlias
from app.schemas.nutrition import (
    CalculateRecipeRequest,
    CalculateRecipeResponse,
    FoodItemResponse,
    IngredientNutritionBreakdown,
    NormalizeIngredientRequest,
    NormalizeIngredientResponse,
    TotalNutrition,
)

router = APIRouter(prefix="/api/v1/nutrition", tags=["Nutrition Engine"])


@router.get("/foods", response_model=List[FoodItemResponse])
def search_foods(
    query: Optional[str] = Query(None, description="Search query for food name"),
    group: Optional[str] = Query(None, description="Filter by food group"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search real IFCT food-composition records."""
    statement = db.query(FoodItem)
    if query:
        statement = statement.filter(FoodItem.food_name.ilike(f"%{query}%"))
    if group:
        statement = statement.filter(FoodItem.food_group.ilike(f"%{group}%"))
    return statement.order_by(FoodItem.food_name.asc()).limit(limit).all()


@router.get("/foods/{food_id}", response_model=FoodItemResponse)
def get_food_by_id(food_id: str, db: Session = Depends(get_db)):
    """Get one real IFCT food-composition record."""
    food = db.query(FoodItem).filter(FoodItem.food_id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")
    return food


@router.post("/normalize", response_model=NormalizeIngredientResponse)
def normalize_ingredient(
    payload: NormalizeIngredientRequest,
    db: Session = Depends(get_db),
):
    """Resolve an ingredient alias to a database-backed IFCT food record."""
    raw_input = payload.ingredient_name.strip().lower()
    if not raw_input:
        raise HTTPException(status_code=400, detail="Ingredient name cannot be empty")

    canonical_target = raw_input
    alias_match = db.query(IngredientAlias).filter(IngredientAlias.alias == raw_input).first()
    if alias_match:
        canonical_target = alias_match.canonical

    matched_food = db.query(FoodItem).filter(
        FoodItem.food_name.ilike(f"%{canonical_target}%")
    ).first()
    if not matched_food and canonical_target != raw_input:
        matched_food = db.query(FoodItem).filter(
            FoodItem.food_name.ilike(f"%{raw_input}%")
        ).first()

    return NormalizeIngredientResponse(
        original_input=payload.ingredient_name,
        canonical_name=canonical_target if matched_food or alias_match else None,
        matched_food=matched_food,
    )


@router.post("/calculate-recipe", response_model=CalculateRecipeResponse)
def calculate_recipe_nutrition(
    payload: CalculateRecipeRequest,
    db: Session = Depends(get_db),
):
    """Calculate nutrition only from supplied quantities and real IFCT records."""
    total = TotalNutrition()
    breakdown: List[IngredientNutritionBreakdown] = []

    for ingredient in payload.ingredients:
        normalized = normalize_ingredient(
            NormalizeIngredientRequest(ingredient_name=ingredient.name), db=db
        )
        food = normalized.matched_food
        factor = ingredient.amount_g / 100.0
        item = TotalNutrition()

        if food:
            item.energy_kcal = round(food.energy_kcal * factor, 2)
            item.protein_g = round(food.protein_g * factor, 2)
            item.carbohydrate_g = round(food.carbohydrate_g * factor, 2)
            item.fat_g = round(food.fat_g * factor, 2)
            item.fiber_g = round(food.fiber_g * factor, 2)
            item.calcium_mg = round(food.calcium_mg * factor, 2)
            item.iron_mg = round(food.iron_mg * factor, 2)
            item.sodium_mg = round(food.sodium_mg * factor, 2)
            item.potassium_mg = round(food.potassium_mg * factor, 2)
            item.vitamin_c_mg = round(food.vitamin_c_mg * factor, 2)
            item.folate_ug = round(food.folate_ug * factor, 2)
            for field in item.model_fields:
                setattr(total, field, getattr(total, field) + getattr(item, field))

        breakdown.append(IngredientNutritionBreakdown(
            ingredient_name=ingredient.name,
            amount_g=ingredient.amount_g,
            canonical_name=normalized.canonical_name,
            matched_food_id=food.food_id if food else None,
            matched_food_name=food.food_name if food else None,
            nutrition=item,
        ))

    for field in total.model_fields:
        setattr(total, field, round(getattr(total, field), 2))
    servings = payload.servings
    per_serving = TotalNutrition(**{
        field: round(getattr(total, field) / servings, 2)
        for field in total.model_fields
    })
    return CalculateRecipeResponse(
        recipe_name=payload.recipe_name,
        servings=servings,
        total_nutrition=total,
        per_serving_nutrition=per_serving,
        ingredient_breakdown=breakdown,
    )
