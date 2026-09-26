from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductItem
from app.schemas.health_score import (
    HealthScorecard,
    ProductRuleWarning,
    CleanHighlight,
    ProfileWarning,
    HealthySwap,
    ProductScoreResponse,
    ScoreFactor,
)

PALM_OIL_KEYWORDS = ["palm oil", "palmolein", "palm fat", "fractionated palm", "hydrogenated palm"]
MAIDA_KEYWORDS = ["refined wheat flour", "maida", "bleached flour", "enriched flour", "all-purpose flour"]
WHOLE_GRAIN_KEYWORDS = ["whole wheat", "whole grain", "rolled oats", "oat flakes", "ragi", "jowar", "bajra", "quinoa"]
GRADE_THRESHOLDS = {
    "A": "80–100",
    "B": "65–79",
    "C": "50–64",
    "D": "35–49",
    "E": "5–34",
}

def score_breakdown(
    protein_100g: Optional[float],
    sugars_100g: Optional[float],
    saturated_fat_100g: Optional[float],
    fiber_100g: Optional[float],
    sodium_100g: Optional[float],
    ingredients_text: Optional[str],
) -> List[ScoreFactor]:
    """Return the same deterministic contributions used by evaluate_health_score."""
    factors = [ScoreFactor(label="Base score", points=70, reason="Every product starts at 70 points under Jivanya's score rules.")]
    sugar = sugars_100g or 0.0
    if sugar > 22:
        factors.append(ScoreFactor(label="Very high sugar", points=-25, reason=f"Stored sugar is {sugar:.1f}g/100g, above 22g/100g."))
    elif sugar > 10:
        factors.append(ScoreFactor(label="High sugar", points=-15, reason=f"Stored sugar is {sugar:.1f}g/100g, above 10g/100g."))
    elif sugar > 5:
        factors.append(ScoreFactor(label="Moderate sugar", points=-5, reason=f"Stored sugar is {sugar:.1f}g/100g, above 5g/100g."))
    elif sugars_100g is not None and sugar <= 2:
        factors.append(ScoreFactor(label="Low sugar", points=5, reason=f"Stored sugar is {sugar:.1f}g/100g."))

    sat_fat = saturated_fat_100g or 0.0
    if sat_fat > 8:
        factors.append(ScoreFactor(label="Very high saturated fat", points=-20, reason=f"Stored saturated fat is {sat_fat:.1f}g/100g, above 8g/100g."))
    elif sat_fat > 4:
        factors.append(ScoreFactor(label="High saturated fat", points=-10, reason=f"Stored saturated fat is {sat_fat:.1f}g/100g, above 4g/100g."))
    elif saturated_fat_100g is not None and sat_fat <= 1.5:
        factors.append(ScoreFactor(label="Low saturated fat", points=5, reason=f"Stored saturated fat is {sat_fat:.1f}g/100g."))

    sodium = sodium_100g or 0.0
    if sodium > 900:
        factors.append(ScoreFactor(label="Very high sodium", points=-15, reason=f"Stored sodium is {sodium:.0f}mg/100g, above 900mg/100g."))
    elif sodium > 600:
        factors.append(ScoreFactor(label="High sodium", points=-8, reason=f"Stored sodium is {sodium:.0f}mg/100g, above 600mg/100g."))

    fiber = fiber_100g or 0.0
    if fiber >= 6:
        factors.append(ScoreFactor(label="High fibre", points=15, reason=f"Stored fibre is {fiber:.1f}g/100g, at least 6g/100g."))
    elif fiber >= 3:
        factors.append(ScoreFactor(label="Fibre contribution", points=8, reason=f"Stored fibre is {fiber:.1f}g/100g, at least 3g/100g."))

    protein = protein_100g or 0.0
    if protein >= 15:
        factors.append(ScoreFactor(label="High protein", points=15, reason=f"Stored protein is {protein:.1f}g/100g, at least 15g/100g."))
    elif protein >= 8:
        factors.append(ScoreFactor(label="Protein contribution", points=8, reason=f"Stored protein is {protein:.1f}g/100g, at least 8g/100g."))

    ingredients = (ingredients_text or "").lower()
    if any(keyword in ingredients for keyword in PALM_OIL_KEYWORDS):
        factors.append(ScoreFactor(label="Palm oil listed", points=-15, reason="The stored ingredient list contains a palm-oil keyword."))
    if any(keyword in ingredients for keyword in MAIDA_KEYWORDS):
        factors.append(ScoreFactor(label="Refined flour listed", points=-10, reason="The stored ingredient list contains a refined-flour keyword."))
    if any(keyword in ingredients for keyword in WHOLE_GRAIN_KEYWORDS):
        factors.append(ScoreFactor(label="Whole-grain ingredient listed", points=5, reason="The stored ingredient list contains a Jivanya whole-grain keyword."))
    return factors

def evaluate_health_score(
    energy_100g: Optional[float],
    protein_100g: Optional[float],
    carbohydrates_100g: Optional[float],
    sugars_100g: Optional[float],
    fat_100g: Optional[float],
    saturated_fat_100g: Optional[float],
    fiber_100g: Optional[float],
    sodium_100g: Optional[float],
    ingredients_text: Optional[str],
    allergens: Optional[str] = None,
    user_allergies: Optional[List[str]] = None,
    user_exclusions: Optional[List[str]] = None,
    user_diet: Optional[str] = None,
) -> Tuple[int, str, str, str, List[ProductRuleWarning], List[CleanHighlight], List[ProfileWarning], bool, bool]:
    score = 70.0
    hfss_warnings: List[ProductRuleWarning] = []
    clean_highlights: List[CleanHighlight] = []
    profile_warnings: List[ProfileWarning] = []

    ingr_lower = (ingredients_text or "").lower()
    allergens_lower = (allergens or "").lower()

    # 1. Sugar rule, evaluated from the stored product value.
    sugar = sugars_100g or 0.0
    if sugar > 22.0:
        score -= 25.0
        hfss_warnings.append(ProductRuleWarning(
            code="VERY_HIGH_SUGAR",
            label="Very High Added Sugar",
            severity="danger",
            description=f"Contains {sugar:.1f}g sugar per 100g (>22g/100g under Jivanya's rule)."
        ))
    elif sugar > 10.0:
        score -= 15.0
        hfss_warnings.append(ProductRuleWarning(
            code="HIGH_SUGAR",
            label="High sugar",
            severity="warning",
            description=f"Contains {sugar:.1f}g sugar per 100g (above Jivanya's 10g/100g rule)."
        ))
    elif sugar > 5.0:
        score -= 5.0
    elif sugar <= 2.0 and sugars_100g is not None:
        score += 5.0
        clean_highlights.append(CleanHighlight(
            code="LOW_SUGAR",
            label="Low / Zero Added Sugar",
            description=f"Contains only {sugar:.1f}g sugar per 100g."
        ))

    # 2. Saturated-fat rule, evaluated from the stored product value.
    sat_fat = saturated_fat_100g or 0.0
    if sat_fat > 8.0:
        score -= 20.0
        hfss_warnings.append(ProductRuleWarning(
            code="VERY_HIGH_SAT_FAT",
            label="Very High Saturated Fat",
            severity="danger",
            description=f"Contains {sat_fat:.1f}g saturated fat per 100g (>8% sat fat)."
        ))
    elif sat_fat > 4.0:
        score -= 10.0
        hfss_warnings.append(ProductRuleWarning(
            code="HIGH_SAT_FAT",
            label="High saturated fat",
            severity="warning",
            description=f"Contains {sat_fat:.1f}g saturated fat per 100g (above Jivanya's 4g/100g rule)."
        ))
    elif sat_fat <= 1.5 and saturated_fat_100g is not None:
        score += 5.0
        clean_highlights.append(CleanHighlight(
            code="LOW_SAT_FAT",
            label="Heart-Healthy / Low Saturated Fat",
            description=f"Contains only {sat_fat:.1f}g saturated fat per 100g."
        ))

    # Product imports store sodium_100g in milligrams per 100g.
    sod_mg = sodium_100g or 0.0
    if sod_mg > 900.0:
        score -= 15.0
        hfss_warnings.append(ProductRuleWarning(
            code="VERY_HIGH_SODIUM",
            label="Very High Sodium",
            severity="danger",
            description=f"Contains {sod_mg:.0f}mg sodium per 100g (exceeds 900mg/100g limit)."
        ))
    elif sod_mg > 600.0:
        score -= 8.0
        hfss_warnings.append(ProductRuleWarning(
            code="HIGH_SODIUM",
            label="High sodium",
            severity="warning",
            description=f"Contains {sod_mg:.0f}mg sodium per 100g (above Jivanya's 600mg/100g rule)."
        ))

    # 4. Dietary Fiber
    fib = fiber_100g or 0.0
    if fib >= 6.0:
        score += 15.0
        clean_highlights.append(CleanHighlight(
            code="HIGH_FIBER",
            label="Excellent Source of Fiber",
            description=f"Provides {fib:.1f}g dietary fiber per 100g for gut health and satiety."
        ))
    elif fib >= 3.0:
        score += 8.0
        clean_highlights.append(CleanHighlight(
            code="SOURCE_OF_FIBER",
            label="Good Source of Fiber",
            description=f"Provides {fib:.1f}g dietary fiber per 100g."
        ))

    # 5. Protein
    prot = protein_100g or 0.0
    if prot >= 15.0:
        score += 15.0
        clean_highlights.append(CleanHighlight(
            code="HIGH_PROTEIN",
            label="High Protein Powerhouse",
            description=f"Rich in protein with {prot:.1f}g per 100g."
        ))
    elif prot >= 8.0:
        score += 8.0
        clean_highlights.append(CleanHighlight(
            code="SOURCE_OF_PROTEIN",
            label="Good Source of Protein",
            description=f"Provides {prot:.1f}g protein per 100g."
        ))

    # 6. Ingredient Checks (Palm Oil, Maida, Whole Grains)
    contains_palm_oil = any(k in ingr_lower for k in PALM_OIL_KEYWORDS)
    if contains_palm_oil:
        score -= 15.0
        hfss_warnings.append(ProductRuleWarning(
            code="CONTAINS_PALM_OIL",
            label="Contains Palm Oil / Palmolein",
            severity="danger",
            description="Manufactured with palm oil or refined palmolein, high in atherogenic palmitic acid."
        ))
    # An ingredient list that omits palm oil does not prove its absence.
    # Only report the positive finding when the stored list explicitly contains it.

    contains_maida = any(k in ingr_lower for k in MAIDA_KEYWORDS)
    if contains_maida:
        score -= 10.0
        hfss_warnings.append(ProductRuleWarning(
            code="CONTAINS_MAIDA",
            label="Contains Refined Wheat Flour (Maida)",
            severity="warning",
            description="Uses refined maida stripped of germ and bran fiber."
        ))

    contains_whole_grain = any(k in ingr_lower for k in WHOLE_GRAIN_KEYWORDS)
    if contains_whole_grain:
        score += 5.0
        clean_highlights.append(CleanHighlight(
            code="WHOLE_GRAIN",
            label="Wholesome Whole Grains",
            description="Formulated with whole wheat, rolled oats, or millets."
        ))

    # 7. User Profile Checks (Allergens, Exclusions, Diet)
    if user_allergies:
        for allergy in user_allergies:
            al = allergy.strip().lower()
            if al and (al in ingr_lower or al in allergens_lower):
                profile_warnings.append(ProfileWarning(
                    type="allergy",
                    message=f"⚠️ Allergen Conflict: This product contains or may contain '{allergy}', which is in your allergy profile."
                ))

    if user_exclusions:
        for excl in user_exclusions:
            ex = excl.strip().lower()
            if ex and (ex in ingr_lower or ex in allergens_lower):
                profile_warnings.append(ProfileWarning(
                    type="exclusion",
                    message=f"⚠️ Ingredient Exclusion: Matches your exclusion for '{excl}'."
                ))

    if user_diet:
        diet = user_diet.lower()
        if "vegan" in diet and any(d in ingr_lower or d in allergens_lower for d in ["milk", "dairy", "butter", "curd", "paneer", "whey", "ghee", "honey", "casein"]):
            profile_warnings.append(ProfileWarning(
                type="diet",
                message="⚠️ Diet Warning: Contains dairy or animal-derived ingredients, which conflicts with your Vegan diet preference."
            ))

    final_score = max(5, min(100, round(score)))

    if final_score >= 80:
        grade = "A"
        grade_label = "Excellent / Clean"
        summary = "Highly nutritious choice with wholesome ingredients, clean macronutrients, and low harmful additives."
    elif final_score >= 65:
        grade = "B"
        grade_label = "Good"
        summary = "Balanced profile suitable for regular consumption with moderate nutrient density."
    elif final_score >= 50:
        grade = "C"
        grade_label = "Moderate"
        summary = "Average nutritional quality. Best consumed in moderation as part of a balanced diet."
    elif final_score >= 35:
        grade = "D"
        grade_label = "Poor under Jivanya's rules"
        summary = "High in added sugars, saturated fats, or refined flour. Look for healthier alternatives below."
    else:
        grade = "E"
        grade_label = "Ultra-Processed"
        summary = "Heavily processed with high sugar, palm oil, or excessive saturated fat. A healthier swap is strongly advised."

    return (
        final_score,
        grade,
        grade_label,
        summary,
        hfss_warnings,
        clean_highlights,
        profile_warnings,
        contains_palm_oil,
        contains_maida,
    )

def find_healthy_swaps(
    current_product: Product,
    current_score: int,
    db: Session,
    user_allergies: Optional[List[str]] = None,
    user_exclusions: Optional[List[str]] = None,
    limit: int = 3
) -> List[HealthySwap]:
    if not current_product.category:
        return []

    # Query items in same category
    candidates = db.query(Product).filter(
        Product.category == current_product.category,
        Product.barcode != current_product.barcode,
    ).all()

    scored_candidates: List[Tuple[Product, int, str, List[CleanHighlight]]] = []

    for cand in candidates:
        cand_ingr = (cand.ingredients_text or "").lower()
        cand_all = (cand.allergens or "").lower()

        # Filter out user allergens if specified
        if user_allergies and any(al.lower() in cand_ingr or al.lower() in cand_all for al in user_allergies if al):
            continue

        c_score, c_grade, _, _, _, c_cleans, _, _, _ = evaluate_health_score(
            energy_100g=cand.energy_100g,
            protein_100g=cand.protein_100g,
            carbohydrates_100g=cand.carbohydrates_100g,
            sugars_100g=cand.sugars_100g,
            fat_100g=cand.fat_100g,
            saturated_fat_100g=cand.saturated_fat_100g,
            fiber_100g=cand.fiber_100g,
            sodium_100g=cand.sodium_100g,
            ingredients_text=cand.ingredients_text,
            allergens=cand.allergens,
        )

        # Must be healthier than current product (at least +8 points or Grade A/B)
        if c_score > current_score and (c_score >= 65 or c_score >= current_score + 10):
            scored_candidates.append((cand, c_score, c_grade, c_cleans))

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    swaps: List[HealthySwap] = []
    for cand, c_score, c_grade, c_cleans in scored_candidates[:limit]:
        highlights: List[str] = []

        # Sugar reduction
        sugar_diff_pct = None
        if current_product.sugars_100g and cand.sugars_100g is not None and current_product.sugars_100g > 0:
            reduction = ((current_product.sugars_100g - cand.sugars_100g) / current_product.sugars_100g) * 100
            if reduction > 10:
                sugar_diff_pct = round(reduction, 1)
                highlights.append(f"{sugar_diff_pct:.0f}% less sugar")

        # Sat fat reduction
        sat_fat_diff_pct = None
        if current_product.saturated_fat_100g and cand.saturated_fat_100g is not None and current_product.saturated_fat_100g > 0:
            reduction = ((current_product.saturated_fat_100g - cand.saturated_fat_100g) / current_product.saturated_fat_100g) * 100
            if reduction > 10:
                sat_fat_diff_pct = round(reduction, 1)
                highlights.append(f"{sat_fat_diff_pct:.0f}% less saturated fat")

        # Protein multiplier
        protein_multiplier = None
        if current_product.protein_100g and cand.protein_100g and current_product.protein_100g > 0:
            ratio = cand.protein_100g / current_product.protein_100g
            if ratio >= 1.4:
                protein_multiplier = round(ratio, 1)
                highlights.append(f"{protein_multiplier:.1f}× more protein")

        # Clean highlights
        cand_ingr_lower = (cand.ingredients_text or "").lower()
        if any(k in cand_ingr_lower for k in WHOLE_GRAIN_KEYWORDS):
            highlights.append("Whole grain ingredient listed")

        if not highlights:
            for cl in c_cleans[:2]:
                highlights.append(cl.label)

        swaps.append(HealthySwap(
            product=ProductItem.model_validate(cand),
            score=c_score,
            grade=c_grade,
            sugar_diff_pct=sugar_diff_pct,
            sat_fat_diff_pct=sat_fat_diff_pct,
            protein_multiplier=protein_multiplier,
            highlights=highlights,
        ))

    return swaps

def get_product_scorecard_data(
    product: Product,
    db: Session,
    user_allergies: Optional[List[str]] = None,
    user_exclusions: Optional[List[str]] = None,
    user_diet: Optional[str] = None,
) -> HealthScorecard:
    (
        score,
        grade,
        grade_label,
        summary,
        hfss_warnings,
        clean_highlights,
        profile_warnings,
        contains_palm_oil,
        contains_maida,
    ) = evaluate_health_score(
        energy_100g=product.energy_100g,
        protein_100g=product.protein_100g,
        carbohydrates_100g=product.carbohydrates_100g,
        sugars_100g=product.sugars_100g,
        fat_100g=product.fat_100g,
        saturated_fat_100g=product.saturated_fat_100g,
        fiber_100g=product.fiber_100g,
        sodium_100g=product.sodium_100g,
        ingredients_text=product.ingredients_text,
        allergens=product.allergens,
        user_allergies=user_allergies,
        user_exclusions=user_exclusions,
        user_diet=user_diet,
    )

    swaps = find_healthy_swaps(
        current_product=product,
        current_score=score,
        db=db,
        user_allergies=user_allergies,
        user_exclusions=user_exclusions,
        limit=3,
    )

    return HealthScorecard(
        score=score,
        grade=grade,
        grade_label=grade_label,
        summary=summary,
        rule_warnings=hfss_warnings,
        clean_highlights=clean_highlights,
        profile_warnings=profile_warnings,
        contains_palm_oil=contains_palm_oil,
        contains_maida=contains_maida,
        healthy_swaps=swaps,
        score_breakdown=score_breakdown(
            protein_100g=product.protein_100g,
            sugars_100g=product.sugars_100g,
            saturated_fat_100g=product.saturated_fat_100g,
            fiber_100g=product.fiber_100g,
            sodium_100g=product.sodium_100g,
            ingredients_text=product.ingredients_text,
        ),
        grade_thresholds=GRADE_THRESHOLDS,
    )
