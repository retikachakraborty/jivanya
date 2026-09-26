from pydantic import BaseModel, Field
from typing import Optional, List

class FoodItemBase(BaseModel):
    food_id: str
    food_name: str
    food_group: Optional[str] = None
    energy_kcal: float
    protein_g: float
    carbohydrate_g: float
    fat_g: float
    fiber_g: float
    calcium_mg: float
    iron_mg: float
    sodium_mg: float
    potassium_mg: float
    vitamin_c_mg: float
    folate_ug: float

class FoodItemResponse(FoodItemBase):
    id: int

    class Config:
        from_attributes = True

class IngredientAliasBase(BaseModel):
    canonical: str
    alias: str

class IngredientAliasResponse(IngredientAliasBase):
    id: int

    class Config:
        from_attributes = True

class NormalizeIngredientRequest(BaseModel):
    ingredient_name: str

class NormalizeIngredientResponse(BaseModel):
    original_input: str
    canonical_name: Optional[str]
    matched_food: Optional[FoodItemResponse] = None

# --- Recipe Calculator Schemas ---

class RecipeIngredientInput(BaseModel):
    name: str = Field(..., description="Ingredient name (e.g., 'toor dal', 'ghee', 'tamatar')")
    amount_g: float = Field(..., gt=0, description="Amount in grams")

class CalculateRecipeRequest(BaseModel):
    recipe_name: str = Field(..., description="Name of the recipe/dish")
    servings: int = Field(1, ge=1, description="Number of servings")
    ingredients: List[RecipeIngredientInput] = Field(..., min_items=1)

class TotalNutrition(BaseModel):
    energy_kcal: float = 0.0
    protein_g: float = 0.0
    carbohydrate_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    sodium_mg: float = 0.0
    potassium_mg: float = 0.0
    vitamin_c_mg: float = 0.0
    folate_ug: float = 0.0

class IngredientNutritionBreakdown(BaseModel):
    ingredient_name: str
    amount_g: float
    canonical_name: Optional[str] = None
    matched_food_id: Optional[str] = None
    matched_food_name: Optional[str] = None
    nutrition: TotalNutrition

class CalculateRecipeResponse(BaseModel):
    recipe_name: str
    servings: int
    total_nutrition: TotalNutrition
    per_serving_nutrition: TotalNutrition
    ingredient_breakdown: List[IngredientNutritionBreakdown]
