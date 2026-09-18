import csv
import os
import re

def build_dataset():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    nutrition_engine_dir = os.path.dirname(script_dir)
    raw_dir = os.path.join(nutrition_engine_dir, "raw")
    processed_dir = os.path.join(nutrition_engine_dir, "processed")

    os.makedirs(processed_dir, exist_ok=True)

    ifct_source = os.path.join(raw_dir, "ifct2017_raw.csv")
    if not os.path.exists(ifct_source):
        ifct_source = "/home/cnsqncs/Downloads/ifct2017-main/compositions/index.csv"

    clean_csv_path = os.path.join(processed_dir, "food_nutrition_clean.csv")
    aliases_csv_path = os.path.join(processed_dir, "ingredient_aliases.csv")

    def parse_float(val):
        if not val or val.strip() in ["-", "NA", "N/A", "None", "null", ""]:
            return 0.0
        try:
            v = float(val.strip())
            return max(0.0, v)
        except ValueError:
            return 0.0

    fieldnames = [
        "food_id", "food_name", "food_group",
        "energy_kcal", "protein_g", "carbohydrate_g", "fat_g", "fiber_g",
        "calcium_mg", "iron_mg", "sodium_mg", "potassium_mg",
        "vitamin_c_mg", "folate_ug"
    ]

    curated_aliases = [
        ("Milk, whole, Cow", "curd"),
        ("Milk, whole, Cow", "dahi"),
        ("Milk, whole, Cow", "yogurt"),
        ("Bengal gram, dal", "besan"),
        ("Bengal gram, dal", "chickpea flour"),
        ("Bengal gram, dal", "gram flour"),
        ("Bengal gram, dal", "chana dal"),
        ("Bengal gram, dal", "split bengal gram"),
        ("Red gram, dal", "toor dal"),
        ("Red gram, dal", "arhar dal"),
        ("Red gram, dal", "pigeon pea"),
        ("Black gram, dal", "urad dal"),
        ("Black gram, dal", "black gram"),
        ("Green gram, dal", "moong dal"),
        ("Green gram, dal", "green gram"),
        ("Lentil, dal", "masoor dal"),
        ("Lentil, dal", "red lentil"),
        ("Rice, flakes", "poha"),
        ("Rice, flakes", "flattened rice"),
        ("Wheat flour, atta", "atta"),
        ("Wheat flour, atta", "gehun ka atta"),
        ("Wheat flour, atta", "wheat flour"),
        ("Wheat flour, refined", "maida"),
        ("Ragi", "ragi"),
        ("Ragi", "finger millet"),
        ("Bajra", "bajra"),
        ("Bajra", "pearl millet"),
        ("Jowar", "jowar"),
        ("Ghee", "ghee"),
        ("Ghee", "clarified butter"),
        ("Spinach", "palak"),
        ("Spinach", "spinach"),
        ("Fenugreek leaves", "methi"),
        ("Fenugreek leaves", "fenugreek leaves"),
        ("Coriander leaves", "dhania"),
        ("Coriander leaves", "coriander leaves"),
        ("Potato", "aloo"),
        ("Potato", "potato"),
        ("Onion", "pyaz"),
        ("Onion", "onion"),
        ("Tomato, green", "tamatar"),
        ("Tomato, green", "tomato"),
        ("Ginger, fresh", "adrak"),
        ("Ginger, fresh", "ginger"),
        ("Garlic", "lehsun"),
        ("Garlic", "garlic")
    ]

    seen_aliases = set()
    final_aliases = []

    for canonical, alias in curated_aliases:
        c_clean = canonical.strip()
        a_clean = alias.strip().lower()
        if (c_clean, a_clean) not in seen_aliases:
            seen_aliases.add((c_clean, a_clean))
            final_aliases.append((c_clean, a_clean))

    rows_written = 0

    with open(ifct_source, mode="r", encoding="utf-8") as infile, \
         open(clean_csv_path, mode="w", encoding="utf-8", newline="") as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            food_id = row.get("code", "").strip()
            food_name = row.get("name", "").strip()
            food_group = row.get("grup", "").strip()

            if not food_id or not food_name:
                continue

            enerc_kj = parse_float(row.get("enerc"))
            energy_kcal = round(enerc_kj / 4.184, 2)

            clean_row = {
                "food_id": food_id,
                "food_name": food_name,
                "food_group": food_group,
                "energy_kcal": energy_kcal,
                "protein_g": round(parse_float(row.get("protcnt")), 2),
                "carbohydrate_g": round(parse_float(row.get("choavldf")), 2),
                "fat_g": round(parse_float(row.get("fatce")), 2),
                "fiber_g": round(parse_float(row.get("fibtg")), 2),
                "calcium_mg": round(parse_float(row.get("ca")) * 1000.0, 2),
                "iron_mg": round(parse_float(row.get("fe")) * 1000.0, 2),
                "sodium_mg": round(parse_float(row.get("na")) * 1000.0, 2),
                "potassium_mg": round(parse_float(row.get("k")) * 1000.0, 2),
                "vitamin_c_mg": round(parse_float(row.get("vitc")) * 1000.0, 2),
                "folate_ug": round(parse_float(row.get("folsum")) * 1000000.0, 2)
            }
            writer.writerow(clean_row)
            rows_written += 1

            lang_str = row.get("lang", "").strip()
            if lang_str:
                parts = lang_str.split(";")
                for p in parts:
                    p_clean = re.sub(r"^[A-Za-z]+\.\s*", "", p.strip())
                    if p_clean and len(p_clean) > 1:
                        alias_val = p_clean.lower()
                        if alias_val != food_name.lower() and (food_name, alias_val) not in seen_aliases:
                            seen_aliases.add((food_name, alias_val))
                            final_aliases.append((food_name, alias_val))

    with open(aliases_csv_path, mode="w", encoding="utf-8", newline="") as afile:
        awriter = csv.writer(afile)
        awriter.writerow(["canonical", "alias"])
        for canonical, alias in final_aliases:
            awriter.writerow([canonical, alias])

    print(f"[BUILD SUCCESS] Cleaned Food Nutrition dataset written to: {clean_csv_path} ({rows_written} rows)")
    print(f"[BUILD SUCCESS] Cleaned Ingredient Aliases dataset written to: {aliases_csv_path} ({len(final_aliases)} rows)")

if __name__ == "__main__":
    build_dataset()
