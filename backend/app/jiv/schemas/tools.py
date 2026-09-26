from typing import Any, Optional
from pydantic import BaseModel, Field


# 1. Search Recipes
class SearchRecipesInput(BaseModel):
    query: Optional[str] = Field(default=None, description="Free text query for recipe name, course, or cuisine")
    cuisine: Optional[str | list[str]] = Field(default=None, description="One or more exact corpus cuisine values")
    course: Optional[str | list[str]] = Field(default=None, description="One or more exact corpus course values")
    diet: Optional[str] = Field(default=None, description="Diet constraint (e.g., 'vegetarian', 'vegan')")
    ingredients: Optional[list[str]] = Field(default=None, description="Specific ingredients to search for")
    max_time: Optional[int] = Field(default=None, description="Maximum total cooking and preparation minutes")
    health_goal: Optional[str] = Field(default=None, description="Supported ranking preference: healthy or high_protein; no recipe nutrient totals are fabricated")
    no_onion: Optional[bool] = Field(default=None, description="Explicit no-onion constraint")
    no_garlic: Optional[bool] = Field(default=None, description="Explicit no-garlic constraint")
    exclude: Optional[list[str]] = Field(default=None, description="Ingredients or allergens to exclude")
    limit: int = Field(default=20, ge=1, le=100, description="Max recipes to return")
    offset: int = Field(default=0, ge=0, description="Pagination offset")


# 2. Match Recipes
class MatchRecipesInput(BaseModel):
    available_ingredients: list[str] = Field(description="List of ingredients currently available in kitchen")
    cuisine: Optional[str | list[str]] = Field(default=None, description="One or more exact corpus cuisine values")
    max_time: Optional[int] = Field(default=None, description="Maximum total cooking time")
    course: Optional[str | list[str]] = Field(default=None, description="One or more exact corpus course values")
    health_goal: Optional[str] = Field(default=None, description="Supported ranking preference: healthy or high_protein")
    diet: Optional[str] = Field(default=None, description="Diet constraint")
    no_onion: Optional[bool] = Field(default=None, description="Exclude onion")
    no_garlic: Optional[bool] = Field(default=None, description="Exclude garlic")
    exclude: Optional[list[str]] = Field(default=None, description="Excluded ingredients or allergens")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# 3. Lookup Nutrition
class LookupNutritionInput(BaseModel):
    food_id: Optional[str] = Field(default=None, description="IFCT 2017 Food Code (e.g., 'A001') or food item name")
    ingredient_name: Optional[str] = Field(default=None, description="Common food or ingredient name (e.g., 'almond', 'atta', 'curd')")


# 4. Search Products
class SearchProductsInput(BaseModel):
    category: Optional[str] = Field(default=None, description="Product category (e.g., 'oats', 'tea', 'milk', 'snacks')")
    query: Optional[str] = Field(default=None, description="Product name or keywords")
    brand: Optional[str] = Field(default=None, description="Brand name filter")
    sort: Optional[str] = Field(default=None, description="Field to sort by: 'energy', 'protein', 'sugar', 'fat', 'fiber', 'sodium'")
    order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort direction")
    limit: int = Field(default=5, ge=1, le=20)
    offset: int = Field(default=0, ge=0)


# 5. Compare Products
class CompareProductsInput(BaseModel):
    product_ids: list[int] = Field(description="List of 2 to 4 product barcodes to compare")


# 6. Check Restrictions
class CheckRestrictionsInput(BaseModel):
    ingredient_ids: list[str] = Field(description="Ingredient names or IDs to check against profile restrictions")


# 7. Optimize Basket
class OptimizeBasketInput(BaseModel):
    budget: Optional[float] = Field(default=None, description="Optional total budget cap in INR")
    categories: Optional[list[str]] = Field(default=None, description="Target product categories to fill in basket")
    priorities: Optional[list[str]] = Field(default=None, description="Nutrition priorities: 'high_protein', 'low_sugar', 'low_sodium', 'balanced'")
    max_items: int = Field(default=5, ge=1, le=10, description="Target number of items")


# 8. Explain Result
class ExplainResultInput(BaseModel):
    result_id: str = Field(description="Identifier for recipe or product")
    result_type: str = Field(default="recipe", pattern="^(recipe|product)$", description="'recipe' or 'product'")
    matched_ingredients: Optional[list[str]] = Field(default=None, description="Ingredients matched from user request")
    score_components: Optional[dict[str, Any]] = Field(default=None, description="Specific score breakdown components")
