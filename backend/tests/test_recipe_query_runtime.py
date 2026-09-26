import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.nutrition import IngredientAlias
from app.models.recipe import Recipe, RecipeIngredient
from app.jiv.agent.orchestrator import jiv_agent
from app.jiv.schemas.chat import JivChatRequest, UserProfileSchema
from app.jiv.tools.recipe_tools import MatchRecipesTool, SearchRecipesTool


class RecipeQueryRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine, tables=[Recipe.__table__, RecipeIngredient.__table__, IngredientAlias.__table__])

    def setUp(self):
        self.db = Session(self.engine)
        rows = [
            ("dinner-1", "Dinner Paneer", "Dinner", "Chinese", "Vegetarian", ["paneer", "rice"]),
            ("dinner-2", "Chinese Dinner", "Dinner", "Indo Chinese", "Vegetarian", ["rice"]),
            ("lunch-1", "Vegetarian Lunch", "Lunch", "Bengali Recipes", "Vegetarian", ["lentil"]),
            ("breakfast-1", "Indian Breakfast", "Indian Breakfast", "Indian", "Vegetarian", ["rice"]),
            ("allergy-1", "Peanut Chinese", "Dinner", "Chinese", "Vegetarian", ["peanut", "rice"]),
        ]
        for recipe_id, name, course, cuisine, diet, ingredients in rows:
            self.db.add(Recipe(recipe_id=recipe_id, recipe_name=name, course=course, cuisine=cuisine, diet=diet, total_minutes=20))
            for ingredient in ingredients:
                self.db.add(RecipeIngredient(recipe_id=recipe_id, ingredient=ingredient, ingredient_raw=ingredient))
        self.db.flush()

    def tearDown(self):
        self.db.rollback()
        self.db.close()

    def assert_ids_exist(self, ids):
        stored = {row[0] for row in self.db.query(Recipe.recipe_id).filter(Recipe.recipe_id.in_(ids)).all()}
        self.assertEqual(set(ids), stored)

    def test_backend_course_and_cuisine_filters_do_not_require_ingredients(self):
        dinner = MatchRecipesTool().execute(self.db, available_ingredients=[], course=["Dinner"], limit=5)
        chinese = SearchRecipesTool().execute(self.db, cuisine=["Chinese", "Indo Chinese"], limit=5)
        self.assertEqual(dinner["status"], "FOUND")
        self.assertEqual(chinese["status"], "FOUND")
        self.assertEqual(len(chinese["items"]), 3)
        self.assert_ids_exist([item["recipe_id"] for item in chinese["items"]])

    def test_jiv_orchestration_executes_real_filters_and_hard_profile_constraints(self):
        dinner = jiv_agent.process(self.db, JivChatRequest(message="what can i have for dinner", profile=UserProfileSchema()))
        chinese = jiv_agent.process(self.db, JivChatRequest(message="5 chinese recipes", profile=UserProfileSchema(allergies=["peanut"])))
        self.assertEqual(dinner.tool_called, "search_recipes")
        self.assertEqual(dinner.tool_result["status"], "FOUND")
        self.assertEqual(chinese.tool_called, "search_recipes")
        self.assertEqual(chinese.tool_result["status"], "FOUND")
        self.assertLessEqual(len(chinese.tool_result["items"]), 5)
        ids = [item["recipe_id"] for item in chinese.tool_result["items"]]
        self.assertNotIn("allergy-1", ids)
        self.assert_ids_exist(ids)


if __name__ == "__main__":
    unittest.main()
