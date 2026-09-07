import pandas as pd

from build_recommender import JivanyaRecommender


def check_filter(
    recommender,
    name,
    ingredients,
    **filters,
):
    print("\n" + "=" * 60)
    print(f"TEST: {name}")
    print("=" * 60)

    results = recommender.recommend(
        ingredients=ingredients,
        preference_text="Indian",
        top_n=20,
        **filters,
    )

    if results.empty:
        print("No recommendations returned.")
        return

    print(
        f"Recipes returned: {len(results)}"
    )

    problems = []

    for _, row in results.iterrows():

        if filters.get(
            "vegetarian_only"
        ):
            if not bool(
                row["vegetarian"]
            ):
                problems.append(
                    (
                        row["recipe_name"],
                        "Not verified vegetarian",
                    )
                )

        if filters.get(
            "vegan_only"
        ):
            if not bool(
                row["vegan"]
            ):
                problems.append(
                    (
                        row["recipe_name"],
                        "Not verified vegan",
                    )
                )

        if filters.get(
            "no_onion_no_garlic"
        ):
            if (
                bool(
                    row[
                        "contains_onion"
                    ]
                )
                or bool(
                    row[
                        "contains_garlic"
                    ]
                )
            ):
                problems.append(
                    (
                        row["recipe_name"],
                        (
                            "Contains onion "
                            "or garlic"
                        ),
                    )
                )

    if problems:
        print("\nFAILED")

        for recipe, reason in problems:
            print(
                f"- {recipe}: {reason}"
            )

    else:
        print("PASSED")

    print("\nSample results:")

    for _, row in (
        results.head(5).iterrows()
    ):
        print(
            f"- {row['recipe_name']}"
        )

        print(
            f"  Source diet: "
            f"{row['diet']}"
        )

        print(
            f"  Vegetarian verified: "
            f"{row['vegetarian']}"
        )

        print(
            f"  Vegan verified: "
            f"{row['vegan']}"
        )

        print(
            f"  Onion: "
            f"{row['contains_onion']}"
        )

        print(
            f"  Garlic: "
            f"{row['contains_garlic']}"
        )


def main():

    recommender = (
        JivanyaRecommender()
        .load()
    )

    pantry = [
        "potato",
        "tomato",
        "onion",
        "garlic",
        "ginger",
        "cumin",
        "turmeric",
        "green chilli",
        "coriander leaves",
        "oil",
        "salt",
    ]

    check_filter(
        recommender,
        "Vegetarian filter",
        pantry,
        vegetarian_only=True,
    )

    check_filter(
        recommender,
        "Vegan filter",
        pantry,
        vegan_only=True,
    )

    check_filter(
        recommender,
        "No Onion / No Garlic filter",
        pantry,
        no_onion_no_garlic=True,
    )


if __name__ == "__main__":
    main()
