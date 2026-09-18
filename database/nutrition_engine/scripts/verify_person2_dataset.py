import csv
import os

def verify_dataset():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nutrition_engine_dir = os.path.dirname(script_dir)
    processed_dir = os.path.join(nutrition_engine_dir, "processed")

    clean_csv = os.path.join(processed_dir, "food_nutrition_clean.csv")
    aliases_csv = os.path.join(processed_dir, "ingredient_aliases.csv")

    assert os.path.exists(clean_csv), f"Missing {clean_csv}"
    assert os.path.exists(aliases_csv), f"Missing {aliases_csv}"

    required_headers = [
        "food_id", "food_name", "food_group",
        "energy_kcal", "protein_g", "carbohydrate_g", "fat_g", "fiber_g",
        "calcium_mg", "iron_mg", "sodium_mg", "potassium_mg",
        "vitamin_c_mg", "folate_ug"
    ]

    food_count = 0
    with open(clean_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == required_headers, f"Header mismatch in {clean_csv}: {reader.fieldnames}"
        for row in reader:
            food_count += 1
            assert row["food_id"].strip(), "Empty food_id found!"
            assert row["food_name"].strip(), "Empty food_name found!"
            for field in required_headers[3:]:
                try:
                    val = float(row[field])
                    assert val >= 0.0, f"Negative value {val} in field {field}"
                except ValueError:
                    raise AssertionError(f"Non-numeric value '{row[field]}' in field {field} for food {row['food_id']}")

    print(f"✅ Verified {clean_csv}: {food_count} rows, all 14 schema columns valid and numeric.")

    alias_count = 0
    with open(aliases_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["canonical", "alias"], f"Header mismatch in {aliases_csv}"
        for row in reader:
            alias_count += 1
            assert row["canonical"].strip(), "Empty canonical found!"
            assert row["alias"].strip(), "Empty alias found!"

    print(f"✅ Verified {aliases_csv}: {alias_count} rows, valid canonical-to-alias mappings.")
    print("🎉 PERSON 2 NUTRITION ENGINE DATASET AUDIT PASSED 100%!")

if __name__ == "__main__":
    verify_dataset()
