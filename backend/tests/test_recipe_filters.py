import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.nutrition import IngredientAlias
from app.models.recipe import Recipe, RecipeIngredient
from app.api.recipes import list_recipes, matching_recipes


class RecipeRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine, tables=[
            Recipe.__table__, RecipeIngredient.__table__, IngredientAlias.__table__,
        ])

    def setUp(self):
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.db = Session(bind=self.connection)
        recipes = [
            Recipe(recipe_id="veg-chicken", recipe_name="Chicken Rice", diet="Vegetarian"),
            Recipe(recipe_id="veg-safe", recipe_name="Tomato Rice", diet="Vegetarian"),
            Recipe(recipe_id="nonveg", recipe_name="Chicken Curry", diet="High Protein Non Vegetarian"),
            Recipe(recipe_id="nuts", recipe_name="Nut Curry", diet="Vegetarian"),
            Recipe(recipe_id="coconut", recipe_name="Coconut Curry", diet="Vegetarian"),
            Recipe(recipe_id="onion", recipe_name="Onion Rice", diet="Vegetarian"),
            Recipe(recipe_id="garlic", recipe_name="Garlic Rice", diet="Vegetarian"),
            Recipe(recipe_id="vegan-safe", recipe_name="Coconut Rice", diet="Vegan"),
            Recipe(recipe_id="vegan-egg", recipe_name="Almond Milk Egg Rice", diet="Vegan"),
            Recipe(recipe_id="unknown-ingredients", recipe_name="Unverified Vegetarian", diet="Vegetarian"),
            Recipe(recipe_id="carrot", recipe_name="Carrot Rice", diet="Vegetarian"),
        ]
        self.db.add_all(recipes)
        ingredients = {
            "veg-chicken": ["chicken", "tomato"],
            "veg-safe": ["tomato", "rice"],
            "nonveg": ["chicken", "rice"],
            "nuts": ["walnut", "rice"],
            "coconut": ["coconut milk", "rice"],
            "onion": ["onion", "rice"],
            "garlic": ["garlic", "rice"],
            "vegan-safe": ["coconut milk", "rice"],
            "vegan-egg": ["almond milk egg", "rice"],
            "carrot": ["carrot", "rice"],
        }
        self.db.add_all([
            RecipeIngredient(recipe_id=recipe_id, ingredient_raw=item, ingredient=item)
            for recipe_id, items in ingredients.items() for item in items
        ])
        self.db.add_all([
            IngredientAlias(canonical="Walnut", alias="akhrot"),
            IngredientAlias(canonical="Ground nut", alias="peanut, groundnut"),
            IngredientAlias(canonical="Almond", alias="badam"),
        ])
        self.db.flush()

    def tearDown(self):
        self.db.close()
        self.transaction.rollback()
        self.connection.close()

    def match(self, ingredients, **kwargs):
        response = matching_recipes(ingredients=ingredients, exclude=kwargs.pop("exclude", None), diet=kwargs.pop("diet", None), cuisine=None, no_onion=kwargs.pop("no_onion", False), no_garlic=kwargs.pop("no_garlic", False), db=self.db, limit=20, offset=0, **kwargs)
        return {item.recipe_id for item in response.items}, response.ignored_ingredients

    def test_vegetarian_rejects_chicken_and_keeps_safe_ingredient(self):
        ids, ignored = self.match("chicken,tomato", diet="vegetarian")
        self.assertEqual(ids, {"veg-safe"})
        self.assertEqual(ignored, ["chicken"])

    def test_nuts_allergy_rejects_walnut_but_no_allergy_allows_it(self):
        restricted, _ = self.match("rice", exclude="nuts")
        unrestricted, _ = self.match("rice")
        self.assertNotIn("nuts", restricted)
        self.assertIn("nuts", unrestricted)
        self.assertIn("coconut", restricted)

    def test_onion_flag_is_personal_and_false_allows_onion(self):
        restricted, ignored = self.match("onion", no_onion=True)
        unrestricted, _ = self.match("onion", no_onion=False)
        self.assertNotIn("onion", restricted)
        self.assertEqual(ignored, ["onion"])
        self.assertIn("onion", unrestricted)

    def test_garlic_flag_is_personal_and_false_allows_garlic(self):
        restricted, ignored = self.match("garlic", no_garlic=True)
        unrestricted, _ = self.match("garlic", no_garlic=False)
        self.assertNotIn("garlic", restricted)
        self.assertEqual(ignored, ["garlic"])
        self.assertIn("garlic", unrestricted)

    def test_vegetarian_preference_is_personal_and_no_preference_allows_chicken(self):
        vegetarian, _ = self.match("chicken", diet="vegetarian")
        unrestricted, _ = self.match("chicken", diet=None)
        self.assertNotIn("nonveg", vegetarian)
        self.assertIn("nonveg", unrestricted)

    def test_carrot_exclusion_is_personal(self):
        excluded, _ = self.match("rice", exclude="carrot")
        allowed, _ = self.match("rice")
        self.assertNotIn("carrot", excluded)
        self.assertIn("carrot", allowed)

    def test_safe_ingredient_remains_searchable_after_rejection(self):
        ids, ignored = self.match("chicken,tomato", diet="vegetarian")
        self.assertEqual(ignored, ["chicken"])
        self.assertIn("veg-safe", ids)
        self.assertEqual(next(x for x in self.match("tomato", diet="vegetarian")[0]), "veg-safe")

    def test_profile_restricted_browse_excludes_recipes_without_ingredient_evidence(self):
        response = list_recipes(query=None, cuisine=None, course=None, diet="vegetarian", diet_filter=None, ingredient=None, exclude="nuts", no_onion=False, no_garlic=False, offset=0, limit=50, db=self.db)
        self.assertNotIn("unknown-ingredients", {item.recipe_id for item in response.items})

    def test_vegan_allows_plant_milk_but_rejects_separate_egg_conflict(self):
        ids, ignored = self.match("coconut milk,egg", diet="vegan")
        self.assertEqual(ids, {"vegan-safe"})
        self.assertEqual(ignored, ["egg"])

    def test_nut_term_does_not_match_coconut_or_nutmeg(self):
        from app.api.recipes import _ingredient_matches
        self.assertFalse(_ingredient_matches("coconut milk", "nuts"))
        self.assertFalse(_ingredient_matches("nutmeg", "nuts"))
        self.assertTrue(_ingredient_matches("walnut", "nuts"))


if __name__ == "__main__":
    unittest.main()
