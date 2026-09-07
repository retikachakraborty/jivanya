import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RECIPES_PATH = "database/processed/recipes_recommendation.csv"


def load_data():
    print("Loading recommendation data...")

    df = pd.read_csv(RECIPES_PATH)

    df["search_text"] = (
        df["search_text"]
        .fillna("")
        .astype(str)
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
        f"TF-IDF matrix shape: "
        f"{matrix.shape}"
    )

    return vectorizer, matrix


def recommend_by_text(
    df,
    vectorizer,
    matrix,
    query,
    top_n=10,
    vegetarian_only=False,
    vegan_only=False,
    no_onion_no_garlic=False,
):
    query_vector = vectorizer.transform(
        [query.lower()]
    )

    scores = cosine_similarity(
        query_vector,
        matrix,
    ).flatten()

    results = df.copy()

    results["cosine_score"] = scores

    # -----------------------------------------------------
    # Optional filters
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

    # Ignore zero similarity
    results = results[
        results["cosine_score"] > 0
    ]

    results = results.sort_values(
        by="cosine_score",
        ascending=False,
    )

    return results.head(top_n)


def main():
    df = load_data()

    vectorizer, matrix = build_tfidf_matrix(
        df
    )

    # -----------------------------------------------------
    # Test query
    # -----------------------------------------------------

    query = (
        "potato tomato onion "
        "Indian vegetarian"
    )

    print("\nSearch query:")
    print(query)

    results = recommend_by_text(
        df=df,
        vectorizer=vectorizer,
        matrix=matrix,
        query=query,
        top_n=10,
        vegetarian_only=True,
    )

    print("\nTop TF-IDF recommendations:\n")

    if results.empty:
        print("No matching recipes found.")
        return

    for rank, (_, row) in enumerate(
        results.iterrows(),
        start=1,
    ):
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
            f"   Cosine score: "
            f"{row['cosine_score']:.4f}"
        )

        print()


if __name__ == "__main__":
    main()
