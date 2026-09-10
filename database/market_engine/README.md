# Open Food Facts Raw Dataset

## Source

Open Food Facts

Official website: https://world.openfoodfacts.org/

API documentation: https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/

## Purpose

This directory contains the raw Open Food Facts data that will be used to build Jivanya's India-focused packaged food product dataset.

The processed dataset will be used for:

* Packaged food product search
* Nutrition comparison
* Ingredient analysis
* Allergen checking
* Dietary restriction checking
* Jivanya Match Score
* Product comparison

## Data Collection

* Source: Open Food Facts
* Dataset scope: India-focused packaged food products
* Download date: 2 September 2026
* Project: Jivanya

## Processing

The raw dataset will not be modified directly.

The processing pipeline will:

1. Filter India-related products
2. Select relevant food categories
3. Remove unusable records
4. Clean product names
5. Normalize categories
6. Normalize ingredients
7. Normalize allergen information
8. Remove duplicate products
9. Calculate nutrition-data completeness
10. Export the cleaned dataset

## Expected Output

Processed dataset:

`data/processed/products_india_clean.csv`

Processing script:

`scripts/process_openfoodfacts.py`

## Important

The raw Open Food Facts data is kept separate from processed project data so that the cleaning and preprocessing pipeline remains reproducible.
