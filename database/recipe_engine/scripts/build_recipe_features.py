import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

RECIPES_PATH = BASE_DIR / "processed" / "recipes_clean.csv"
INGREDIENTS_PATH = BASE_DIR / "processed" / "recipe_ingredients.csv"

OUTPUT_PATH = BASE_DIR / "processed" / "recipes_features.csv"


# ---------------------------------------------------------
# Ingredient groups
# ---------------------------------------------------------

ONION_INGREDIENTS = {
    "onion",
    "spring onion",
    "shallot",
    "pearl onion",
    "red onion",
    "white onion",
}

GARLIC_INGREDIENTS = {
    "garlic",
    "garlic paste",
    "ginger garlic paste",
}

EGG_INGREDIENTS = {
    "egg",
    "whole egg",
    "whole eggs",
    "egg white",
    "egg whites",
    "egg yolk",
    "egg yolks",
}

DAIRY_INGREDIENTS = {
    "milk",
    "butter",
    "ghee",
    "paneer",
    "yogurt",
    "curd",
    "cream",
    "fresh cream",
    "cheese",
    "mozzarella cheese",
    "cheddar cheese",
    "parmesan cheese",
    "condensed milk",
    "milk powder",
    "buttermilk",
    "khoya",
    "mawa",
}

# ---------------------------------------------------------
# Plant-based ingredients that contain dairy-like words
# ---------------------------------------------------------

PLANT_BASED_DAIRY_ALTERNATIVES = {
    "coconut milk",
    "almond milk",
    "soy milk",
    "soya milk",
    "oat milk",
    "rice milk",
    "cashew milk",

    "coconut yogurt",
    "coconut yoghurt",
    "coconut curd",
    "soy yogurt",
    "soya yogurt",
    "almond yogurt",

    "coconut cream",

    "peanut butter",
    "almond butter",
    "cashew butter",
}

NUT_INGREDIENTS = {
    "almond",
    "almonds",
    "cashew",
    "cashew nuts",
    "walnut",
    "walnuts",
    "peanut",
    "peanuts",
    "pistachio",
    "pistachios",
    "hazelnut",
    "hazelnuts",
}

NON_VEGETARIAN_INGREDIENTS = {
    "chicken",
    "mutton",
    "lamb",
    "beef",
    "pork",
    "fish",
    "prawn",
    "prawns",
    "shrimp",
    "crab",
    "sardine",
    "salmon",
    "tuna",
    "anchovy",
    "anchovies",
}

NON_VEGAN_INGREDIENTS = (
    EGG_INGREDIENTS
    | DAIRY_INGREDIENTS
    | NON_VEGETARIAN_INGREDIENTS
    | {
        "honey",
    }
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def ingredient_matches(ingredient, keywords):
    """
    Match a normalized ingredient against a keyword set.

    Exact matches are preferred, but this also allows phrases such as:
    'red onion' -> onion
    'boneless chicken breast' -> chicken
    """

    ingredient = str(ingredient).strip().lower()

    for keyword in keywords:
        keyword = keyword.lower()

        if ingredient == keyword:
            return True

        if keyword in ingredient.split():
            return True

        if f" {keyword} " in f" {ingredient} ":
            return True

    return False


def is_dairy_ingredient(ingredient):
    """
    Detect real dairy while excluding plant-based alternatives
    such as coconut milk, soy milk and peanut butter.
    """

    ingredient = str(ingredient).strip().lower()

    # Explicit plant-based alternatives are not dairy.
    if ingredient in PLANT_BASED_DAIRY_ALTERNATIVES:
        return False

    # Also allow extra descriptive words around common
    # plant-based alternatives.
    plant_markers = {
        "coconut",
        "almond",
        "soy",
        "soya",
        "oat",
        "cashew",
        "rice",
        "peanut",
    }

    dairy_words = {
        "milk",
        "yogurt",
        "yoghurt",
        "curd",
        "cream",
        "butter",
    }

    words = set(ingredient.split())

    if words & plant_markers and words & dairy_words:
        return False

    return ingredient_matches(
        ingredient,
        DAIRY_INGREDIENTS,
    )


def recipe_has_any(ingredients, keywords):
    return any(
        ingredient_matches(ingredient, keywords)
        for ingredient in ingredients
    )


def normalize_diet(value):
    if pd.isna(value):
        return ""

    return str(value).strip().lower()


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

print("Loading recipe data...")

recipes = pd.read_csv(RECIPES_PATH)
ingredients = pd.read_csv(INGREDIENTS_PATH)

print(f"Recipes loaded: {len(recipes):,}")
print(f"Ingredient rows loaded: {len(ingredients):,}")


# ---------------------------------------------------------
# Group ingredients by recipe
# ---------------------------------------------------------

ingredient_groups = (
    ingredients
    .groupby("recipe_id")["ingredient"]
    .apply(list)
    .to_dict()
)


# ---------------------------------------------------------
# Build features
# ---------------------------------------------------------

feature_rows = []

for _, recipe in recipes.iterrows():

    recipe_id = recipe["recipe_id"]

    recipe_ingredients = ingredient_groups.get(recipe_id, [])

    contains_onion = recipe_has_any(
        recipe_ingredients,
        ONION_INGREDIENTS,
    )

    contains_garlic = recipe_has_any(
        recipe_ingredients,
        GARLIC_INGREDIENTS,
    )

    contains_egg = recipe_has_any(
        recipe_ingredients,
        EGG_INGREDIENTS,
    )

    contains_dairy = any(
    is_dairy_ingredient(ingredient)
    for ingredient in recipe_ingredients
    )

    contains_nuts = recipe_has_any(
        recipe_ingredients,
        NUT_INGREDIENTS,
    )

    contains_non_veg = recipe_has_any(
        recipe_ingredients,
        NON_VEGETARIAN_INGREDIENTS,
    )

    contains_honey = recipe_has_any(
        recipe_ingredients,
        {"honey"},
    )

    contains_non_vegan = (
        contains_dairy
        or contains_egg
        or contains_non_veg
        or contains_honey
    )

    diet = normalize_diet(recipe.get("diet"))

    # -----------------------------------------------------
    # Vegetarian classification
    # -----------------------------------------------------

    if "non vegeterian" in diet or "non vegetarian" in diet:
        vegetarian = False

    elif "eggetarian" in diet:
        vegetarian = False

    elif contains_non_veg or contains_egg:
        vegetarian = False

    elif (
        "vegetarian" in diet
        or "vegan" in diet
        or "no onion no garlic" in diet
    ):
        vegetarian = True

    else:
        vegetarian = not contains_non_veg and not contains_egg

        # -----------------------------------------------------
    # Vegan classification
    # -----------------------------------------------------

    # Vegan is treated conservatively.
    #
    # We only mark a recipe vegan when the source dataset
    # explicitly labels it Vegan AND the parsed ingredients
    # do not contradict that label.
    #
    # Recipes that merely contain no detected dairy/egg/meat
    # are not automatically assumed to be vegan.

    if "vegan" in diet:
        vegan = not contains_non_vegan
    else:
        vegan = False

        # -----------------------------------------------------
    # No onion / no garlic
    # -----------------------------------------------------

    no_onion_no_garlic_by_ingredients = (
        not contains_onion
        and not contains_garlic
    )

    sattvic_source_label = (
        "no onion no garlic" in diet
    )

    feature_rows.append(
        {
            "recipe_id": recipe_id,

            "contains_onion": contains_onion,
            "contains_garlic": contains_garlic,
            "contains_egg": contains_egg,
            "contains_dairy": contains_dairy,
            "contains_nuts": contains_nuts,

            "vegetarian": vegetarian,
            "vegan": vegan,

            "no_onion_no_garlic_by_ingredients":
                no_onion_no_garlic_by_ingredients,

            "sattvic_source_label":
                sattvic_source_label,

            "ingredient_count": len(recipe_ingredients),
        }
    )


features = pd.DataFrame(feature_rows)

# ---------------------------------------------------------
# Merge with recipes
# ---------------------------------------------------------

final_df = recipes.merge(
    features,
    on="recipe_id",
    how="left",
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

final_df.to_csv(
    OUTPUT_PATH,
    index=False,
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\nRecipe feature generation complete.")
print(f"Recipes processed: {len(final_df):,}")

print(
    f"Contains onion: "
    f"{final_df['contains_onion'].sum():,}"
)

print(
    f"Contains garlic: "
    f"{final_df['contains_garlic'].sum():,}"
)

print(
    f"Contains egg: "
    f"{final_df['contains_egg'].sum():,}"
)

print(
    f"Contains dairy: "
    f"{final_df['contains_dairy'].sum():,}"
)

print(
    f"Contains nuts: "
    f"{final_df['contains_nuts'].sum():,}"
)

print(
    f"Vegetarian: "
    f"{final_df['vegetarian'].sum():,}"
)

print(
    f"Vegan: "
    f"{final_df['vegan'].sum():,}"
)

print(
    f"No onion / no garlic by ingredients: "
    f"{final_df['no_onion_no_garlic_by_ingredients'].sum():,}"
)

print(
    f"Source-labelled Sattvic: "
    f"{final_df['sattvic_source_label'].sum():,}"
)

print(
    f"Recipes with zero extracted ingredients: "
    f"{(final_df['ingredient_count'] == 0).sum():,}"
)

print("\nSaved to:")
print(OUTPUT_PATH)
