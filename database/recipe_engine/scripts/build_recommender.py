import re
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


RECIPES_PATH = "database/recipe_engine/processed/recipes_recommendation.csv"


def parse_ingredient_list(value):
    if pd.isna(value) or str(value).strip() == "":
        return set()

    return {
        item.strip().lower()
        for item in str(value).split("|")
        if item.strip()
    }


def normalize_recipe_name(name):
    """
    Normalize recipe names for duplicate suppression.

    Example:
    'Tomato Noodle Soup Recipe'
    'Tomato Noodle Soup recipe'

    both become effectively the same normalized name.
    """

    name = str(name).lower().strip()

    name = re.sub(
        r"\(recipe in hindi\)",
        "",
        name,
    )

    name = re.sub(
        r"\brecipe\b",
        "",
        name,
    )

    name = re.sub(
        r"[^a-z0-9\s]",
        " ",
        name,
    )

    name = re.sub(
        r"\s+",
        " ",
        name,
    )

    return name.strip()


def jaccard_similarity(user_set, recipe_set):
    if not user_set or not recipe_set:
        return 0.0

    intersection = user_set & recipe_set
    union = user_set | recipe_set

    return len(intersection) / len(union)


class JivanyaRecommender:
    def __init__(self, recipes_path=RECIPES_PATH):
        self.recipes_path = recipes_path

        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None

    def load(self):
        print("Loading Jivanya recipe data...")

        self.df = pd.read_csv(
            self.recipes_path
        )

        self.df["search_text"] = (
            self.df["search_text"]
            .fillna("")
            .astype(str)
        )

        self.df["recipe_ingredient_set"] = (
            self.df["ingredient_list"]
            .apply(parse_ingredient_list)
        )

        self.df["normalized_recipe_name"] = (
            self.df["recipe_name"]
            .apply(normalize_recipe_name)
        )

        print(
            f"Recipes loaded: "
            f"{len(self.df):,}"
        )

        self._build_tfidf()

        return self

    def _build_tfidf(self):
        print("Building TF-IDF index...")

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
        )

        self.tfidf_matrix = (
            self.vectorizer.fit_transform(
                self.df["search_text"]
            )
        )

        print(
            "TF-IDF matrix shape:",
            self.tfidf_matrix.shape,
        )

    def recommend(
        self,
        ingredients,
        preference_text="",
        top_n=10,
        vegetarian_only=False,
        vegan_only=False,
        no_onion_no_garlic=False,
    ):
        if self.df is None:
            raise RuntimeError(
                "Recommender is not loaded. "
                "Call .load() first."
            )

        user_set = {
            str(item).strip().lower()
            for item in ingredients
            if str(item).strip()
        }

        if not user_set:
            return pd.DataFrame()

        results = self.df.copy()

        # -------------------------------------------------
        # Dietary filters
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Ingredient overlap
        # -------------------------------------------------

        results["matched_ingredients"] = (
            results["recipe_ingredient_set"]
            .apply(
                lambda recipe_set:
                    sorted(
                        user_set
                        & recipe_set
                    )
            )
        )

        results["matched_count"] = (
            results[
                "matched_ingredients"
            ].apply(len)
        )

        results["user_coverage"] = (
            results["matched_count"]
            / len(user_set)
        )

        results["jaccard_score"] = (
            results[
                "recipe_ingredient_set"
            ].apply(
                lambda recipe_set:
                    jaccard_similarity(
                        user_set,
                        recipe_set,
                    )
            )
        )

        results["pantry_coverage"] = (
            results[
                "recipe_ingredient_set"
            ].apply(
                lambda recipe_set:
                    (
                        len(
                            user_set
                            & recipe_set
                        )
                        / len(recipe_set)
                    )
                    if recipe_set
                    else 0.0
            )
        )

        # -------------------------------------------------
        # Missing ingredients
        # -------------------------------------------------

        results["missing_ingredients"] = (
            results[
                "recipe_ingredient_set"
            ].apply(
                lambda recipe_set:
                    sorted(
                        recipe_set
                        - user_set
                    )
            )
        )

        results["missing_count"] = (
            results[
                "missing_ingredients"
            ].apply(len)
        )

        # -------------------------------------------------
        # TF-IDF semantic relevance
        # -------------------------------------------------

        ingredient_query = " ".join(
            sorted(user_set)
        )

        full_query = (
            ingredient_query
            + " "
            + preference_text.strip().lower()
        ).strip()

        query_vector = (
            self.vectorizer.transform(
                [full_query]
            )
        )

        cosine_scores = (
            cosine_similarity(
                query_vector,
                self.tfidf_matrix,
            ).flatten()
        )

        cosine_series = pd.Series(
            cosine_scores,
            index=self.df.index,
        )

        results["cosine_score"] = (
            cosine_series.loc[
                results.index
            ]
        )

        # -------------------------------------------------
        # Final hybrid score
        # -------------------------------------------------

        results["hybrid_score"] = (
            0.35
            * results["user_coverage"]
            + 0.25
            * results["jaccard_score"]
            + 0.20
            * results["pantry_coverage"]
            + 0.20
            * results["cosine_score"]
        )

        # Recipes must match at least one
        # ingredient entered by the user.
        results = results[
            results["matched_count"] > 0
        ]

        # -------------------------------------------------
        # Ranking
        # -------------------------------------------------

        results = results.sort_values(
            by=[
                "hybrid_score",
                "matched_count",
                "missing_count",
                "jaccard_score",
            ],
            ascending=[
                False,
                False,
                True,
                False,
            ],
        )

        # -------------------------------------------------
        # Near-duplicate suppression
        # -------------------------------------------------

        results = results.drop_duplicates(
            subset=[
                "normalized_recipe_name"
            ],
            keep="first",
        )


        # -------------------------------------------------
        # Verified diet label
        # -------------------------------------------------

        def verified_diet_label(row):
            source_diet = str(
                row["diet"]
            ).strip()

            # Never trust a source Vegan label
            # when ingredient verification fails.
            if (
                "vegan"
                in source_diet.lower()
            ):
                if row["vegan"]:
                    return "Vegan"

                if row["vegetarian"]:
                    return "Vegetarian"

                return "Non Vegetarian"

            return source_diet

        results["verified_diet"] = (
            results.apply(
                verified_diet_label,
                axis=1,
            )
        )

        # -------------------------------------------------
        # Final output
        # -------------------------------------------------

        output_columns = [
            "recipe_id",
            "recipe_name",
            "cuisine",
            "course",
            "diet",
            "verified_diet",
            "prep_minutes",
            "cook_minutes",
            "total_minutes",
            "servings",
            "matched_ingredients",
            "matched_count",
            "missing_ingredients",
            "missing_count",
            "user_coverage",
            "jaccard_score",
            "pantry_coverage",
            "cosine_score",
            "hybrid_score",
            "vegetarian",
            "vegan",
            "contains_onion",
            "contains_garlic",
            "source_url",
        ]

        return (
            results[
                output_columns
            ]
            .head(top_n)
            .reset_index(drop=True)
        )


def print_recommendations(results):
    if results.empty:
        print(
            "\nNo matching recipes found."
        )
        return

    print(
        "\nTop Jivanya recommendations:\n"
    )

    for index, row in results.iterrows():
        matched = ", ".join(
            row[
                "matched_ingredients"
            ]
        )

        missing = ", ".join(
            row[
                "missing_ingredients"
            ]
        )

        print(
            f"{index + 1}. "
            f"{row['recipe_name']}"
        )

        print(
            f"   Cuisine: "
            f"{row['cuisine']}"
        )

        print(
            f"   Diet: "
            f"{row['verified_diet']}"
        )

        print(
            f"   Matched: {matched}"
        )

        print(
            f"   Missing: "
            f"{missing}"
        )

        print(
            f"   User coverage: "
            f"{row['user_coverage']:.2%}"
        )

        print(
            f"   Hybrid score: "
            f"{row['hybrid_score']:.4f}"
        )

        print()


def main():
    recommender = (
        JivanyaRecommender()
        .load()
    )

    # Temporary terminal test.
    # Later the backend will pass these
    # values dynamically from the UI.

    user_ingredients = [
        "potato",
        "tomato",
        "onion",
    ]

    results = recommender.recommend(
        ingredients=user_ingredients,
        preference_text=(
            "Indian vegetarian"
        ),
        top_n=10,
        vegetarian_only=True,
    )

    print_recommendations(
        results
    )


if __name__ == "__main__":
    main()
