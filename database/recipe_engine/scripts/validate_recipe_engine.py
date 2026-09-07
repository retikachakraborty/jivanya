import pandas as pd


RECIPES_PATH = "database/processed/recipes_recommendation.csv"


def bool_count(df, column):
    return int(
        df[column]
        .fillna(False)
        .astype(bool)
        .sum()
    )


def normalize_name(name):
    return (
        str(name)
        .strip()
        .lower()
    )


def main():
    print("Loading final Jivanya recipe dataset...")

    df = pd.read_csv(RECIPES_PATH)

    print(f"Recipes loaded: {len(df):,}")

    print("\n" + "=" * 60)
    print("1. BASIC DATA QUALITY")
    print("=" * 60)

    print(
        f"Duplicate recipe IDs: "
        f"{df['recipe_id'].duplicated().sum():,}"
    )

    print(
        f"Missing recipe names: "
        f"{df['recipe_name'].isna().sum():,}"
    )

    print(
        f"Missing cuisines: "
        f"{df['cuisine'].isna().sum():,}"
    )

    print(
        f"Missing diet values: "
        f"{df['diet'].isna().sum():,}"
    )

    print(
        f"Missing source URLs: "
        f"{df['source_url'].isna().sum():,}"
    )

    print("\n" + "=" * 60)
    print("2. INGREDIENT COVERAGE")
    print("=" * 60)

    zero_ingredients = df[
        df["ingredient_count"].fillna(0) == 0
    ]

    print(
        f"Recipes with ingredients: "
        f"{len(df) - len(zero_ingredients):,}"
    )

    print(
        f"Recipes with zero ingredients: "
        f"{len(zero_ingredients):,}"
    )

    print(
        f"Average ingredient count: "
        f"{df['ingredient_count'].mean():.2f}"
    )

    print(
        f"Median ingredient count: "
        f"{df['ingredient_count'].median():.0f}"
    )

    print("\n" + "=" * 60)
    print("3. DIETARY FEATURE COUNTS")
    print("=" * 60)

    print(
        f"Verified vegetarian: "
        f"{bool_count(df, 'vegetarian'):,}"
    )

    print(
        f"Verified vegan: "
        f"{bool_count(df, 'vegan'):,}"
    )

    print(
        f"Contains onion: "
        f"{bool_count(df, 'contains_onion'):,}"
    )

    print(
        f"Contains garlic: "
        f"{bool_count(df, 'contains_garlic'):,}"
    )

    print(
        f"No onion/no garlic: "
        f"{bool_count(
            df,
            'no_onion_no_garlic_by_ingredients'
        ):,}"
    )

    print("\n" + "=" * 60)
    print("4. LOGICAL CONSISTENCY")
    print("=" * 60)

    vegan_not_vegetarian = df[
        (df["vegan"] == True)
        & (df["vegetarian"] != True)
    ]

    print(
        f"Vegan but not vegetarian: "
        f"{len(vegan_not_vegetarian):,}"
    )

    vegan_with_dairy = df[
        (df["vegan"] == True)
        & (df["contains_dairy"] == True)
    ]

    print(
        f"Vegan with dairy detected: "
        f"{len(vegan_with_dairy):,}"
    )

    vegan_with_egg = df[
        (df["vegan"] == True)
        & (df["contains_egg"] == True)
    ]

    print(
        f"Vegan with egg detected: "
        f"{len(vegan_with_egg):,}"
    )

    no_og_conflicts = df[
        (
            df[
                "no_onion_no_garlic_by_ingredients"
            ]
            == True
        )
        & (
            (df["contains_onion"] == True)
            | (df["contains_garlic"] == True)
        )
    ]

    print(
        f"No-onion/no-garlic conflicts: "
        f"{len(no_og_conflicts):,}"
    )

    print("\n" + "=" * 60)
    print("5. SOURCE LABEL VS VERIFIED LOGIC")
    print("=" * 60)

    source_vegan = (
        df["diet"]
        .fillna("")
        .str.lower()
        .str.contains("vegan")
    )

    source_vegan_count = int(
        source_vegan.sum()
    )

    source_vegan_rejected = df[
        source_vegan
        & (df["vegan"] != True)
    ]

    print(
        f"Source-labelled Vegan: "
        f"{source_vegan_count:,}"
    )

    print(
        f"Source Vegan rejected by "
        f"ingredient verification: "
        f"{len(source_vegan_rejected):,}"
    )

    source_sattvic = (
        df["sattvic_source_label"]
        .fillna(False)
        .astype(bool)
    )

    sattvic_conflicts = df[
        source_sattvic
        & (
            (df["contains_onion"] == True)
            | (df["contains_garlic"] == True)
        )
    ]

    print(
        f"Source-labelled Sattvic: "
        f"{int(source_sattvic.sum()):,}"
    )

    print(
        f"Source Sattvic with onion/garlic: "
        f"{len(sattvic_conflicts):,}"
    )

    print("\n" + "=" * 60)
    print("6. RECIPE NAME DUPLICATES")
    print("=" * 60)

    normalized_names = (
        df["recipe_name"]
        .fillna("")
        .apply(normalize_name)
    )

    duplicate_names = normalized_names.duplicated(
        keep=False
    )

    print(
        f"Rows with exact case-insensitive "
        f"duplicate recipe names: "
        f"{int(duplicate_names.sum()):,}"
    )

    print(
        f"Unique normalized recipe names: "
        f"{normalized_names.nunique():,}"
    )

    print("\n" + "=" * 60)
    print("7. RECOMMENDATION READINESS")
    print("=" * 60)

    recommendation_ready = df[
        (df["ingredient_count"].fillna(0) > 0)
        & df["recipe_name"].notna()
        & df["search_text"].notna()
    ]

    print(
        f"Recommendation-ready recipes: "
        f"{len(recommendation_ready):,}"
    )

    print(
        f"Not recommendation-ready: "
        f"{len(df) - len(recommendation_ready):,}"
    )

    readiness_percent = (
        len(recommendation_ready)
        / len(df)
        * 100
    )

    print(
        f"Recommendation readiness: "
        f"{readiness_percent:.2f}%"
    )

    print("\n" + "=" * 60)
    print("8. FINAL VALIDATION STATUS")
    print("=" * 60)

    critical_failures = (
        int(df["recipe_id"].duplicated().sum())
        + len(vegan_not_vegetarian)
        + len(vegan_with_dairy)
        + len(vegan_with_egg)
        + len(no_og_conflicts)
    )

    if critical_failures == 0:
        print(
            "PASS: No critical logical "
            "validation failures detected."
        )
    else:
        print(
            f"WARNING: {critical_failures} "
            f"critical validation issues detected."
        )

    print(
        "\nNote: source-label disagreements are "
        "reported separately and do not automatically "
        "count as pipeline failures."
    )


if __name__ == "__main__":
    main()
