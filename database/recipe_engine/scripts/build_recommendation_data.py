import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

RECIPES_PATH = BASE_DIR / "processed" / "recipes_features.csv"
INGREDIENTS_PATH = BASE_DIR / "processed" / "recipe_ingredients.csv"

OUTPUT_PATH = BASE_DIR / "processed" / "recipes_recommendation.csv"


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("Loading recipe data...")

recipes = pd.read_csv(RECIPES_PATH)
ingredients = pd.read_csv(INGREDIENTS_PATH)

print(f"Recipes loaded: {len(recipes):,}")
print(f"Ingredient rows loaded: {len(ingredients):,}")


# ---------------------------------------------------------
# Build ingredient sets
# ---------------------------------------------------------

ingredient_groups = (
    ingredients
    .groupby("recipe_id")["ingredient"]
    .apply(
        lambda values: sorted(
            set(
                str(value).strip().lower()
                for value in values
                if pd.notna(value)
                and str(value).strip()
            )
        )
    )
    .to_dict()
)


# ---------------------------------------------------------
# Add recommendation fields
# ---------------------------------------------------------

recipes["ingredient_list"] = recipes["recipe_id"].map(
    ingredient_groups
)

recipes["ingredient_list"] = recipes["ingredient_list"].apply(
    lambda value: value if isinstance(value, list) else []
)

recipes["ingredient_text"] = recipes["ingredient_list"].apply(
    lambda values: " ".join(values)
)

recipes["ingredient_count"] = recipes["ingredient_list"].apply(len)


# ---------------------------------------------------------
# Searchable text
# ---------------------------------------------------------

def safe_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


recipes["search_text"] = (
    recipes["recipe_name"].apply(safe_text)
    + " "
    + recipes["cuisine"].apply(safe_text)
    + " "
    + recipes["course"].apply(safe_text)
    + " "
    + recipes["diet"].apply(safe_text)
    + " "
    + recipes["ingredient_text"]
)


# ---------------------------------------------------------
# Store ingredient list in CSV-safe format
# ---------------------------------------------------------

recipes["ingredient_list"] = recipes["ingredient_list"].apply(
    lambda values: "|".join(values)
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

recipes.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\nRecommendation data preparation complete.")

print(
    f"Recipes processed: "
    f"{len(recipes):,}"
)

print(
    f"Recipes with ingredients: "
    f"{(recipes['ingredient_count'] > 0).sum():,}"
)

print(
    f"Recipes without ingredients: "
    f"{(recipes['ingredient_count'] == 0).sum():,}"
)

print(
    f"Average ingredients per recipe: "
    f"{recipes['ingredient_count'].mean():.2f}"
)

print("\nSaved to:")
print(OUTPUT_PATH)
