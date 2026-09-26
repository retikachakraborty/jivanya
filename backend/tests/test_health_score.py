import unittest
from app.core.database import SessionLocal
from app.models.product import Product
from app.api.health_score import evaluate_health_score, find_healthy_swaps, get_product_scorecard_data

class TestHealthScore(unittest.TestCase):
    def test_clean_product_gets_grade_a(self):
        score, grade, grade_label, summary, hfss, clean, profile, palm, maida = evaluate_health_score(
            energy_100g=380.0,
            protein_100g=12.5,
            carbohydrates_100g=65.0,
            sugars_100g=1.5,
            fat_100g=8.0,
            saturated_fat_100g=1.5,
            fiber_100g=10.0,
            sodium_100g=0.01,
            ingredients_text="100% Rolled Oats",
        )
        self.assertGreaterEqual(score, 80)
        self.assertEqual(grade, "A")
        self.assertFalse(palm)
        self.assertFalse(maida)
        codes = [c.code for c in clean]
        self.assertIn("HIGH_FIBER", codes)
        self.assertIn("SOURCE_OF_PROTEIN", codes)

    def test_sugary_palm_oil_product_gets_hfss_alerts(self):
        score, grade, grade_label, summary, hfss, clean, profile, palm, maida = evaluate_health_score(
            energy_100g=480.0,
            protein_100g=5.0,
            carbohydrates_100g=72.0,
            sugars_100g=28.0,
            fat_100g=20.0,
            saturated_fat_100g=9.5,
            fiber_100g=1.0,
            sodium_100g=0.4,
            ingredients_text="Refined wheat flour (maida), sugar, refined palm oil, invert sugar syrup, cocoa solids",
        )
        self.assertLessEqual(score, 40)
        self.assertIn(grade, ["D", "E"])
        self.assertTrue(palm)
        self.assertTrue(maida)
        hfss_codes = [h.code for h in hfss]
        self.assertIn("VERY_HIGH_SUGAR", hfss_codes)
        self.assertIn("VERY_HIGH_SAT_FAT", hfss_codes)
        self.assertIn("CONTAINS_PALM_OIL", hfss_codes)
        self.assertIn("CONTAINS_MAIDA", hfss_codes)

    def test_allergen_profile_conflict(self):
        _, _, _, _, _, _, profile_warnings, _, _ = evaluate_health_score(
            energy_100g=550.0,
            protein_100g=24.0,
            carbohydrates_100g=20.0,
            sugars_100g=8.0,
            fat_100g=45.0,
            saturated_fat_100g=6.0,
            fiber_100g=6.0,
            sodium_100g=0.3,
            ingredients_text="Roasted Peanuts, Salt",
            allergens="Peanuts",
            user_allergies=["peanut", "shellfish"],
        )
        self.assertTrue(any("peanut" in w.message.lower() for w in profile_warnings))

    def test_vegan_dairy_conflict(self):
        _, _, _, _, _, _, profile_warnings, _, _ = evaluate_health_score(
            energy_100g=120.0,
            protein_100g=8.0,
            carbohydrates_100g=10.0,
            sugars_100g=8.0,
            fat_100g=4.0,
            saturated_fat_100g=2.5,
            fiber_100g=0.0,
            sodium_100g=0.1,
            ingredients_text="Pasteurised toned milk, active culture, milk solids",
            user_diet="vegan",
        )
        self.assertTrue(any("vegan" in w.message.lower() for w in profile_warnings))

    def test_sodium_values_are_milligrams_per_100g(self):
        low = evaluate_health_score(
            380, 12, 65, 2, 8, 1.5, 10, 9.5, "Rolled oats"
        )
        high = evaluate_health_score(
            380, 12, 65, 2, 8, 1.5, 10, 9500, "Salted oats"
        )
        self.assertFalse(any(w.code.endswith("SODIUM") for w in low[4]))
        self.assertIn("VERY_HIGH_SODIUM", [w.code for w in high[4]])
        self.assertIn("9500mg", high[4][0].description)

    def test_healthy_swaps_from_db(self):
        db = SessionLocal()
        try:
            # Find an unhealthy biscuit
            biscuit = db.query(Product).filter(
                Product.category == "Biscuits",
                Product.sugars_100g > 15.0
            ).first()

            if biscuit:
                scorecard = get_product_scorecard_data(biscuit, db=db)
                self.assertIsNotNone(scorecard.grade)
                # Swaps should have higher scores
                for swap in scorecard.healthy_swaps:
                    self.assertGreater(swap.score, scorecard.score)
                    self.assertEqual(swap.product.category, "Biscuits")
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
