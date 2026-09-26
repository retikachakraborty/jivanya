import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.recipe import Recipe, RecipeIngredient
from app.api.meal_plan import (
    MealPlanRequest,
    MealSwapRequest,
    GroceryListRequest,
    generate_meal_plan,
    swap_meal_slot,
    generate_grocery_list,
)


class TestMealPlanAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            cls.engine,
            tables=[
                Recipe.__table__,
                RecipeIngredient.__table__,
            ],
        )

    def setUp(self):
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.db = Session(bind=self.connection)

        # Seed sample recipes
        recipes = [
            Recipe(
                recipe_id="poha-1",
                recipe_name="Kanda Poha",
                cuisine="Maharashtrian Recipes",
                course="North Indian Breakfast",
                diet="Vegetarian",
                ingredients_raw="poha, onion, mustard seeds, green chili, turmeric, peanut",
                total_minutes=20,
            ),
            Recipe(
                recipe_id="idli-1",
                recipe_name="Steamed Idli",
                cuisine="South Indian Recipes",
                course="South Indian Breakfast",
                diet="Vegetarian",
                ingredients_raw="rice, urad dal, salt",
                total_minutes=25,
            ),
            Recipe(
                recipe_id="dal-tadka-1",
                recipe_name="Yellow Dal Tadka",
                cuisine="North Indian Recipes",
                course="Lunch",
                diet="Vegetarian",
                ingredients_raw="toor dal, tomato, cumin, ghee, turmeric",
                total_minutes=30,
            ),
            Recipe(
                recipe_id="paneer-bhurji-1",
                recipe_name="Amritsari Paneer Bhurji",
                cuisine="North Indian Recipes",
                course="Lunch",
                diet="Vegetarian",
                ingredients_raw="paneer, tomato, onion, capsicum, butter",
                total_minutes=20,
            ),
            Recipe(
                recipe_id="khichdi-1",
                recipe_name="Moong Dal Khichdi",
                cuisine="Indian",
                course="Dinner",
                diet="Vegetarian",
                ingredients_raw="rice, moong dal, ghee, cumin, turmeric",
                total_minutes=25,
            ),
            Recipe(
                recipe_id="palak-paneer-1",
                recipe_name="Palak Paneer",
                cuisine="North Indian Recipes",
                course="Dinner",
                diet="Vegetarian",
                ingredients_raw="spinach, paneer, garlic, tomato, garam masala",
                total_minutes=35,
            ),
            Recipe(
                recipe_id="dhokla-1",
                recipe_name="Khaman Dhokla",
                cuisine="Gujarati Recipes",
                course="Snack",
                diet="Vegetarian",
                ingredients_raw="besan, mustard seeds, curry leaves, green chili",
                total_minutes=20,
            ),
            Recipe(
                recipe_id="samosa-1",
                recipe_name="Aloo Samosa",
                cuisine="North Indian Recipes",
                course="Snack",
                diet="Vegetarian",
                ingredients_raw="potato, maida, cumin, coriander, oil",
                total_minutes=40,
            ),
            Recipe(
                recipe_id="jain-khichdi",
                recipe_name="Jain Khichdi No Onion Garlic",
                cuisine="Indian",
                course="Dinner",
                diet="Vegetarian",
                ingredients_raw="rice, moong dal, turmeric, salt, cumin",
                total_minutes=20,
            ),
        ]
        self.db.add_all(recipes)

        # Seed ingredients
        for r in recipes:
            for item in r.ingredients_raw.split(","):
                clean = item.strip()
                self.db.add(
                    RecipeIngredient(
                        recipe_id=r.recipe_id,
                        ingredient_raw=clean,
                        ingredient=clean.lower(),
                    )
                )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.transaction.rollback()
        self.connection.close()

    def test_generate_meal_plan_default(self):
        req = MealPlanRequest(
            regional_preference="all",
            diet_preference="all",
            no_onion=False,
            no_garlic=False,
            include_snack=True,
        )
        res = generate_meal_plan(req, self.db)
        self.assertEqual(len(res.days), 7)
        self.assertFalse(hasattr(res, "weekly_calories_avg"))
        self.assertFalse(hasattr(res, "weekly_protein_avg_g"))
        self.assertTrue(all(meal.recipe.recipe_id for day in res.days for meal in day.meals))

        first_day = res.days[0]
        self.assertEqual(first_day.day, "Monday")
        self.assertEqual(first_day.day_short, "Mon")
        self.assertEqual(len(first_day.meals), 4)
        meal_types = [m.meal_type for m in first_day.meals]
        self.assertEqual(meal_types, ["breakfast", "lunch", "dinner", "snack"])

    def test_generate_meal_plan_without_snack(self):
        req = MealPlanRequest(
            regional_preference="all",
            diet_preference="all",
            no_onion=False,
            no_garlic=False,
            include_snack=False,
        )
        res = generate_meal_plan(req, self.db)
        self.assertEqual(len(res.days), 7)
        first_day = res.days[0]
        self.assertEqual(len(first_day.meals), 3)
        meal_types = [m.meal_type for m in first_day.meals]
        self.assertEqual(meal_types, ["breakfast", "lunch", "dinner"])

    def test_generate_meal_plan_restrictions(self):
        req = MealPlanRequest(
            regional_preference="all",
            diet_preference="vegetarian",
            no_onion=True,
            no_garlic=True,
            exclude_allergies=["peanut"],
            include_snack=False,
        )
        res = generate_meal_plan(req, self.db)
        self.assertEqual(len(res.days), 7)

        for day in res.days:
            for meal in day.meals:
                raw_ing = (meal.recipe.ingredients_raw or "").lower()
                self.assertNotIn("onion", raw_ing)
                self.assertNotIn("garlic", raw_ing)
                self.assertNotIn("peanut", raw_ing)

    def test_swap_meal_slot(self):
        # Generate plan
        gen_req = MealPlanRequest(include_snack=False)
        gen_res = generate_meal_plan(gen_req, self.db)
        first_meal = gen_res.days[0].meals[0]

        swap_req = MealSwapRequest(
            slot_id=first_meal.slot_id,
            meal_type=first_meal.meal_type,
            current_recipe_id=first_meal.recipe.recipe_id,
            regional_preference="all",
            diet_preference="all",
            no_onion=False,
            no_garlic=False,
            exclude_recipe_ids=[first_meal.recipe.recipe_id],
        )
        swapped = swap_meal_slot(swap_req, self.db)
        self.assertEqual(swapped.slot_id, first_meal.slot_id)
        self.assertEqual(swapped.meal_type, first_meal.meal_type)
        self.assertIsNotNone(swapped.recipe.recipe_id)

    def test_grocery_list_generation(self):
        req = GroceryListRequest(recipe_ids=["poha-1", "dal-tadka-1", "palak-paneer-1"])
        res = generate_grocery_list(req, self.db)
        self.assertGreater(res.total_items, 0)
        category_names = [c.category_name for c in res.categories]
        self.assertTrue(any("Produce" in name for name in category_names))
        self.assertTrue(any("Dairy" in name for name in category_names))


if __name__ == "__main__":
    unittest.main()
