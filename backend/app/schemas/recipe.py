from pydantic import BaseModel, ConfigDict
from typing import Optional

class RecipeItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    recipe_id: str
    recipe_name: str
    ingredients_raw: Optional[str] = None
    instructions: Optional[str] = None
    cuisine: Optional[str] = None
    course: Optional[str] = None
    diet: Optional[str] = None
    prep_minutes: Optional[int] = None
    cook_minutes: Optional[int] = None
    total_minutes: Optional[int] = None
    servings: Optional[int] = None
    source_url: Optional[str] = None
    ingredients: list[str] = []
    matched_ingredients: list[str] = []
    matching_count: int = 0

class RecipeListResponse(BaseModel):
    items: list[RecipeItem]
    total: int
    offset: int
    limit: int
    status: str = "FOUND"
    ignored_ingredients: list[str] = []

class RecipeMatchRequest(BaseModel):
    ingredients: list[str]
    exclude_ingredients: list[str] = []
    no_onion: bool = False
    no_garlic: bool = False
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    limit: int = 20
