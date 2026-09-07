import re
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_FILE = (
    BASE_DIR
    / "database"
    / "raw"
    / "recipes"
    / "IndianFoodDatasetCSV.csv"
)

PROCESSED_DIR = BASE_DIR / "database" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RECIPES_OUTPUT = PROCESSED_DIR / "recipes_clean.csv"


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def clean_text(value):
    """Normalize whitespace while preserving the original text."""
    if pd.isna(value):
        return ""

    value = str(value)

    # Replace non-breaking spaces
    value = value.replace("\xa0", " ")

    # Collapse repeated whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def clean_category(value):
    """Clean categorical values such as cuisine/course/diet."""
    value = clean_text(value)

    # Remove invisible BOM / odd whitespace characters
    value = value.replace("\ufeff", "")

    return value.strip()


def create_recipe_id(number):
    """Create stable Jivanya recipe IDs such as R00001."""
    return f"R{int(number):05d}"


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

print("Loading raw recipe dataset...")

df = pd.read_csv(RAW_FILE)

print(f"Raw recipes: {len(df):,}")


# ---------------------------------------------------------
# Create clean recipe table
# ---------------------------------------------------------

recipes = pd.DataFrame()

recipes["recipe_id"] = df["Srno"].apply(create_recipe_id)

recipes["recipe_name"] = (
    df["TranslatedRecipeName"]
    .apply(clean_text)
)

recipes["ingredients_raw"] = (
    df["TranslatedIngredients"]
    .apply(clean_text)
)

recipes["instructions"] = (
    df["TranslatedInstructions"]
    .apply(clean_text)
)

recipes["cuisine"] = (
    df["Cuisine"]
    .apply(clean_category)
)

recipes["course"] = (
    df["Course"]
    .apply(clean_category)
)

recipes["diet"] = (
    df["Diet"]
    .apply(clean_category)
)

recipes["prep_minutes"] = pd.to_numeric(
    df["PrepTimeInMins"],
    errors="coerce"
)

recipes["cook_minutes"] = pd.to_numeric(
    df["CookTimeInMins"],
    errors="coerce"
)

recipes["total_minutes"] = pd.to_numeric(
    df["TotalTimeInMins"],
    errors="coerce"
)

recipes["servings"] = pd.to_numeric(
    df["Servings"],
    errors="coerce"
)

recipes["source_url"] = (
    df["URL"]
    .apply(clean_text)
)


# ---------------------------------------------------------
# Quality flags
# ---------------------------------------------------------

recipes["missing_ingredients"] = (
    recipes["ingredients_raw"] == ""
)

recipes["long_prep_time"] = (
    recipes["prep_minutes"] > 300
)

recipes["large_serving"] = (
    recipes["servings"] > 20
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

recipes.to_csv(
    RECIPES_OUTPUT,
    index=False
)

print("\nCleaning complete.")
print(f"Clean recipes: {len(recipes):,}")
print(
    "Missing ingredients:",
    int(recipes["missing_ingredients"].sum())
)
print(
    "Long prep time (>300 mins):",
    int(recipes["long_prep_time"].sum())
)
print(
    "Large serving (>20):",
    int(recipes["large_serving"].sum())
)

print(f"\nSaved to:\n{RECIPES_OUTPUT}")
