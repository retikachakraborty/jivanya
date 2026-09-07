# Jivanya Recipe Engine

This directory contains Person 1's recipe-data pipeline and recommendation-engine preparation for Jivanya.

## Dataset

Source dataset:

- Indian Food Dataset
- Kaggle: https://www.kaggle.com/datasets/sukhmandeepsinghbrar/indian-food-dataset

The raw dataset contains 6,871 Indian and related recipes with recipe names, ingredients, cuisine, course, diet, preparation time, cooking time, instructions, and source URLs.

Raw and generated CSV files are intentionally excluded from Git using `.gitignore`.

## Pipeline

The recipe pipeline runs in this order:

```text
Raw Kaggle CSV
        ↓
clean_recipes.py
        ↓
recipes_clean.csv
        ↓
extract_ingredients.py
        ↓
recipe_ingredients.csv
        ↓
build_recipe_features.py
        ↓
recipes_features.csv
        ↓
build_recommendation_data.py
        ↓
recipes_recommendation.csv
        ↓
build_recommender.py
