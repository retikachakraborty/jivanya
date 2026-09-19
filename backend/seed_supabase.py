from pathlib import Path
import os

import pandas as pd
from sqlalchemy import create_engine, text


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"


def load_database_url():
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("DATABASE_URL not found in .env")


DATABASE_URL = load_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


FILES = {
    "food_items": ROOT / "database/nutrition_engine/processed/food_nutrition_clean.csv",
    "ingredient_aliases": ROOT / "database/nutrition_engine/processed/ingredient_aliases.csv",
    "recipes": ROOT / "database/recipe_engine/processed/recipes_clean.csv",
    "recipe_ingredients": ROOT / "database/recipe_engine/processed/recipe_ingredients.csv",
    "products": ROOT / "database/market_engine/processed/products_india_clean.csv",
}


def clear_tables():
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                truncate table
                    recipe_ingredients,
                    recipes,
                    ingredient_aliases,
                    food_items,
                    products
                restart identity cascade
                """
            )
        )


def insert_table(table_name, csv_path):
    df = pd.read_csv(csv_path)

    if table_name == "recipes":
        df = df[
            [
                "recipe_id",
                "recipe_name",
                "ingredients_raw",
                "instructions",
                "cuisine",
                "course",
                "diet",
                "prep_minutes",
                "cook_minutes",
                "total_minutes",
                "servings",
                "source_url",
                "missing_ingredients",
                "long_prep_time",
                "large_serving",
            ]
        ]

    elif table_name == "recipe_ingredients":
        df = df[
            [
                "recipe_id",
                "ingredient_raw",
                "ingredient",
            ]
        ]

    elif table_name == "products":
        df = df[
            [
                "barcode",
                "product_name",
                "brand",
                "category",
                "countries",
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
                "labels",
                "image_url",
                "last_updated",
                "data_completeness",
            ]
        ]

    df = df.where(pd.notna(df), None)

    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )

    print(f"{table_name}: imported {len(df):,} rows")


def main():
    print("Connected to Supabase.")
    print("CSV files:")
    for table, path in FILES.items():
        print(f"  {table}: {path}")

    print("\nClearing existing runtime data...")
    clear_tables()

    for table_name, csv_path in FILES.items():
        print(f"\nImporting {table_name}...")
        insert_table(table_name, csv_path)

    print("\nSupabase seed completed successfully.")


if __name__ == "__main__":
    main()
