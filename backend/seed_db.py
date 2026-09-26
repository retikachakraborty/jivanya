import csv
import os
import sys

# Add app directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, SessionLocal, Base
from app.models.nutrition import FoodItem, IngredientAlias

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    seed_dir = os.path.join(project_root, "database", "nutrition_engine", "processed")
    clean_csv_path = os.path.join(seed_dir, "food_nutrition_clean.csv")
    aliases_csv_path = os.path.join(seed_dir, "ingredient_aliases.csv")
    
    if not os.path.exists(clean_csv_path) or not os.path.exists(aliases_csv_path):
        print("Seed files not found! Please run data generation script first.")
        return

    # Seed FoodItems
    existing_foods = db.query(FoodItem).count()
    if existing_foods == 0:
        print("Seeding FoodItem records from food_nutrition_clean.csv...")
        with open(clean_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            food_objects = []
            for row in reader:
                food_objects.append(FoodItem(
                    food_id=row["food_id"],
                    food_name=row["food_name"],
                    food_group=row["food_group"],
                    energy_kcal=float(row["energy_kcal"]),
                    protein_g=float(row["protein_g"]),
                    carbohydrate_g=float(row["carbohydrate_g"]),
                    fat_g=float(row["fat_g"]),
                    fiber_g=float(row["fiber_g"]),
                    calcium_mg=float(row["calcium_mg"]),
                    iron_mg=float(row["iron_mg"]),
                    sodium_mg=float(row["sodium_mg"]),
                    potassium_mg=float(row["potassium_mg"]),
                    vitamin_c_mg=float(row["vitamin_c_mg"]),
                    folate_ug=float(row["folate_ug"])
                ))
            db.bulk_save_objects(food_objects)
            db.commit()
            print(f"Successfully seeded {len(food_objects)} FoodItem records!")
    else:
        print(f"FoodItem table already seeded ({existing_foods} records). Skipping.")

    # Seed IngredientAliases
    existing_aliases = db.query(IngredientAlias).count()
    if existing_aliases == 0:
        print("Seeding IngredientAlias records from ingredient_aliases.csv...")
        with open(aliases_csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            alias_objects = []
            for row in reader:
                alias_objects.append(IngredientAlias(
                    canonical=row["canonical"].strip().lower(),
                    alias=row["alias"].strip().lower()
                ))
            db.bulk_save_objects(alias_objects)
            db.commit()
            print(f"Successfully seeded {len(alias_objects)} IngredientAlias records!")
    else:
        print(f"IngredientAlias table already seeded ({existing_aliases} records). Skipping.")

    db.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
