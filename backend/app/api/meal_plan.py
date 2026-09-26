import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.recipe import Recipe, RecipeIngredient
from app.api.recipes import _exclusion_predicates, _diet_predicates
from app.schemas.recipe import RecipeItem

router = APIRouter(prefix="/api/v1/meal-plan", tags=["Meal Plan"])

REGIONAL_CUISINE_MAP = {
    "north_indian": ["North Indian Recipes", "Punjabi", "Kashmiri", "Awadhi", "Mughlai", "Bihari", "Himachal", "Haryana", "Indian"],
    "south_indian": ["South Indian Recipes", "Tamil Nadu", "Kerala Recipes", "Karnataka", "Andhra", "Chettinad", "Mangalorean", "Hyderabadi", "Coorg", "Malabar"],
    "bengali": ["Bengali Recipes", "Assamese", "Oriya Recipes", "Jharkhand"],
    "maharashtrian": ["Maharashtrian Recipes", "Konkan", "Malvani", "Goan Recipes"],
    "gujarati": ["Gujarati Recipes"],
    "rajasthani": ["Rajasthani"],
}

MEAL_COURSES = {
    "breakfast": [
        "North Indian Breakfast",
        "South Indian Breakfast",
        "Indian Breakfast",
        "World Breakfast",
        "Brunch",
    ],
    "lunch": [
        "Lunch",
        "Main Course",
        "One Pot Dish",
    ],
    "dinner": [
        "Dinner",
        "Side Dish",
        "Main Course",
        "One Pot Dish",
    ],
    "snack": [
        "Snack",
        "Appetizer",
    ],
}

DAYS_OF_WEEK = [
    ("Monday", "Mon"),
    ("Tuesday", "Tue"),
    ("Wednesday", "Wed"),
    ("Thursday", "Thu"),
    ("Friday", "Fri"),
    ("Saturday", "Sat"),
    ("Sunday", "Sun"),
]

# Aisle categorization keywords for Indian grocery shopping
PRODUCE_TERMS = {
    "onion", "tomato", "potato", "ginger", "garlic", "coriander", "cilantro", "mint", "pudina",
    "green chili", "chilli", "spinach", "palak", "methi", "fenugreek", "capsicum", "bell pepper",
    "carrot", "cucumber", "lemon", "lime", "curry leaves", "cauliflower", "gobi", "cabbage",
    "peas", "matar", "beans", "brinjal", "eggplant", "baingan", "bhindi", "okra", "beetroot",
    "radish", "mooli", "pumpkin", "kaddu", "bottle gourd", "lauki", "zucchini", "mushroom",
}

DAIRY_TERMS = {
    "paneer", "curd", "dahi", "yogurt", "milk", "doodh", "butter", "makhan", "cream", "malai",
    "cheese", "ghee", "tofu", "buttermilk", "chaas", "whey",
}

PULSES_GRAINS_TERMS = {
    "atta", "wheat flour", "flour", "maida", "besan", "gram flour", "rice", "basmati", "poha",
    "flattened rice", "rava", "sooji", "semolina", "oats", "dal", "toor dal", "arhar dal",
    "moong dal", "chana dal", "urad dal", "masoor dal", "rajma", "kidney beans", "chickpeas",
    "chana", "kabuli chana", "quinoa", "millet", "jowar", "bajra", "ragi",
}

SPICE_PANTRY_TERMS = {
    "turmeric", "haldi", "cumin", "jeera", "mustard seeds", "rai", "sarson", "coriander powder",
    "dhania powder", "red chili powder", "kashmiri mirch", "garam masala", "asafoetida", "hing",
    "black pepper", "kali mirch", "cardamom", "elaichi", "clove", "laung", "cinnamon", "dalchini",
    "bay leaf", "tej patta", "kasuri methi", "amchur", "dry mango powder", "chaat masala",
    "salt", "kala namak", "oil", "mustard oil", "sunflower oil", "sesame oil", "sugar", "jaggery",
    "gur", "cashew", "kaju", "almond", "badam", "raisin", "kishmish", "sesame seeds", "til",
}


class MealSlot(BaseModel):
    slot_id: str
    meal_type: str
    recipe: RecipeItem


class DayMealPlan(BaseModel):
    day: str
    day_short: str
    meals: List[MealSlot]


class MealPlanRequest(BaseModel):
    regional_preference: str = "all"
    diet_preference: str = "all"
    no_onion: bool = False
    no_garlic: bool = False
    exclude_allergies: List[str] = []
    include_snack: bool = True
    max_cook_time: Optional[int] = None


class MealPlanResponse(BaseModel):
    days: List[DayMealPlan]
    total_unique_recipes: int


class MealSwapRequest(BaseModel):
    slot_id: str
    meal_type: str
    current_recipe_id: str
    regional_preference: str = "all"
    diet_preference: str = "all"
    no_onion: bool = False
    no_garlic: bool = False
    exclude_allergies: List[str] = []
    exclude_recipe_ids: List[str] = []


class GroceryCategory(BaseModel):
    category_name: str
    icon: str
    items: List[str]


class GroceryListRequest(BaseModel):
    recipe_ids: List[str]


class GroceryListResponse(BaseModel):
    categories: List[GroceryCategory]
    total_items: int


def _recipe_to_item(recipe: Recipe, db: Session) -> RecipeItem:
    # Load structured ingredients
    ingredients = [
        row.ingredient_raw
        for row in db.query(RecipeIngredient.ingredient_raw)
        .filter(RecipeIngredient.recipe_id == recipe.recipe_id)
        .all()
    ]
    if not ingredients and recipe.ingredients_raw:
        ingredients = [i.strip() for i in recipe.ingredients_raw.split(",") if i.strip()]

    return RecipeItem(
        recipe_id=recipe.recipe_id,
        recipe_name=recipe.recipe_name,
        ingredients_raw=recipe.ingredients_raw,
        instructions=recipe.instructions,
        cuisine=recipe.cuisine,
        course=recipe.course,
        diet=recipe.diet,
        prep_minutes=recipe.prep_minutes,
        cook_minutes=recipe.cook_minutes,
        total_minutes=recipe.total_minutes,
        servings=recipe.servings,
        source_url=recipe.source_url,
        ingredients=ingredients,
        matched_ingredients=[],
        matching_count=0,
    )


def _build_recipe_query(
    db: Session,
    meal_type: str,
    regional_pref: str,
    diet_pref: str,
    no_onion: bool,
    no_garlic: bool,
    exclude_allergies: List[str],
    max_cook_time: Optional[int] = None,
):
    query = db.query(Recipe)

    # 1. Course Filter
    courses = MEAL_COURSES.get(meal_type, [])
    if courses:
        query = query.filter(Recipe.course.in_(courses))

    # 2. Regional Cuisine Filter
    if regional_pref != "all" and regional_pref in REGIONAL_CUISINE_MAP:
        cuisines = REGIONAL_CUISINE_MAP[regional_pref]
        query = query.filter(or_(*(Recipe.cuisine.ilike(f"%{c}%") for c in cuisines)))

    # 3. Diet Filter
    if diet_pref != "all" and diet_pref:
        predicates = _diet_predicates([diet_pref])
        if predicates:
            query = query.filter(*predicates)

    # 4. Exclusions (no-onion, no-garlic, allergies)
    excl_predicates = _exclusion_predicates(exclude_allergies, no_onion, no_garlic)
    if excl_predicates:
        query = query.filter(*excl_predicates)

    # 5. Cook Time Limit
    if max_cook_time and max_cook_time > 0:
        query = query.filter(
            or_(
                Recipe.total_minutes <= max_cook_time,
                Recipe.total_minutes == None,
            )
        )

    return query


@router.post("/generate", response_model=MealPlanResponse)
def generate_meal_plan(req: MealPlanRequest, db: Session = Depends(get_db)):
    meal_types = ["breakfast", "lunch", "dinner"]
    if req.include_snack:
        meal_types.append("snack")

    # Fetch candidate pool for each meal type
    candidate_pools: dict[str, list[Recipe]] = {}
    for mt in meal_types:
        q = _build_recipe_query(
            db=db,
            meal_type=mt,
            regional_pref=req.regional_preference,
            diet_pref=req.diet_preference,
            no_onion=req.no_onion,
            no_garlic=req.no_garlic,
            exclude_allergies=req.exclude_allergies,
            max_cook_time=req.max_cook_time,
        )
        items = q.limit(100).all()
        candidate_pools[mt] = items

    used_recipe_ids: set[str] = set()
    days_output: list[DayMealPlan] = []
    for idx, (day_name, day_short) in enumerate(DAYS_OF_WEEK):
        slots: list[MealSlot] = []

        for mt in meal_types:
            pool = candidate_pools.get(mt, [])
            # Filter out recipes already used this week if possible
            fresh_candidates = [r for r in pool if r.recipe_id not in used_recipe_ids]
            chosen_recipe = None
            # Stable rotation makes the same profile/query reproducible and
            # never falls back to a recipe that violates the requested slot.
            ordered_candidates = sorted(fresh_candidates or pool, key=lambda r: (r.recipe_name.lower(), r.recipe_id))
            if ordered_candidates:
                chosen_recipe = ordered_candidates[idx % len(ordered_candidates)]

            if chosen_recipe:
                used_recipe_ids.add(chosen_recipe.recipe_id)
                recipe_item = _recipe_to_item(chosen_recipe, db)

                slot = MealSlot(
                    slot_id=f"{day_short.lower()}-{mt}",
                    meal_type=mt,
                    recipe=recipe_item,
                )
                slots.append(slot)

        days_output.append(
            DayMealPlan(
                day=day_name,
                day_short=day_short,
                meals=slots,
            )
        )

    return MealPlanResponse(
        days=days_output,
        total_unique_recipes=len(used_recipe_ids),
    )


@router.post("/swap", response_model=MealSlot)
def swap_meal_slot(req: MealSwapRequest, db: Session = Depends(get_db)):
    q = _build_recipe_query(
        db=db,
        meal_type=req.meal_type,
        regional_pref=req.regional_preference,
        diet_pref=req.diet_preference,
        no_onion=req.no_onion,
        no_garlic=req.no_garlic,
        exclude_allergies=req.exclude_allergies,
    )
    excluded = set(req.exclude_recipe_ids)
    excluded.add(req.current_recipe_id)

    candidates = q.limit(60).all()
    filtered = [r for r in candidates if r.recipe_id not in excluded]

    if not filtered:
        raise HTTPException(status_code=404, detail="No recipe matches the requested meal slot and restrictions")

    chosen = sorted(filtered, key=lambda r: (r.recipe_name.lower(), r.recipe_id))[0]
    recipe_item = _recipe_to_item(chosen, db)

    return MealSlot(
        slot_id=req.slot_id,
        meal_type=req.meal_type,
        recipe=recipe_item,
    )


@router.post("/grocery-list", response_model=GroceryListResponse)
def generate_grocery_list(req: GroceryListRequest, db: Session = Depends(get_db)):
    if not req.recipe_ids:
        return GroceryListResponse(categories=[], total_items=0)

    # Fetch ingredients for all requested recipes
    rows = (
        db.query(RecipeIngredient.ingredient)
        .filter(RecipeIngredient.recipe_id.in_(req.recipe_ids))
        .distinct()
        .all()
    )
    raw_ingredients = [r[0].strip() for r in rows if r[0] and r[0].strip()]

    # If no structured ingredients found, fallback to ingredients_raw
    if not raw_ingredients:
        recipes = db.query(Recipe.ingredients_raw).filter(Recipe.recipe_id.in_(req.recipe_ids)).all()
        for r in recipes:
            if r[0]:
                for item in r[0].split(","):
                    clean = item.strip().lower()
                    if clean and len(clean) > 2:
                        raw_ingredients.append(clean)

    # Normalize and deduplicate ingredients
    cleaned_items: dict[str, str] = {}
    for item in raw_ingredients:
        norm = re.sub(r"\b(\d+(\.\d+)?\s*(cup|cups|tbsp|tsp|g|kg|ml|pinch|tablespoon|teaspoon|piece|pieces|slice|slices)?)\b", "", item, flags=re.IGNORECASE)
        norm = re.sub(r"[\(\)\[\]]", "", norm).strip().title()
        if norm and len(norm) >= 3:
            cleaned_items[norm.lower()] = norm

    produce: list[str] = []
    dairy: list[str] = []
    pulses_grains: list[str] = []
    spices_pantry: list[str] = []

    for lower_term, display_name in sorted(cleaned_items.items(), key=lambda x: x[1]):
        if any(term in lower_term for term in DAIRY_TERMS):
            dairy.append(display_name)
        elif any(term in lower_term for term in PULSES_GRAINS_TERMS):
            pulses_grains.append(display_name)
        elif any(term in lower_term for term in PRODUCE_TERMS):
            produce.append(display_name)
        elif any(term in lower_term for term in SPICE_PANTRY_TERMS):
            spices_pantry.append(display_name)
        else:
            # General kitchen produce/pantry heuristic
            produce.append(display_name)

    categories = [
        GroceryCategory(category_name="Fresh Produce (Sabzi & Herbs)", icon="🥬", items=produce),
        GroceryCategory(category_name="Dairy & Plant-Based Alternatives", icon="🥛", items=dairy),
        GroceryCategory(category_name="Dals, Grains & Flours", icon="🌾", items=pulses_grains),
        GroceryCategory(category_name="Spices, Oils & Pantry Essentials", icon="🧂", items=spices_pantry),
    ]

    # Filter out empty categories
    active_categories = [c for c in categories if c.items]
    total_count = sum(len(c.items) for c in active_categories)

    return GroceryListResponse(
        categories=active_categories,
        total_items=total_count,
    )
