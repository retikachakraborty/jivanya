import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.nutrition import FoodItem, IngredientAlias
from app.models.product import Product
from app.models.recipe import Recipe, RecipeIngredient
from app.jiv.agent.orchestrator import jiv_agent
from app.jiv.providers import BaseLLMProvider, LLMResponse, set_llm_provider
from app.jiv.safety.hallucination_guard import HallucinationGuard
from app.jiv.safety.restriction_guard import RestrictionGuard
from app.jiv.schemas.chat import (
    ChatMessage,
    JivChatRequest,
    UserProfileSchema,
    VisionContextSchema,
)
from app.jiv.tools.registry import tool_registry


class FailingMockProvider(BaseLLMProvider):
    """Failing provider to test graceful error handling."""

    def chat(self, messages: list[ChatMessage], tools: list[dict], system_instruction: str, temperature: float = 0.2) -> LLMResponse:
        raise RuntimeError("Simulated network timeout connecting to remote LLM endpoint")


class JivOrchestrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(
            cls.engine,
            tables=[
                Recipe.__table__,
                RecipeIngredient.__table__,
                IngredientAlias.__table__,
                FoodItem.__table__,
                Product.__table__,
            ],
        )

    def setUp(self):
        from app.jiv.providers.mock_provider import MockLLMProvider
        set_llm_provider(MockLLMProvider())
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        self.db = Session(bind=self.connection)

        # Seed test recipes
        recipes = [
            Recipe(recipe_id="masoor-1", recipe_name="Masoor Dal Tadka", cuisine="North Indian", course="Main", diet="Vegetarian", total_minutes=25),
            Recipe(recipe_id="quick-dal", recipe_name="Quick Moong Dal", cuisine="North Indian", course="Main", diet="Vegetarian", total_minutes=15),
            Recipe(recipe_id="peanut-curry", recipe_name="Peanut Chutney Curry", cuisine="South Indian", course="Side", diet="Vegetarian", total_minutes=20),
            Recipe(recipe_id="chicken-biryani", recipe_name="Chicken Biryani", cuisine="Indian", course="Main", diet="High Protein Non Vegetarian", total_minutes=45),
            Recipe(recipe_id="onion-sambhar", recipe_name="Shallot Onion Sambhar", cuisine="South Indian", course="Main", diet="Vegetarian", total_minutes=30),
            Recipe(recipe_id="jain-dal", recipe_name="No Onion No Garlic Dal", cuisine="Indian", course="Main", diet="Vegetarian", total_minutes=20),
        ]
        self.db.add_all(recipes)

        ingredients = {
            "masoor-1": ["masoor dal", "onion", "tomato"],
            "quick-dal": ["moong dal", "tomato"],
            "peanut-curry": ["peanut", "rice"],
            "chicken-biryani": ["chicken", "rice"],
            "onion-sambhar": ["onion", "toor dal"],
            "jain-dal": ["toor dal", "tomato"],
        }
        for r_id, items in ingredients.items():
            for item in items:
                self.db.add(RecipeIngredient(recipe_id=r_id, ingredient=item, ingredient_raw=item))

        # Seed test foods
        foods = [
            FoodItem(
                food_id="A001",
                food_name="Almond",
                food_group="Nuts and Oilseeds",
                energy_kcal=609.0,
                protein_g=20.8,
                carbohydrate_g=10.5,
                fat_g=58.9,
                fiber_g=10.5,
                calcium_mg=230.0,
                iron_mg=5.09,
                sodium_mg=4.0,
            ),
            FoodItem(
                food_id="B005",
                food_name="Masoor dal",
                food_group="Grain Legumes",
                energy_kcal=343.0,
                protein_g=25.1,
                carbohydrate_g=59.0,
                fat_g=0.7,
                fiber_g=10.8,
            ),
        ]
        self.db.add_all(foods)

        # Seed aliases
        aliases = [
            IngredientAlias(canonical="Almond", alias="badam"),
            IngredientAlias(canonical="Ground nut", alias="peanut, groundnut"),
            IngredientAlias(canonical="Lentil", alias="masoor dal"),
            IngredientAlias(canonical="Walnut", alias="akhrot"),
        ]
        self.db.add_all(aliases)

        # Seed products
        products = [
            Product(
                barcode=890123456001,
                product_name="Quaker Rolled Oats",
                brand="Quaker",
                category="oats",
                protein_100g=13.5,
                sugars_100g=1.1,
                sodium_100g=5.0,
                ingredients_text="Rolled oats",
                allergens="",
                data_completeness=0.9,
            ),
            Product(
                barcode=890123456002,
                product_name="Kelloggs Instant Oats",
                brand="Kelloggs",
                category="oats",
                protein_100g=11.8,
                sugars_100g=2.5,
                sodium_100g=8.0,
                ingredients_text="Whole oats",
                allergens="",
                data_completeness=0.85,
            ),
            Product(
                barcode=890123456003,
                product_name="Pintola Peanut Butter Crunch",
                brand="Pintola",
                category="spreads",
                protein_100g=26.0,
                sugars_100g=6.0,
                sodium_100g=120.0,
                ingredients_text="Roasted peanuts, salt",
                allergens="Peanuts",
                data_completeness=0.95,
            ),
        ]
        self.db.add_all(products)
        self.db.flush()

    def tearDown(self):
        set_llm_provider(None)
        self.db.close()
        self.transaction.rollback()
        self.connection.close()

    # 1. Basic recipe request
    def test_basic_recipe_request(self):
        req = JivChatRequest(message="Give me a recipe using masoor dal")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "search_recipes")
        self.assertIsNotNone(res.tool_result)
        self.assertGreaterEqual(res.tool_result["total"], 1)
        recipe_names = [r["recipe_name"] for r in res.tool_result["items"]]
        self.assertIn("Masoor Dal Tadka", recipe_names)
        self.assertIn("Masoor Dal Tadka", res.reply)
        self.assertEqual(len(res.sources), len(res.tool_result["items"]))

    def test_requested_recipe_count_is_preserved_in_sources(self):
        self.db.add_all([
            Recipe(recipe_id=f"count-fixture-{index}", recipe_name=f"Count Fixture {index}", cuisine="Test")
            for index in range(20)
        ])
        self.db.flush()
        for count in (3, 5, 10, 20):
            response = jiv_agent.process(db=self.db, request=JivChatRequest(message=f"Give me {count} recipes"))
            self.assertEqual(len(response.tool_result["items"]), count)
            self.assertEqual(len(response.sources), count)

    # 2. Recipe request with profile restrictions
    def test_recipe_request_with_profile_restrictions(self):
        profile = UserProfileSchema(allergies=["peanut"])
        req = JivChatRequest(message="Find a recipe for dinner", profile=profile)
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "search_recipes")
        recipe_ids = [r["recipe_id"] for r in res.tool_result["items"]]
        self.assertNotIn("peanut-curry", recipe_ids)

    # 3. No-onion request
    def test_no_onion_request(self):
        profile = UserProfileSchema(noOnion=True)
        req = JivChatRequest(message="Find a dal recipe", profile=profile)
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "search_recipes")
        recipe_ids = [r["recipe_id"] for r in res.tool_result["items"]]
        self.assertNotIn("onion-sambhar", recipe_ids)
        self.assertNotIn("masoor-1", recipe_ids)
        self.assertTrue(any(r in recipe_ids for r in ["quick-dal", "jain-dal"]))

    def test_requested_ingredients_are_not_treated_as_restrictions(self):
        for message, expected_id in (
            ("Give me 10 recipes using onion", "onion-sambhar"),
            ("Show me recipes with peanut", "peanut-curry"),
            ("Give me chicken recipes", "chicken-biryani"),
        ):
            with self.subTest(message=message):
                response = jiv_agent.process(
                    db=self.db,
                    request=JivChatRequest(message=message, profile=UserProfileSchema()),
                )
                self.assertEqual(response.tool_called, "search_recipes")
                self.assertIn(expected_id, {item["recipe_id"] for item in response.tool_result["items"]})

    def test_restriction_state_is_user_scoped_and_false_is_disabled(self):
        restricted = jiv_agent.process(
            db=self.db,
            request=JivChatRequest(message="recipes using onion", profile=UserProfileSchema(noOnion=True)),
        )
        unrestricted = jiv_agent.process(
            db=self.db,
            request=JivChatRequest(message="recipes using onion", profile=UserProfileSchema(noOnion="false")),
        )
        self.assertNotIn("onion-sambhar", {item["recipe_id"] for item in restricted.tool_result["items"]})
        self.assertIn("onion-sambhar", {item["recipe_id"] for item in unrestricted.tool_result["items"]})
        self.assertFalse(UserProfileSchema(noOnion="false").no_onion)

    def test_updated_profile_replaces_prior_session_restrictions(self):
        session_id = "profile-update-regression"
        first = jiv_agent.process(
            db=self.db,
            request=JivChatRequest(session_id=session_id, message="recipes using onion", profile=UserProfileSchema(noOnion=True)),
        )
        second = jiv_agent.process(
            db=self.db,
            request=JivChatRequest(session_id=session_id, message="recipes using onion", profile=UserProfileSchema(noOnion=False)),
        )
        self.assertNotIn("onion-sambhar", {item["recipe_id"] for item in first.tool_result["items"]})
        self.assertIn("onion-sambhar", {item["recipe_id"] for item in second.tool_result["items"]})

    def test_allergy_conflict_is_distinct_from_no_database_match(self):
        blocked = jiv_agent.process(
            db=self.db,
            request=JivChatRequest(message="recipes using peanut", profile=UserProfileSchema(allergies=["peanut"])),
        )
        missing = jiv_agent.process(
            db=self.db,
            request=JivChatRequest(message="recipes using dragonfruit", profile=UserProfileSchema()),
        )
        self.assertEqual(blocked.tool_result["status"], "BLOCKED_BY_ALLERGY")
        self.assertEqual(missing.tool_result["status"], "NO_DATABASE_MATCH")

    # 4. Allergy conflict
    def test_allergy_conflict(self):
        profile = UserProfileSchema(allergies=["peanut"])
        req = JivChatRequest(message="Can I eat peanut butter?", profile=profile)
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "check_restrictions")
        self.assertEqual(res.tool_result["overall_status"], "CONFIRMED CONFLICT")
        self.assertFalse(res.tool_result["is_safe"])
        self.assertIn("CONFIRMED CONFLICT", res.reply)

    # 5. Product search
    def test_product_search(self):
        req = JivChatRequest(message="Which packaged oats are available?")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "search_products")
        self.assertGreaterEqual(res.tool_result["total"], 1)
        product_names = [p["product_name"] for p in res.tool_result["items"]]
        self.assertTrue(any("Oats" in name for name in product_names))

    # 6. Product comparison
    def test_product_comparison(self):
        req = JivChatRequest(message="Compare products 890123456001, 890123456002")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "compare_products")
        self.assertEqual(res.tool_result["count"], 2)
        barcodes = [p["barcode"] for p in res.tool_result["items"]]
        self.assertEqual(barcodes, [890123456001, 890123456002])

    # 7. Nutrition lookup
    def test_nutrition_lookup(self):
        req = JivChatRequest(message="What is the nutrition breakdown of almond?")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "lookup_nutrition")
        food = res.tool_result["matched_food"]
        self.assertIsNotNone(food)
        self.assertEqual(food["food_id"], "A001")
        self.assertEqual(food["energy_kcal"], 609.0)
        self.assertEqual(food["protein_g"], 20.8)

    # 8. Vision result -> recipe handoff
    def test_vision_result_recipe_handoff(self):
        # 8a: High-confidence vision handoff
        vc_safe = VisionContextSchema(label="tomato", confidence=0.88, confirmed=True)
        req_safe = JivChatRequest(message="What can I cook with this?", vision_context=vc_safe)
        res_safe = jiv_agent.process(db=self.db, request=req_safe)
        self.assertIn("tomato", res_safe.conversation_state["vision_items"])

        # 8b: Low-confidence detection requires user confirmation
        vc_low = VisionContextSchema(label="carrot", confidence=0.52, confirmed=False)
        req_low = JivChatRequest(message="What is this food?", vision_context=vc_low)
        res_low = jiv_agent.process(db=self.db, request=req_low)
        self.assertIn("please confirm", res_low.reply.lower())

        # 8c: Restricted detection is blocked
        profile = UserProfileSchema(allergies=["peanut"])
        vc_peanut = VisionContextSchema(label="peanut", confidence=0.92, confirmed=True)
        req_restricted = JivChatRequest(message="Can I cook with this?", vision_context=vc_peanut, profile=profile)
        res_restricted = jiv_agent.process(db=self.db, request=req_restricted)
        self.assertIn("conflicts with your saved allergy", res_restricted.reply.lower())

    # 9. Follow-up request / context handling
    def test_follow_up_request_context_handling(self):
        session_id = "test-session-follow-up"

        # Turn 1: Search for dal
        req1 = JivChatRequest(message="Find me a dal recipe", session_id=session_id)
        res1 = jiv_agent.process(db=self.db, request=req1)
        self.assertEqual(res1.tool_called, "search_recipes")

        # Turn 2: Follow-up with time constraint
        req2 = JivChatRequest(message="Make it under 20 minutes", session_id=session_id)
        res2 = jiv_agent.process(db=self.db, request=req2)
        self.assertEqual(res2.conversation_state["active_max_time"], 20)
        for r in res2.tool_result["items"]:
            self.assertLessEqual(r["total_minutes"], 20)

        # Turn 3: Follow-up with no-onion constraint
        req3 = JivChatRequest(message="Also no onion", session_id=session_id)
        res3 = jiv_agent.process(db=self.db, request=req3)
        self.assertTrue(res3.conversation_state["active_no_onion"])
        recipe_ids = [r["recipe_id"] for r in res3.tool_result["items"]]
        self.assertNotIn("masoor-1", recipe_ids)

    # 10. Invalid tool arguments
    def test_invalid_tool_arguments(self):
        result = tool_registry.execute(
            tool_name="search_recipes",
            db=self.db,
            arguments={"limit": "not_an_integer"},
        )
        self.assertEqual(result["status"], "validation_error")
        self.assertIn("error", result)

    # 11. Empty results
    def test_empty_results(self):
        req = JivChatRequest(message="search recipes for mythicaldragonfruit")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_result["total"], 0)
        self.assertTrue("no matching records were found" in res.reply.lower() or "no recipes matched" in res.reply.lower())

    # 12. LLM/tool failure
    def test_llm_tool_failure_graceful_handling(self):
        set_llm_provider(FailingMockProvider())
        req = JivChatRequest(message="What should I cook?")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertIn("temporarily unable", res.reply)
        self.assertIn("LLM provider unavailable", res.warnings)

    # 13. Deterministic restriction overriding an LLM suggestion
    def test_deterministic_restriction_overrides_llm_suggestion(self):
        profile = UserProfileSchema(allergies=["peanut"])
        hallucinated_llm_text = "Peanut is fine for you, feel free to try peanut."
        safe_text = RestrictionGuard.enforce_text_safety(
            text=hallucinated_llm_text,
            blocked_items=["peanut"],
            profile=profile,
        )
        self.assertIn("Deterministic Safety Alert", safe_text)
        self.assertIn("conflicts with your saved food profile", safe_text)

    # 14. LLM cannot fabricate unavailable data
    def test_llm_cannot_fabricate_unavailable_data(self):
        # When tool returned empty result, hallucination guard sanitizes fake claims
        fake_response = "Here are 5 delicious recipes using dragonfruit: Recipe 1..."
        sanitized = HallucinationGuard.sanitize_response(
            text=fake_response,
            tool_called="search_recipes",
            tool_result={"items": []},
        )
        self.assertIn("no matching records were found", sanitized.lower())
        self.assertIn("cannot generate or assume", sanitized.lower())

    # 15. Optimize basket tool
    def test_optimize_basket(self):
        req = JivChatRequest(message="Optimize grocery basket for high protein")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "optimize_basket")
        self.assertGreaterEqual(res.tool_result["count"], 1)
        self.assertEqual(res.tool_result["priority_applied"], "high_protein")

    # 16. Explain result tool
    def test_explain_result(self):
        req = JivChatRequest(message="Why was masoor-1 recommended?")
        res = jiv_agent.process(db=self.db, request=req)
        self.assertEqual(res.tool_called, "explain_result")
        self.assertEqual(res.tool_result["factors"]["recipe_name"], "Masoor Dal Tadka")
        self.assertIn("Masoor Dal Tadka", res.reply)

    # 17. FastAPI HTTP Endpoint Handlers
    def test_fastapi_endpoints(self):
        from app.jiv.api import chat_with_jiv, list_jiv_tools, jiv_status

        # Test /status handler
        status_res = jiv_status()
        self.assertEqual(status_res["status"], "online")
        self.assertEqual(status_res["tools_count"], 8)

        # Test /tools handler
        tools_res = list_jiv_tools()
        self.assertEqual(len(tools_res), 8)

        # Test /chat handler
        chat_res = chat_with_jiv(
            request=JivChatRequest(message="Give me a recipe using masoor dal"),
            db=self.db,
        )
        self.assertEqual(chat_res.tool_called, "search_recipes")
        self.assertIn("Masoor Dal Tadka", chat_res.reply)


if __name__ == "__main__":
    unittest.main()
