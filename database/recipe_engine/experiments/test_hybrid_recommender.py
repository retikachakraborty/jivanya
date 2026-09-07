import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
    if not user_ingredients or not recipe_ingredients:
        return 0.0

    intersection = user_ingredients & recipe_ingredients
    union = user_ingredients | recipe_ingredients

    return len(intersection) / len(union)


def load_data():
    print("Loading recommendation data...")

    df = pd.read_csv(RECIPES_PATH)

    df["search_text"] = (
        df["search_text"]
        .fillna("")
        .astype(str)
    )

    df["recipe_ingredient_set"] = (
        df["ingredient_list"]
        .apply(parse_ingredient_list)
    )

    print(f"Recipes loaded: {len(df):,}")

    return df


def build_tfidf_matrix(df):
    print("Building TF-IDF matrix...")

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
    )

    matrix = vectorizer.fit_transform(
        df["search_text"]
    )

    print(
        f"TF-IDF matrix shape: {matrix.shape}"
    )

    return vectorizer, matrix


def hybrid_recommend(
    df,
    vectorizer,
    matrix,
    user_ingredients,
    query_context="",
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

    results = df.copy()

    # -----------------------------------------------------
    # Dietary filters
    # -----------------------------------------------------

    if vegetarian_only:
        results = results[
            results["vegetarian"] == True
        ]

    if vegan_only:
        results = results[
            results["vegan"] == True
        ]

    if no_onion_no_garlic:
        results = results[
            results[
                "no_onion_no_garlic_by_ingredients"
            ] == True
        ]

    # -----------------------------------------------------
    # Ingredient overlap
    # -----------------------------------------------------

    results["matched_ingredients"] = (
        results["recipe_ingredient_set"]
        .apply(
            lambda recipe_set:
                sorted(user_set & recipe_set)
        )
    )

    results["matched_count"] = (
        results["matched_ingredients"]
        .apply(len)
    )

    results["jaccard_score"] = (
        results["recipe_ingredient_set"]
        .apply(
            lambda recipe_set:
                jaccard_similarity(
                    user_set,
                    recipe_set,
                )
        )
    )

    # User ingredient coverage:
    # What percentage of the ingredients entered
    # by the user appear in this recipe?
    results["user_coverage"] = (
        results["matched_count"]
        / len(user_set)
        if user_set
        else 0.0
    )



    # Pantry coverage:
    # What percentage of the recipe's ingredients
    # does the user already have?
    results["pantry_coverage"] = (
        results["recipe_ingredient_set"]
        .apply(
            lambda recipe_set:
                (
                    len(user_set & recipe_set)
                    / len(recipe_set)
                )
                if recipe_set
                else 0.0
        )
    )

    # -----------------------------------------------------
    # TF-IDF / cosine relevance
    # -----------------------------------------------------

    ingredient_query = " ".join(
        sorted(user_set)
    )

    full_query = (
        ingredient_query
        + " "
        + query_context.strip().lower()
    ).strip()

    query_vector = vectorizer.transform(
        [full_query]
    )

    all_cosine_scores = cosine_similarity(
        query_vector,
        matrix,
    ).flatten()

    # Preserve original dataframe index so the cosine
    # scores stay aligned after dietary filtering.
    cosine_series = pd.Series(
        all_cosine_scores,
        index=df.index,
    )

    results["cosine_score"] = (
        cosine_series.loc[results.index]
    )

    # -----------------------------------------------------
    # Hybrid score
    # -----------------------------------------------------
    #
    # 70% ingredient relevance:
    #     45% Jaccard
    #     25% pantry coverage
    #
    # 30% semantic relevance:
    #     TF-IDF cosine similarity
    #
    # -----------------------------------------------------

    results["hybrid_score"] = (
        0.35 * results["user_coverage"]
        + 0.25 * results["jaccard_score"]
        + 0.20 * results["pantry_coverage"]
        + 0.20 * results["cosine_score"]
    )

    # Remove recipes with no pantry overlap.
    results = results[
        results["matched_count"] > 0
    ]

    # Sort first by hybrid score.
    # matched_count is used as a tie-breaker.
    results = results.sort_values(
        by=[
            "hybrid_score",
            "matched_count",
            "jaccard_score",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    )

    return results.head(top_n)


def main():
    df = load_data()

    vectorizer, matrix = build_tfidf_matrix(
        df
    )

    # -----------------------------------------------------
    # Test pantry
    # -----------------------------------------------------

    user_ingredients = [
        "potato",
        "tomato",
        "onion",
    ]

    query_context = (
        "Indian vegetarian"
    )

    print("\nUser ingredients:")
    print(", ".join(user_ingredients))

    print("\nPreference:")
    print(query_context)

    results = hybrid_recommend(
        df=df,
        vectorizer=vectorizer,
        matrix=matrix,
        user_ingredients=user_ingredients,
        query_context=query_context,
        top_n=10,
        vegetarian_only=True,
    )

    print("\nTop hybrid recommendations:\n")

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
            f"   User coverage: "
            f"{row['user_coverage']:.4f}"
        )
        print(
            f"   Jaccard: "
            f"{row['jaccard_score']:.4f}"
        )

        print(
            f"   Pantry coverage: "
            f"{row['pantry_coverage']:.4f}"
        )

        print(
            f"   Cosine: "
            f"{row['cosine_score']:.4f}"
        )

        print(
            f"   Hybrid score: "
            f"{row['hybrid_score']:.4f}"
        )

        print()


if __name__ == "__main__":
    main()
