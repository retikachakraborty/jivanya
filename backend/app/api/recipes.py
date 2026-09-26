import re
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, exists, func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.nutrition import IngredientAlias
from app.models.recipe import Recipe, RecipeIngredient
from app.schemas.recipe import RecipeItem, RecipeListResponse

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])

# These labels exist in the current recipe corpus. An explicit whitelist avoids
# treating "High Protein Non Vegetarian" as vegetarian via substring matching.
VEGETARIAN_DIET_LABELS = {"vegetarian", "high protein vegetarian", "vegan"}
VEGAN_DIET_LABELS = {"vegan"}

# Terms are whole words/phrases. This deliberately does not equate coconut or
# nutmeg with tree nuts.
NUT_FAMILY_TERMS = {
    "almond", "badam", "cashew", "cashew nut", "kaju", "walnut", "akhrot",
    "pistachio", "pista", "hazelnut", "pecan", "macadamia", "brazil nut",
    "pine nut", "ground nut", "groundnut", "peanut", "mixed nut", "nutella",
    "nut",
}
# Diet compatibility vocabulary only: these terms are consulted only for an explicit saved diet.
VEGETARIAN_INCOMPATIBLE = {
    "chicken", "mutton", "lamb", "beef", "pork", "fish", "prawn", "shrimp",
    "crab", "lobster", "bacon", "ham", "sausage", "salami", "anchovy",
    "meat", "egg",
}
VEGAN_INCOMPATIBLE = VEGETARIAN_INCOMPATIBLE | {
    "milk", "curd", "yogurt", "paneer", "cheese", "butter", "ghee",
    "cream", "whey", "casein", "honey", "buttermilk",
}
PLANT_BASED_EXCEPTIONS = {
    "almond milk", "coconut milk", "soy milk", "oat milk", "cashew milk",
    "almond yogurt", "coconut yogurt", "soy yogurt", "coconut curd",
    "peanut butter", "almond butter", "cashew butter", "coconut butter",
    "coconut cream", "vegan cheese",
}


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _terms(values: list[str]) -> list[str]:
    return sorted({_normalize(value) for value in values if _normalize(value)})


def _term_pattern(term: str) -> str:
    words = _normalize(term).split()
    if not words:
        return r"(?!)"
    # Match singular and plural for the final word, preserving word boundaries.
    words[-1] = re.escape(words[-1].removesuffix("s")) + "s?"
    phrase = r"\s+".join(words)
    return rf"(^|[^A-Za-z0-9]){phrase}([^A-Za-z0-9]|$)"


def _ingredient_matches(ingredient: str, term: str) -> bool:
    normalized = _normalize(term)
    candidates = {normalized}
    if normalized in {"nut", "nuts", "tree nut", "tree nuts"}:
        candidates.update(NUT_FAMILY_TERMS)
    return any(re.search(_term_pattern(candidate), ingredient, flags=re.IGNORECASE) for candidate in candidates)


def _matches_any(ingredient: str, terms: set[str] | list[str]) -> bool:
    return any(_ingredient_matches(ingredient, term) for term in terms)


def _expand_ingredient_terms(db: Session, terms: list[str]) -> set[str]:
    expanded = set(_terms(terms))
    if expanded & {"nut", "nuts", "tree nut", "tree nuts"}:
        expanded.update(NUT_FAMILY_TERMS)
        # IFCT-backed canonical ingredient groups. Read aliases rather than
        # guessing regional spellings such as kaju, pista, or moog phali.
        canonicals = {"almond", "cashew nut", "ground nut", "pistachio nuts", "walnut"}
        alias_rows = db.query(IngredientAlias.alias, IngredientAlias.canonical).filter(
            func.lower(func.trim(IngredientAlias.canonical)).in_(canonicals)
        ).all()
        for alias, canonical in alias_rows:
            expanded.add(_normalize(canonical))
            expanded.update(_terms(alias.split(",")))
    direct_aliases = db.query(IngredientAlias.alias, IngredientAlias.canonical).filter(
        or_(
            func.lower(func.trim(IngredientAlias.alias)).in_(expanded),
            func.lower(func.trim(IngredientAlias.canonical)).in_(expanded),
        )
    ).all()
    canonical_names = {_normalize(canonical) for _, canonical in direct_aliases}
    if canonical_names:
        canonical_rows = db.query(IngredientAlias.alias, IngredientAlias.canonical).filter(
            func.lower(func.trim(IngredientAlias.canonical)).in_(canonical_names)
        ).all()
        for alias, canonical in [*direct_aliases, *canonical_rows]:
            expanded.add(_normalize(canonical))
            expanded.update(_terms(alias.split(",")))
    return {term for term in expanded if term}


def _diet_label_allowed(label: Optional[str], preference: Optional[str]) -> bool:
    diet = _normalize(preference or "")
    if not diet:
        return True
    actual = _normalize(label or "")
    if diet == "vegetarian":
        return actual in VEGETARIAN_DIET_LABELS
    if diet == "vegan":
        return actual in VEGAN_DIET_LABELS
    return actual == diet


def _diet_ingredient_conflict(ingredient: str, preference: Optional[str]) -> bool:
    diet = _normalize(preference or "")
    if diet not in {"vegetarian", "vegan"}:
        return False
    blocked = VEGETARIAN_INCOMPATIBLE if diet == "vegetarian" else VEGAN_INCOMPATIBLE
    for term in blocked:
        if not _ingredient_matches(ingredient, term):
            continue
        if diet == "vegan" and any(
            _ingredient_matches(ingredient, exception)
            and _ingredient_matches(exception, term)
            for exception in PLANT_BASED_EXCEPTIONS
        ):
            continue
        return True
    return False


def _ingredient_predicate(terms: set[str] | list[str]):
    patterns = [_term_pattern(term) for term in sorted(terms) if term]
    if not patterns:
        return None
    return or_(*(RecipeIngredient.ingredient.regexp_match(pattern, flags="i") for pattern in patterns))


def _exclusion_predicates(terms: set[str] | list[str], no_onion: bool, no_garlic: bool):
    values = set(terms)
    if no_onion:
        values.add("onion")
    if no_garlic:
        values.add("garlic")
    patterns = [_term_pattern(term) for term in sorted(values) if term]
    return [
        ~exists().where(
            and_(
                RecipeIngredient.recipe_id == Recipe.recipe_id,
                RecipeIngredient.ingredient.regexp_match(pattern, flags="i"),
            )
        ).correlate(Recipe)
        for pattern in patterns
    ]


def _diet_predicates(preferences: list[Optional[str]]):
    predicates = []
    for preference in preferences:
        diet = _normalize(preference or "")
        if not diet:
            continue
        actual = func.lower(func.trim(func.coalesce(Recipe.diet, "")))
        if diet == "vegetarian":
            predicates.append(actual.in_(VEGETARIAN_DIET_LABELS))
            incompatible = VEGETARIAN_INCOMPATIBLE
        elif diet == "vegan":
            predicates.append(actual.in_(VEGAN_DIET_LABELS))
            incompatible = VEGAN_INCOMPATIBLE
        else:
            predicates.append(actual == diet)
            continue
        # The source corpus contains a small number of recipes whose diet tag
        # conflicts with their structured ingredients, so enforce both fields.
        for term in sorted(incompatible):
            if diet == "vegan":
                continue
            pattern = _term_pattern(term)
            predicates.append(
                ~exists().where(
                    and_(
                        RecipeIngredient.recipe_id == Recipe.recipe_id,
                        RecipeIngredient.ingredient.regexp_match(pattern, flags="i"),
                    )
                ).correlate(Recipe)
            )
        if diet == "vegan":
            for term in sorted(incompatible):
                pattern = _term_pattern(term)
                # Plant-based milk/yogurt/butter/cream labels are explicit
                # exceptions and stay eligible for vegan recipes.
                matching_exceptions = [
                    _term_pattern(exception) for exception in PLANT_BASED_EXCEPTIONS
                    if _ingredient_matches(exception, term)
                ]
                conflict = RecipeIngredient.ingredient.regexp_match(pattern, flags="i")
                conditions = [
                    RecipeIngredient.recipe_id == Recipe.recipe_id,
                    conflict,
                ]
                if matching_exceptions:
                    exception = or_(*(
                        RecipeIngredient.ingredient.regexp_match(p, flags="i")
                        for p in matching_exceptions
                    ))
                    conditions.append(~exception)
                predicates.append(
                    ~exists().where(and_(*conditions)).correlate(Recipe)
                )
    return predicates


def _safe_matching_terms(
    requested: list[str],
    restrictions: set[str],
    no_onion: bool,
    no_garlic: bool,
    diet: Optional[str],
) -> tuple[list[str], list[str]]:
    safe, rejected = [], []
    for ingredient in _terms(requested):
        if (
            _matches_any(ingredient, restrictions)
            or (no_onion and _ingredient_matches(ingredient, "onion"))
            or (no_garlic and _ingredient_matches(ingredient, "garlic"))
            or _diet_ingredient_conflict(ingredient, diet)
        ):
            rejected.append(ingredient)
        else:
            safe.append(ingredient)
    return safe, rejected


def _ingredient_map(db: Session, recipe_ids: list[str]) -> dict[str, list[str]]:
    if not recipe_ids:
        return {}
    rows = db.query(RecipeIngredient.recipe_id, RecipeIngredient.ingredient).filter(
        RecipeIngredient.recipe_id.in_(recipe_ids)
    ).all()
    result: dict[str, list[str]] = defaultdict(list)
    for recipe_id, ingredient in rows:
        if ingredient not in result[recipe_id]:
            result[recipe_id].append(ingredient)
    for recipe_id in recipe_ids:
        result.setdefault(recipe_id, [])
    return result


def _to_items(
    recipes: list[Recipe],
    ingredient_map: dict[str, list[str]],
    requested: list[str] | None = None,
) -> list[RecipeItem]:
    requested_terms = _terms(requested or [])
    items = []
    for recipe in recipes:
        ingredients = ingredient_map.get(recipe.recipe_id, [])
        matched = [
            ingredient for ingredient in ingredients
            if any(_ingredient_matches(ingredient, term) for term in requested_terms)
        ]
        items.append(RecipeItem(
            recipe_id=recipe.recipe_id,
            recipe_name=recipe.recipe_name,
            ingredients_raw=recipe.ingredients_raw,
            instructions=recipe.instructions,
            cuisine=recipe.cuisine,
            course=recipe.course,
            diet=recipe.diet,
            prep_minutes=recipe.prep_minutes,
            cook_minutes=recipe.cook_minutes,
            total_minutes=recipe.total_minutes,
            servings=recipe.servings,
            source_url=recipe.source_url,
            ingredients=ingredients,
            matched_ingredients=matched,
            matching_count=len(matched),
        ))
    return items


def _base_query(
    db: Session,
    query: Optional[str],
    cuisine: Optional[str],
    course: Optional[str],
    diet: Optional[str],
    diet_filter: Optional[str],
    ingredient: Optional[str],
    exclude_ingredients: set[str],
    no_onion: bool,
    no_garlic: bool,
):
    statement = db.query(Recipe)
    if query:
        like = f"%{query.strip()}%"
        statement = statement.filter(or_(
            Recipe.recipe_name.ilike(like),
            Recipe.cuisine.ilike(like),
            Recipe.course.ilike(like),
            Recipe.diet.ilike(like),
            Recipe.ingredients_raw.ilike(like),
        ))
    if cuisine:
        statement = statement.filter(func.lower(func.trim(Recipe.cuisine)) == cuisine.strip().lower())
    if course:
        statement = statement.filter(Recipe.course.ilike(f"%{course.strip()}%"))
    for preference in (diet, diet_filter):
        if preference:
            statement = statement.filter(*_diet_predicates([preference]))
    needs_ingredient_evidence = bool(exclude_ingredients or no_onion or no_garlic) or any(
        _normalize(preference or "") in {"vegetarian", "vegan"}
        for preference in (diet, diet_filter)
    )
    if needs_ingredient_evidence:
        statement = statement.filter(
            exists().where(
                RecipeIngredient.recipe_id == Recipe.recipe_id
            ).correlate(Recipe)
        )
    if ingredient:
        expanded = _expand_ingredient_terms(db, [ingredient])
        predicate = _ingredient_predicate(expanded)
        if predicate is not None:
            statement = statement.filter(
                exists().where(and_(
                    RecipeIngredient.recipe_id == Recipe.recipe_id,
                    predicate,
                )).correlate(Recipe)
            )
    for predicate in _exclusion_predicates(exclude_ingredients, no_onion, no_garlic):
        statement = statement.filter(predicate)
    return statement


@router.get("", response_model=RecipeListResponse)
def list_recipes(
    query: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    course: Optional[str] = Query(None),
    diet: Optional[str] = Query(None, description="Saved dietary preference hard constraint"),
    diet_filter: Optional[str] = Query(None, description="Exact corpus diet label filter"),
    ingredient: Optional[str] = Query(None),
    exclude: Optional[str] = Query(None, description="Comma-separated allergies and exclusions"),
    no_onion: bool = False,
    no_garlic: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    restrictions = _expand_ingredient_terms(db, (exclude or "").split(","))
    statement = _base_query(
        db, query, cuisine, course, diet, diet_filter, ingredient,
        restrictions, no_onion, no_garlic,
    )
    total = statement.order_by(None).count()
    recipes = statement.order_by(Recipe.recipe_name.asc()).offset(offset).limit(limit).all()
    ingredients = _ingredient_map(db, [recipe.recipe_id for recipe in recipes])
    return RecipeListResponse(
        items=_to_items(recipes, ingredients),
        total=total,
        offset=offset,
        limit=limit,
        status="FOUND" if recipes else "NO_DATABASE_MATCH",
        ignored_ingredients=[],
    )


@router.get("/matching", response_model=RecipeListResponse)
def matching_recipes(
    ingredients: str = Query(..., description="Comma-separated ingredients on hand"),
    exclude: Optional[str] = Query(None),
    no_onion: bool = False,
    no_garlic: bool = False,
    diet: Optional[str] = Query(None, description="Saved dietary preference hard constraint"),
    cuisine: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    restrictions = _expand_ingredient_terms(db, (exclude or "").split(","))
    safe_terms, rejected_terms = _safe_matching_terms(
        ingredients.split(","), restrictions, no_onion, no_garlic, diet,
    )
    if not safe_terms:
        return RecipeListResponse(
            items=[], total=0, offset=offset, limit=limit,
            status="BLOCKED_BY_DIETARY_RESTRICTION" if (no_onion or no_garlic or diet) else "BLOCKED_BY_ALLERGY",
            ignored_ingredients=rejected_terms,
        )
    expanded = _expand_ingredient_terms(db, safe_terms)
    predicates = _diet_predicates([diet]) if diet else []
    statement = db.query(Recipe).filter(*predicates)
    if cuisine:
        statement = statement.filter(func.lower(func.trim(Recipe.cuisine)) == cuisine.strip().lower())
    for predicate in _exclusion_predicates(restrictions, no_onion, no_garlic):
        statement = statement.filter(predicate)
    requested_predicate = _ingredient_predicate(expanded)
    statement = statement.join(
        RecipeIngredient, RecipeIngredient.recipe_id == Recipe.recipe_id,
    ).filter(requested_predicate).group_by(Recipe.recipe_id).order_by(
        func.count(RecipeIngredient.id).desc(),
        Recipe.total_minutes.asc().nullslast(),
        Recipe.recipe_name.asc(),
    )
    total = statement.order_by(None).count()
    recipes = statement.offset(offset).limit(limit).all()
    ingredient_map = _ingredient_map(db, [recipe.recipe_id for recipe in recipes])
    return RecipeListResponse(
        items=_to_items(recipes, ingredient_map, safe_terms),
        total=total,
        offset=offset,
        limit=limit,
        status="FOUND" if recipes else ("NO_DATABASE_MATCH" if not rejected_terms else "BLOCKED_BY_ALLERGY"),
        ignored_ingredients=rejected_terms,
    )


@router.get("/filter-options")
def recipe_filter_options(db: Session = Depends(get_db)):
    values = db.query(func.trim(Recipe.cuisine)).filter(
        Recipe.cuisine.isnot(None), func.trim(Recipe.cuisine) != ""
    ).distinct().order_by(func.trim(Recipe.cuisine)).all()
    return {"cuisines": [value for (value,) in values]}


@router.get("/{recipe_id}", response_model=RecipeItem)
def get_recipe(recipe_id: str, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.recipe_id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _to_items([recipe], _ingredient_map(db, [recipe.recipe_id]))[0]
