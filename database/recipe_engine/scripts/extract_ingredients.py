import re
import unicodedata
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "database"
    / "processed"
    / "recipes_clean.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "database"
    / "processed"
    / "recipe_ingredients.csv"
)


# ---------------------------------------------------------
# Measurement units
# ---------------------------------------------------------

UNITS = [
    # English volume / spoon measurements
    "cup",
    "cups",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "teaspoon",
    "teaspoons",
    "tsp",

    # English metric / size measurements
    "kg",
    "kilogram",
    "kilograms",
    "ml",
    "milliliter",
    "milliliters",
    "litre",
    "litres",
    "liter",
    "liters",
    "inch",
    "inches",

    # English count measurements
    "sprig",
    "sprigs",
    "clove",
    "cloves",
    "piece",
    "pieces",
    "pinch",
    "handful",

    # Hindi volume / spoon measurements
    "कप",
    "चम्मच",
    "चमच्च",
    "बड़ा",
    "बड़े",
    "छोटा",
    "छोटे",

    # Hindi weight / size measurements
    "ग्राम",
    "ग्राम्स",
    "किलो",
    "किलोग्राम",
    "इंच",

    # Hindi count measurements
    "कली",
    "कलियां",
    "टहनी",
    "टहनियां",
]


# ---------------------------------------------------------
# Ingredient aliases
# ---------------------------------------------------------

ALIASES = {
    # Spices
    "jeera": "cumin",
    "cumin seeds": "cumin",

    "haldi": "turmeric",
    "turmeric powder": "turmeric",

    "dhania": "coriander",
    "coriander powder": "coriander",

    "hing": "asafoetida",

    "mustard seeds": "mustard",

    # Chillies
    "mirchi": "chilli",
    "chili": "chilli",
    "chilies": "chilli",
    "chillies": "chilli",

    "green chili": "green chilli",
    "green chilies": "green chilli",
    "green chillies": "green chilli",

    "red chili": "red chilli",
    "red chilies": "red chilli",
    "red chillies": "red chilli",
    "red chilli powder": "red chilli",
    "dry red chilli": "red chilli",

    # Flour
    "besan": "gram flour",
    "gram flour": "gram flour",
    "gram flour besan": "gram flour",

    "maida": "all purpose flour",
    "all purpose flour maida": "all purpose flour",

    "atta": "wheat flour",
    "whole wheat flour": "wheat flour",

    # Dairy
    "curd": "yogurt",
    "dahi": "yogurt",

    # Vegetables
    "gajjar": "carrot",
    "carrots": "carrot",

    "tomatoes": "tomato",

    "onions": "onion",

    "potatoes": "potato",
    "aloo": "potato",

    "matar": "green peas",
    "green peas": "green peas",

    # Lentils
    "chickpea lentils": "chana dal",
    "white urad dal": "urad dal",

    # Nuts
    "cashews": "cashew",
    "almonds": "almond",
    "peanuts": "peanut",
    "walnuts": "walnut",

    # Garlic
    "garlic cloves": "garlic",

    # Other
    "rice vermicelli noodles": "rice vermicelli",
    "amchur": "dry mango powder",
    "sunflower oil": "sunflower oil",

    "paneer": "paneer",
    "ghee": "ghee",

        # -------------------------------------------------
    # Hindi / Devanagari ingredient aliases
    # -------------------------------------------------

    "प्याज": "onion",
    "लहसुन": "garlic",
    "अदरक": "ginger",

    "टमाटर": "tomato",
    "गाजर": "carrot",
    "आलू": "potato",
    "बैंगन": "brinjal",
    "भिंडी": "okra",
    "शिमला मिर्च": "green bell pepper",
    "हरे मटर": "green peas",
    "हरा मटर": "green peas",

    "हरी मिर्च": "green chilli",
    "सुखी लाल मिर्च": "red chilli",
    "लाल मिर्च": "red chilli",

    "जीरा": "cumin",
    "जीरा पाउडर": "cumin powder",
    "हल्दी पाउडर": "turmeric",
    "हींग": "asafoetida",
    "राइ": "mustard",
    "धनिया पाउडर": "coriander",
    "धनिये के बीज": "coriander seeds",
    "सौंफ": "fennel seeds",
    "मेथी के दाने": "fenugreek seeds",
    "कलोंजी के बीज": "nigella seeds",

    "हरा धनिया": "coriander leaves",
    "कढ़ी पत्ता": "curry leaves",
    "पुदीना": "mint leaves",

    "नारियल": "coconut",
    "नारियल का दूध": "coconut milk",

    "पनीर": "paneer",
    "दही": "yogurt",
    "घी": "ghee",
    "दूध": "milk",
    "मक्खन": "butter",

    "बादाम": "almond",
    "काजू": "cashew",
    "मूंगफली": "peanut",
    "अखरोट": "walnut",

    "चना दाल": "chana dal",
    "रोस्टेड चना दाल": "roasted chana dal",
    "सफ़ेद उरद दाल": "urad dal",
    "काली उरद दाल": "urad dal",
    "पिली मूंग दाल": "moong dal",
    "हरी मूंग दाल": "moong dal",
    "अरहर दाल": "toor dal",
    "तुअर दाल": "toor dal",
    "मसूर दाल": "masoor dal",

    "बेसन": "gram flour",
    "गेहूं का आटा": "wheat flour",
    "चावल का आटा": "rice flour",

    "तेल": "oil",
    "नमक": "salt",
    "पानी": "water",
    "गुड़": "jaggery",
    "शक्कर": "sugar",

    "अंडा": "egg",
    "अंडे": "egg",

    "शहद": "honey",
    "निम्बू": "lemon",
    "निम्बू का रस": "lemon juice",
    "इमली": "tamarind",
    "इमली का पेस्ट": "tamarind paste",
    "कॉर्न फ्लौर": "corn flour",
    "अमचूर": "dry mango powder",
    "हरा बीन्स": "green beans",
    "सोया सॉस": "soy sauce",
    "चावल का सिरका": "rice vinegar",
    "रेड चिल्ली सॉस": "red chilli sauce",
    "वेजिटेबल स्टॉक": "vegetable stock",
    "हक्का नूडल्स": "hakka noodles",
    "थाई रेड चिल्ली": "thai red chilli",
    "स्टॉक सेलरी": "celery",
    # Extra Hindi cleanup
    "काली मिर्च पाउडर": "black pepper powder",
    "लौकी": "bottle gourd",
    "गरम मसाला पाउडर": "garam masala powder",
    "पालक": "spinach",
    "लाल मिर्च पाउडर": "red chilli",
    "दाल चीनी पाउडर": "cinnamon powder",
    # Awkward normalized phrases
    "long garlic": "garlic",
    "small spoon garam masala powder": "garam masala powder",
}


# ---------------------------------------------------------
# Basic cleaning
# ---------------------------------------------------------

def clean_basic(text):
    """
    Convert ingredient text to lowercase and normalize spacing.
    """

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Remove non-breaking spaces
    text = text.replace("\xa0", " ")

    # Convert common Unicode fractions
    text = (
        text
        .replace("½", " 1/2 ")
        .replace("¼", " 1/4 ")
        .replace("¾", " 3/4 ")
    )

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------
# Quantity cleaning
# ---------------------------------------------------------

def remove_quantity(text):
    """
    Remove quantities such as:

    2
    1/2
    1 / 2
    1-1/2
    1-1 / 2
    2-1 / 2
    2.5
    """

    patterns = [
        # Mixed fractions
        # Example:
        # 1-1/2
        # 1-1 / 2
        # 2 - 1 / 2
        r"^\s*\d+\s*-\s*\d+\s*/\s*\d+\s*",

        # Simple fractions
        # Example:
        # 1/2
        # 1 / 2
        r"^\s*\d+\s*/\s*\d+\s*",

        # Decimal or whole number
        # Example:
        # 2
        # 2.5
        r"^\s*\d+(?:\.\d+)?\s*",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    return text.strip()


# ---------------------------------------------------------
# Weight cleaning
# ---------------------------------------------------------

def remove_weight_measurements(text):
    """
    Remove weight measurements when they occur as units.

    Examples:

    grams paneer
    -> paneer

    gram rice
    -> rice

    g paneer
    -> paneer

    But preserve actual ingredients such as:

    gram flour
    bengal gram
    green gram
    """

    text = re.sub(
        r"^\s*(?:g|gram|grams)\s+(?!flour\b)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


# ---------------------------------------------------------
# Unit cleaning
# ---------------------------------------------------------

def remove_units(text):
    """
    Remove English and Hindi measurement/count units.

    Uses token-based removal so Hindi/Devanagari units
    are handled reliably.
    """

    english_units = {
        "cup",
        "cups",
        "tablespoon",
        "tablespoons",
        "tbsp",
        "teaspoon",
        "teaspoons",
        "tsp",
        "kg",
        "kilogram",
        "kilograms",
        "ml",
        "milliliter",
        "milliliters",
        "litre",
        "litres",
        "liter",
        "liters",
        "inch",
        "inches",
        "sprig",
        "sprigs",
        "clove",
        "cloves",
        "piece",
        "pieces",
        "pinch",
        "handful",
    }

    hindi_units = {
        "कप",
        "चम्मच",
        "चमच्च",
        "बड़ा",
        "बड़े",
        "बड़े",
        "बड़ी",
        "बड़ी",
        "छोटा",
        "छोटे",
        "छोटी",
        "ग्राम",
        "ग्राम्स",
        "किलो",
        "किलोग्राम",
        "इंच",
        "कली",
        "कलियां",
        "कलियाँ",
        "टहनी",
        "टहनियां",
        "टहनियाँ",
    }

    units = english_units | hindi_units

    words = text.split()

    words = [
        word
        for word in words
        if word not in units
    ]

    return " ".join(words).strip()

# ---------------------------------------------------------
# Parentheses
# ---------------------------------------------------------

def remove_parenthetical(text):
    """
    Remove parenthetical descriptions.

    Example:

    cumin seeds (jeera)
    -> cumin seeds

    carrots (gajjar)
    -> carrots
    """

    text = re.sub(
        r"\([^)]*\)",
        "",
        text
    )

    return text.strip()


# ---------------------------------------------------------
# Preparation notes
# ---------------------------------------------------------

def remove_preparation_notes(text):
    """
    Remove normal preparation instructions after a hyphen.

    Examples:

    onion - thinly sliced
    -> onion

    carrot - chopped
    -> carrot

    Important:
    this does NOT attempt to repair multiple ingredients that
    have accidentally merged into one source string.
    """

    parts = re.split(
        r"\s+-\s+",
        text,
        maxsplit=1
    )

    return parts[0].strip()


# ---------------------------------------------------------
# Noise removal
# ---------------------------------------------------------

def remove_noise(text):
    """
    Remove non-ingredient phrases while preserving
    Unicode characters such as Hindi/Devanagari.
    """

    noise_patterns = [
        r"\bto taste\b",
        r"\bas per taste\b",
        r"\bas per your taste\b",
        r"\bas required\b",
        r"\bas needed\b",
        r"\baccording to taste\b",
        r"\bfor cooking\b",
        r"\bfor frying\b",
        r"\bfor deep frying\b",
        r"\bfor shallow frying\b",
        r"\bfor garnish\b",
        r"\bfor garnishing\b",
        r"\boptional\b",
        r"\bif required\b",
        r"\bif needed\b",
    ]

    for pattern in noise_patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    # Preserve Unicode letters, digits and combining marks.
    # Combining marks are necessary for Hindi vowel signs.
    text = "".join(
        char
        if (
            char.isalnum()
            or char.isspace()
            or unicodedata.category(char).startswith("M")
        )
        else " "
        for char in text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

# ---------------------------------------------------------
# Alias normalization
# ---------------------------------------------------------

def normalize_alias(text):
    """
    Convert ingredient aliases into one consistent name.
    """

    text = text.strip()

    if text in ALIASES:
        return ALIASES[text]

    return text


# ---------------------------------------------------------
# Main normalization function
# ---------------------------------------------------------

def normalize_ingredient(raw):
    """
    Convert one raw ingredient string into a normalized
    ingredient name.
    """

    text = clean_basic(raw)

    if not text:
        return ""

    text = remove_quantity(text)

    text = remove_weight_measurements(text)

    text = remove_units(text)

    text = remove_parenthetical(text)

    text = remove_preparation_notes(text)

    text = remove_noise(text)

    text = normalize_alias(text)

    return text.strip()


# ---------------------------------------------------------
# Load cleaned recipes
# ---------------------------------------------------------

print("Loading cleaned recipes...")

df = pd.read_csv(INPUT_FILE)

print(f"Recipes loaded: {len(df):,}")


# ---------------------------------------------------------
# Extract ingredient rows
# ---------------------------------------------------------

rows = []

for _, row in df.iterrows():

    recipe_id = row["recipe_id"]
    ingredients = row["ingredients_raw"]

    # Skip recipes with no ingredients
    if pd.isna(ingredients):
        continue

    ingredients = str(ingredients).strip()

    if not ingredients:
        continue

    # Ingredients in this dataset are comma separated
    parts = ingredients.split(",")

    for part in parts:

        raw_ingredient = part.strip()

        if not raw_ingredient:
            continue

        normalized = normalize_ingredient(
            raw_ingredient
        )

        if not normalized:
            continue

        rows.append(
            {
                "recipe_id": recipe_id,
                "ingredient_raw": raw_ingredient,
                "ingredient": normalized,
            }
        )


# ---------------------------------------------------------
# Build ingredient DataFrame
# ---------------------------------------------------------

ingredients_df = pd.DataFrame(rows)


# ---------------------------------------------------------
# Remove duplicate ingredients inside a recipe
# ---------------------------------------------------------

ingredients_df = (
    ingredients_df
    .drop_duplicates(
        subset=[
            "recipe_id",
            "ingredient"
        ]
    )
    .reset_index(drop=True)
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

ingredients_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("\nIngredient extraction complete.")

print(
    f"Recipes processed: {len(df):,}"
)

print(
    f"Ingredient rows: {len(ingredients_df):,}"
)

print(
    "Unique normalized ingredients:",
    ingredients_df["ingredient"].nunique()
)

print(
    "Recipes with extracted ingredients:",
    ingredients_df["recipe_id"].nunique()
)

print(
    "Recipes without extracted ingredients:",
    len(df)
    - ingredients_df["recipe_id"].nunique()
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
