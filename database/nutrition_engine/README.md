# Person 2: Nutrition Engine Data & Pipeline

## Overview
This folder contains the complete **Nutrition Engine** data pipeline owned by Person 2. It processes the official **ICMR-NIN Indian Food Composition Tables (IFCT 2017)** dataset (528 analyzed Indian foods with over 150 food components) into clean, standardized CSV datasets for the Jivanya backend database and recipe normalizer.

---

## Directory Layout

```text
database/nutrition_engine/
├── experiments/            <-- Scratch notebooks and exploratory data scripts
├── processed/
│   ├── food_nutrition_clean.csv  <-- Cleaned 542 Indian food records with 14 nutrient fields
│   └── ingredient_aliases.csv    <-- 6,270 mapped recipe-to-canonical ingredient aliases
├── raw/
│   └── ifct2017_raw.csv    <-- Original ICMR-NIN IFCT 2017 composition dataset
├── scripts/
│   ├── build_person2_dataset.py  <-- Dataset cleaning & extraction script
│   └── verify_person2_dataset.py <-- Automated validation and audit script
└── README.md               <-- Documentation
```

---

## Datasets Delivered

### 1. `processed/food_nutrition_clean.csv`
Analyzed nutritional breakdown per **100 g edible portion**:

| Column | Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `food_id` | String | - | Food item unique code (e.g. `A001`, `A010`) |
| `food_name` | String | - | Canonical food item name |
| `food_group` | String | - | Food category/classification |
| `energy_kcal` | Float | kcal | Energy calculated from kJ (`enerc / 4.184`) |
| `protein_g` | Float | g | Total protein content |
| `carbohydrate_g` | Float | g | Available carbohydrate |
| `fat_g` | Float | g | Total fat content |
| `fiber_g` | Float | g | Total dietary fiber |
| `calcium_mg` | Float | mg | Calcium content (`ca * 1000`) |
| `iron_mg` | Float | mg | Iron content (`fe * 1000`) |
| `sodium_mg` | Float | mg | Sodium content (`na * 1000`) |
| `potassium_mg` | Float | mg | Potassium content (`k * 1000`) |
| `vitamin_c_mg` | Float | mg | Total Ascorbic Acid (`vitc * 1000`) |
| `folate_ug` | Float | µg | Total Folate B9 (`folsum * 1000000`) |

### 2. `processed/ingredient_aliases.csv`
Maps common recipe terms and regional Indian names (`atta`, `besan`, `dahi`, `ragi`, `poha`, `toor dal`, `ghee`, `palak`, etc.) to canonical IFCT 2017 food items.

---

## Scripts & Usage

### 1. Build Dataset
To re-extract and clean raw IFCT 2017 data into `processed/`:
```bash
python database/nutrition_engine/scripts/build_person2_dataset.py
```

### 2. Verify & Audit Dataset
To run automated validation checks on schema, data types, and values:
```bash
python database/nutrition_engine/scripts/verify_person2_dataset.py
```
