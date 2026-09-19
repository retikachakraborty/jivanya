import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "database/market_engine/raw/openfoodfacts/openfoodfacts_india_raw.jsonl"
)

OUTPUT_FILE = Path(
    "database/market_engine/processed/products_india_clean.csv"
)


def clean_text(value):
    if not value:
        return ""

    return " ".join(str(value).split()).strip()


def clean_tags(tags):
    if not tags:
        return ""

    cleaned = []

    for tag in tags:
        tag = str(tag)

        if ":" in tag:
            tag = tag.split(":", 1)[1]

        tag = tag.replace("-", " ").strip()

        if tag:
            cleaned.append(tag)

    return ", ".join(cleaned)


def get_category(categories):
    if not categories:
        return "Other"

    category_text = " ".join(
        str(category).lower()
        for category in categories
    )

    category_mapping = [
        ("peanut-butter", "Peanut Butter"),
        ("peanut butter", "Peanut Butter"),
        ("nut-butter", "Nut Butters"),
        ("nut butter", "Nut Butters"),
        ("muesli", "Muesli"),
        ("oat", "Oats"),
        ("bread", "Bread"),
        ("yogurt", "Yogurt"),
        ("yoghurt", "Yogurt"),
        ("milk", "Milk"),
        ("biscuit", "Biscuits"),
        ("cookie", "Biscuits"),
        ("juice", "Juices"),
        ("fruit juice", "Juices"),
        ("protein", "Protein Foods"),
        ("snack", "Snacks"),
        ("breakfast-cereal", "Breakfast Cereals"),
        ("breakfast cereal", "Breakfast Cereals"),
    ]

    for keyword, category_name in category_mapping:
        if keyword in category_text:
            return category_name

    return "Other"


def safe_number(value):
    try:
        if value is None or value == "":
            return None

        number = float(value)

        if number < 0:
            return None

        return number

    except (ValueError, TypeError):
        return None


def calculate_completeness(row):
    important_fields = [
        "product_name",
        "brand",
        "category",
        "energy_100g",
        "protein_100g",
        "carbohydrates_100g",
        "sugars_100g",
        "fat_100g",
        "saturated_fat_100g",
        "fiber_100g",
        "sodium_100g",
        "ingredients_text",
        "allergens",
        "image_url",
    ]

    available = 0

    for field in important_fields:
        value = row.get(field)

        if value is not None and str(value).strip() != "":
            available += 1

    return round(
        (available / len(important_fields)) * 100,
        2
    )


def process_products():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    products = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line_number, line in enumerate(file, start=1):

            try:
                product = json.loads(line)

            except json.JSONDecodeError:
                print(
                    f"Skipping invalid JSON on line {line_number}"
                )
                continue

            nutriments = product.get(
                "nutriments",
                {}
            )

            categories = product.get(
                "categories_tags",
                []
            )

            last_modified = product.get(
                "last_modified_t"
            )

            if last_modified:
                try:
                    last_updated = datetime.fromtimestamp(
                        int(last_modified),
                        tz=timezone.utc
                    ).isoformat()

                except (
                    ValueError,
                    TypeError,
                    OverflowError
                ):
                    last_updated = ""
            else:
                last_updated = ""

            sodium = safe_number(
                nutriments.get("sodium_100g")
            )

            # Open Food Facts stores sodium in grams per 100g.
            # Convert to milligrams per 100g.
            if sodium is not None:
                sodium = round(
                    sodium * 1000,
                    2
                )

            row = {
                "barcode": clean_text(
                    product.get("code")
                ),

                "product_name": clean_text(
                    product.get("product_name")
                ),

                "brand": clean_text(
                    product.get("brands")
                ),

                "category": get_category(
                    categories
                ),

                "countries": clean_tags(
                    product.get(
                        "countries_tags",
                        []
                    )
                ),

                "energy_100g": safe_number(
                    nutriments.get(
                        "energy-kcal_100g"
                    )
                ),

                "protein_100g": safe_number(
                    nutriments.get(
                        "proteins_100g"
                    )
                ),

                "carbohydrates_100g": safe_number(
                    nutriments.get(
                        "carbohydrates_100g"
                    )
                ),

                "sugars_100g": safe_number(
                    nutriments.get(
                        "sugars_100g"
                    )
                ),

                "fat_100g": safe_number(
                    nutriments.get(
                        "fat_100g"
                    )
                ),

                "saturated_fat_100g": safe_number(
                    nutriments.get(
                        "saturated-fat_100g"
                    )
                ),

                "fiber_100g": safe_number(
                    nutriments.get(
                        "fiber_100g"
                    )
                ),

                "sodium_100g": sodium,

                "ingredients_text": clean_text(
                    product.get(
                        "ingredients_text"
                    )
                ),

                "allergens": clean_tags(
                    product.get(
                        "allergens_tags",
                        []
                    )
                ),

                "labels": clean_tags(
                    product.get(
                        "labels_tags",
                        []
                    )
                ),

                "image_url": clean_text(
                    product.get("image_url")
                ),

                "last_updated": last_updated,
            }

            products.append(row)

    df = pd.DataFrame(products)

    # Remove products without barcode or product name.
    df = df[
        (df["barcode"] != "") &
        (df["product_name"] != "")
    ]

    # Remove duplicate barcodes.
    df = df.drop_duplicates(
        subset=["barcode"],
        keep="first"
    )

    # Remove clearly invalid energy values.
    # Low-energy dairy products can legitimately
    # be below 50 kcal, so only values below 10
    # are treated as clearly invalid.
    df.loc[
        (df["energy_100g"] < 10) |
        (df["energy_100g"] > 900),
        "energy_100g"
    ] = None

    # Sodium is stored as mg/100g.
    # Values above 10,000 mg/100g are treated
    # as clearly invalid source-data values.
    df.loc[
        df["sodium_100g"] > 10000,
        "sodium_100g"
    ] = None

    # Calculate data completeness.
    df["data_completeness"] = df.apply(
        calculate_completeness,
        axis=1
    )

    # Sort by product name.
    df = df.sort_values(
        by="product_name",
        na_position="last"
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 60)
    print("Open Food Facts processing completed")
    print("=" * 60)
    print(f"Raw products: {len(products)}")
    print(f"Clean products: {len(df)}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    print("Category distribution:")
    print(
        df["category"].value_counts()
    )
    print()
    print(
        "Average data completeness:",
        round(
            df["data_completeness"].mean(),
            2
        ),
        "%"
    )


if __name__ == "__main__":
    process_products()
