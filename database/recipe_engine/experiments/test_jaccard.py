import pandas as pd


RECIPES_PATH = "database/processed/recipes_recommendation.csv"


def parse_ingredient_list(value):
    if pd.isna(value) or str(value).strip() == "":
        return set()

    return {
        item.strip().lower()
        for item in str(value).split("|")
        if item.strip()
    }


def jaccard_similarity(user_ingredients, recipe_ingredients):
    """
    Jaccard similarity:

    intersection / union
    """

    if not user_ingredients or not recipe_ingredients:
        return 0.0

    intersection = user_ingredients & recipe_ingredients
    union = user_ingredients | recipe_ingredients

    return len(intersection) / len(union)


def recommend_recipes(
    df,
    user_ingredients,
    top_n=10,
    vegetarian_only=False,
    vegan_only=False,
    no_onion_no_garlic=False,
):
    user_set = {
        ingredient.strip().lower()
        for ingredient in user_ingredients
        if ingredient.strip()
    }

    working = df.copy()

    # -----------------------------------------------------
    # Optional filters
    # -----------------------------------------------------

    if vegetarian_only:
        working = working[
            working["vegetarian"] == True
        ]

    if vegan_only:
        working = working[
            working["vegan"] == True
        ]

    if no_onion_no_garlic:
        working = working[
            working[
                "no_onion_no_garlic_by_ingredients"
            ] == True
        ]

    # -----------------------------------------------------
    # Jaccard score
    # -----------------------------------------------------

    working["recipe_ingredient_set"] = (
        working["ingredient_list"]
        .apply(parse_ingredient_list)
    )

    working["jaccard_score"] = (
        working["recipe_ingredient_set"]
        .apply(
            lambda recipe_set:
                jaccard_similarity(
                    user_set,
                    recipe_set,
                )
        )
    )

    # Number of pantry ingredients actually matched
    working["matched_ingredients"] = (
        working["recipe_ingredient_set"]
        .apply(
            lambda recipe_set:
                sorted(user_set & recipe_set)
        )
    )

    working["matched_count"] = (
        working["matched_ingredients"]
        .apply(len)
    )

    # Ignore recipes with zero overlap
    working = working[
        working["matched_count"] > 0
    ]

    # Prioritize:
    # 1. more matched ingredients
    # 2. higher Jaccard score
    working = working.sort_values(
        by=[
            "matched_count",
            "jaccard_score",
        ],
        ascending=[
            False,
            False,
        ],
    )

    return working.head(top_n)


def main():
    print("Loading recommendation data...")

    df = pd.read_csv(RECIPES_PATH)

    print(f"Recipes loaded: {len(df):,}")

    # -----------------------------------------------------
    # Test pantry
    # -----------------------------------------------------

    user_ingredients = [
        "potato",
        "tomato",
        "onion",
    ]

    print("\nUser ingredients:")
    print(", ".join(user_ingredients))

    results = recommend_recipes(
        df,
        user_ingredients=user_ingredients,
        top_n=10,
    )

    print("\nTop Jaccard recommendations:\n")

    if results.empty:
        print("No matching recipes found.")
        return

    for rank, (_, row) in enumerate(
        results.iterrows(),
        start=1,
    ):
        matched = ", ".join(
            row["matched_ingredients"]
        )

        print(
            f"{rank}. {row['recipe_name']}"
        )

        print(
            f"   Cuisine: {row['cuisine']}"
        )

        print(
            f"   Diet: {row['diet']}"
        )

        print(
            f"   Matched: {matched}"
        )

        print(
            f"   Match count: "
            f"{row['matched_count']}"
        )

        print(
            f"   Jaccard score: "
            f"{row['jaccard_score']:.4f}"
        )

        print()


if __name__ == "__main__":
    main()
