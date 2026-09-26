from typing import Any, Optional

from sqlalchemy import and_, case, exists, func, or_
from sqlalchemy.orm import Session

from app.api.recipes import (
    _base_query,
    _expand_ingredient_terms,
    _ingredient_map,
    _safe_matching_terms,
    _diet_predicates,
    _exclusion_predicates,
    _ingredient_predicate,
    _to_items,
)
from app.models.recipe import Recipe, RecipeIngredient
from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.schemas.tools import MatchRecipesInput, SearchRecipesInput
from app.jiv.tools.base import BaseTool


INDIAN_INGREDIENT_SYNONYMS: dict[str, list[str]] = {
    "lentil": ["dal", "dhal", "daal", "lentil", "lentils", "masoor", "toor", "chana", "moong", "urad"],
    "lentils": ["dal", "dhal", "daal", "lentil", "lentils", "masoor", "toor", "chana", "moong", "urad"],
    "dal": ["dal", "dhal", "daal", "lentil", "lentils", "masoor", "toor", "chana", "moong", "urad"],
    "paneer": ["paneer", "cottage cheese"],
    "cottage cheese": ["paneer", "cottage cheese"],
    "curd": ["curd", "dahi", "yogurt"],
    "yogurt": ["curd", "dahi", "yogurt"],
    "dahi": ["curd", "dahi", "yogurt"],
    "capsicum": ["capsicum", "bell pepper", "shimla mirch"],
    "bell pepper": ["capsicum", "bell pepper", "shimla mirch"],
    "coriander": ["coriander", "cilantro", "dhania"],
    "cilantro": ["coriander", "cilantro", "dhania"],
    "brinjal": ["brinjal", "eggplant", "baingan", "aubergine"],
    "eggplant": ["brinjal", "eggplant", "baingan", "aubergine"],
    "spinach": ["spinach", "palak"],
    "palak": ["spinach", "palak"],
    "potato": ["potato", "potatoes", "aloo"],
    "potatoes": ["potato", "potatoes", "aloo"],
    "aloo": ["potato", "potatoes", "aloo"],
    "cauliflower": ["cauliflower", "gobi"],
    "gobi": ["cauliflower", "gobi"],
    "chickpea": ["chickpea", "chickpeas", "chana", "kabuli chana"],
    "chickpeas": ["chickpea", "chickpeas", "chana", "kabuli chana"],
    "chana": ["chickpea", "chickpeas", "chana", "kabuli chana"],
    "chicken": ["chicken", "murgh"],
    "murgh": ["chicken", "murgh"],
    "mutton": ["mutton", "lamb", "gosht"],
    "gosht": ["mutton", "lamb", "gosht"],
    "egg": ["egg", "eggs", "anda"],
    "eggs": ["egg", "eggs", "anda"],
}

HEALTHY_DIET_RANK = {
    "vegan": 5, "vegetarian": 4, "diabetic friendly": 3,
    "gluten free": 2, "high protein vegetarian": 2,
    "high protein non vegetarian": 1, "non vegeterian": 0, "eggetarian": 1,
}
HIGH_PROTEIN_DIET_RANK = {"high protein vegetarian": 2, "high protein non vegetarian": 2, "vegetarian": 1, "vegan": 1}


def _course_values(course: str | list[str] | None) -> list[str]:
    if course is None:
        return []
    return [course] if isinstance(course, str) else course


def _cuisine_values(cuisine: str | list[str] | None) -> list[str]:
    if cuisine is None:
        return []
    return [cuisine] if isinstance(cuisine, str) else cuisine


def _apply_cuisine(statement, cuisine: str | list[str] | None):
    values = [value.strip() for value in _cuisine_values(cuisine) if value and value.strip()]
    if values:
        statement = statement.filter(or_(*(func.lower(func.trim(Recipe.cuisine)) == value.lower() for value in values)))
    return statement


def _apply_course(statement, course: str | list[str] | None):
    values = [value.strip() for value in _course_values(course) if value and value.strip()]
    if values:
        statement = statement.filter(or_(*(Recipe.course.ilike(f"%{value}%") for value in values)))
    return statement


def _apply_health_ranking(statement, health_goal: str | None):
    if health_goal == "healthy":
        ranks = case(HEALTHY_DIET_RANK, value=func.lower(func.trim(func.coalesce(Recipe.diet, ""))), else_=0)
        return statement.order_by(ranks.desc(), Recipe.total_minutes.asc().nullslast(), Recipe.recipe_name.asc())
    if health_goal == "high_protein":
        ranks = case(HIGH_PROTEIN_DIET_RANK, value=func.lower(func.trim(func.coalesce(Recipe.diet, ""))), else_=0)
        return statement.order_by(ranks.desc(), Recipe.total_minutes.asc().nullslast(), Recipe.recipe_name.asc())
    return statement


def _expand_with_synonyms(db: Session, terms: list[str]) -> tuple[set[str], dict[str, set[str]]]:
    all_expanded: set[str] = set()
    term_families: dict[str, set[str]] = {}
    for term in terms:
        clean = term.lower().strip()
        syns = INDIAN_INGREDIENT_SYNONYMS.get(clean, [clean])
        exp = _expand_ingredient_terms(db, syns)
        exp.update(syns)
        term_families[term] = exp
        all_expanded.update(exp)
    return all_expanded, term_families


def _resolve_profile_filters(
    user_profile: Optional[UserProfileSchema],
    diet: Optional[str] = None,
    no_onion: Optional[bool] = None,
    no_garlic: Optional[bool] = None,
    exclude: Optional[list[str]] = None,
) -> tuple[Optional[str], bool, bool, list[str]]:
    resolved_no_onion = bool(no_onion or (user_profile and user_profile.no_onion))
    resolved_no_garlic = bool(no_garlic or (user_profile and user_profile.no_garlic))
    
    resolved_diet = diet
    if not resolved_diet and user_profile and user_profile.diet_preference:
        if user_profile.diet_preference != "no preference":
            resolved_diet = user_profile.diet_preference

    exclusions_set = set(exclude or [])
    if user_profile:
        for item in [*user_profile.allergies, *user_profile.exclusions]:
            if item.strip():
                exclusions_set.add(item.strip().lower())

    return resolved_diet, resolved_no_onion, resolved_no_garlic, sorted(exclusions_set)


class SearchRecipesTool(BaseTool):
    name = "search_recipes"
    description = (
        "Search Jivanya's 6,871-recipe library by dish name keyword, course, cuisine, "
        "diet, and cooking time. Automatically respects user restrictions and allergies."
    )
    args_schema = SearchRecipesInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        query = kwargs.get("query")
        cuisine = kwargs.get("cuisine")
        course = kwargs.get("course")
        diet = kwargs.get("diet")
        ingredients = kwargs.get("ingredients")
        max_time = kwargs.get("max_time")
        health_goal = kwargs.get("health_goal")
        no_onion = kwargs.get("no_onion")
        no_garlic = kwargs.get("no_garlic")
        exclude = kwargs.get("exclude")
        limit = kwargs.get("limit", 20)
        offset = kwargs.get("offset", 0)

        eff_diet, eff_no_onion, eff_no_garlic, eff_exclude = _resolve_profile_filters(
            user_profile, diet, no_onion, no_garlic, exclude
        )

        restrictions = _expand_ingredient_terms(db, eff_exclude)
        primary_ingredient = ingredients[0] if ingredients else None

        statement = _base_query(
            db=db,
            query=query,
            cuisine=None,
            course=None,
            diet=eff_diet,
            diet_filter=None,
            ingredient=primary_ingredient,
            exclude_ingredients=restrictions,
            no_onion=eff_no_onion,
            no_garlic=eff_no_garlic,
        )
        statement = _apply_cuisine(statement, cuisine)
        statement = _apply_course(statement, course)

        if ingredients and len(ingredients) > 1:
            for extra_ing in ingredients[1:]:
                all_extra, _ = _expand_with_synonyms(db, [extra_ing])
                pred = _ingredient_predicate(all_extra)
                if pred is not None:
                    statement = statement.filter(
                        exists().where(and_(
                            RecipeIngredient.recipe_id == Recipe.recipe_id,
                            pred,
                        )).correlate(Recipe)
                    )

        if max_time is not None:
            statement = statement.filter(Recipe.total_minutes <= max_time)

        total = statement.order_by(None).count()
        unrestricted_total = None
        if total == 0 and (eff_exclude or eff_no_onion or eff_no_garlic or eff_diet):
            unrestricted = _base_query(
                db=db, query=query, cuisine=None, course=None, diet=None,
                diet_filter=None, ingredient=primary_ingredient,
                exclude_ingredients=set(), no_onion=False, no_garlic=False,
            )
            unrestricted = _apply_cuisine(unrestricted, cuisine)
            unrestricted = _apply_course(unrestricted, course)
            unrestricted_total = unrestricted.order_by(None).count()
        ordered = _apply_health_ranking(statement, health_goal)
        if not health_goal:
            ordered = statement.order_by(Recipe.total_minutes.asc().nullslast(), Recipe.recipe_name.asc())
        recipes = ordered.offset(offset).limit(limit).all()

        ingredient_map = _ingredient_map(db, [r.recipe_id for r in recipes])
        items = _to_items(recipes, ingredient_map, ingredients)

        blocked = bool(unrestricted_total)
        status = "BLOCKED_BY_ALLERGY" if blocked and user_profile and any(
            _expand_ingredient_terms(db, user_profile.allergies) & restrictions
        ) else "BLOCKED_BY_DIETARY_RESTRICTION" if blocked else "NO_DATABASE_MATCH"
        if items:
            status = "FOUND"
        return {
            "status": status,
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [item.model_dump() for item in items],
            "applied_filters": {
                "diet": eff_diet,
                "no_onion": eff_no_onion,
                "no_garlic": eff_no_garlic,
                "excluded": eff_exclude,
                "max_time": max_time,
                "cuisine": _cuisine_values(cuisine),
                "course": _course_values(course),
                "health_goal": health_goal,
            },
        }


class MatchRecipesTool(BaseTool):
    name = "match_recipes"
    description = (
        "Find recipes that can be cooked using ingredients on hand or specified by the user "
        "(e.g., chicken and lentils, paneer and spinach). "
        "Sorts by highest number of matching distinct ingredients and respects profile restrictions."
    )
    args_schema = MatchRecipesInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        available = kwargs.get("available_ingredients", [])
        cuisine = kwargs.get("cuisine")
        course = kwargs.get("course")
        health_goal = kwargs.get("health_goal")
        max_time = kwargs.get("max_time")
        diet = kwargs.get("diet")
        no_onion = kwargs.get("no_onion")
        no_garlic = kwargs.get("no_garlic")
        exclude = kwargs.get("exclude")
        limit = kwargs.get("limit", 20)
        offset = kwargs.get("offset", 0)

        eff_diet, eff_no_onion, eff_no_garlic, eff_exclude = _resolve_profile_filters(
            user_profile, diet, no_onion, no_garlic, exclude
        )

        restrictions = _expand_ingredient_terms(db, eff_exclude)
        safe_terms, rejected_terms = _safe_matching_terms(
            available, restrictions, eff_no_onion, eff_no_garlic, eff_diet
        )

        if not safe_terms:
            # Course/cuisine recommendation requests are valid without an
            # ingredient list. MatchRecipes remains one coherent capability,
            # but an empty ingredient list must not mean "require an ingredient".
            if not available and (cuisine or course):
                statement = _base_query(
                    db=db, query=None, cuisine=cuisine, course=None, diet=eff_diet,
                    diet_filter=None, ingredient=None, exclude_ingredients=restrictions,
                    no_onion=eff_no_onion, no_garlic=eff_no_garlic,
                )
                statement = _apply_course(statement, course)
                if max_time is not None:
                    statement = statement.filter(Recipe.total_minutes <= max_time)
                total = statement.order_by(None).count()
                ordered = _apply_health_ranking(statement, health_goal)
                if not health_goal:
                    ordered = statement.order_by(Recipe.total_minutes.asc().nullslast(), Recipe.recipe_name.asc())
                recipes = ordered.offset(offset).limit(limit).all()
                ingredient_map = _ingredient_map(db, [r.recipe_id for r in recipes])
                items = _to_items(recipes, ingredient_map)
                return {
                    "status": "FOUND" if items else "NO_DATABASE_MATCH",
                    "total": total,
                    "offset": offset,
                    "limit": limit,
                    "items": [item.model_dump() for item in items],
                    "ignored_ingredients": [],
                    "applied_filters": {
                        "diet": eff_diet, "no_onion": eff_no_onion, "no_garlic": eff_no_garlic,
                        "excluded": eff_exclude, "max_time": max_time, "cuisine": cuisine,
                        "course": _course_values(course), "health_goal": health_goal,
                    },
                }
            return {
                "status": "BLOCKED_BY_ALLERGY" if user_profile and rejected_terms else "BLOCKED_BY_DIETARY_RESTRICTION",
                "total": 0,
                "offset": offset,
                "limit": limit,
                "items": [],
                "ignored_ingredients": rejected_terms,
                "applied_filters": {
                    "diet": eff_diet,
                    "no_onion": eff_no_onion,
                    "no_garlic": eff_no_garlic,
                    "excluded": eff_exclude,
                },
            }

        all_expanded, term_families = _expand_with_synonyms(db, safe_terms)
        predicates = _diet_predicates([eff_diet]) if eff_diet else []
        statement = db.query(Recipe).filter(*predicates)

        statement = _apply_cuisine(statement, cuisine)
        statement = _apply_course(statement, course)
        if max_time is not None:
            statement = statement.filter(Recipe.total_minutes <= max_time)

        for predicate in _exclusion_predicates(restrictions, eff_no_onion, eff_no_garlic):
            statement = statement.filter(predicate)

        cases = []
        term_predicates = []
        for term, family in term_families.items():
            t_pred = _ingredient_predicate(family)
            if t_pred is not None:
                term_predicates.append(t_pred)
                cases.append(func.max(case((t_pred, 1), else_=0)))

        if not term_predicates:
            return {
                "status": "NO_DATABASE_MATCH",
                "total": 0,
                "offset": offset,
                "limit": limit,
                "items": [],
                "ignored_ingredients": rejected_terms,
                "applied_filters": {
                    "diet": eff_diet,
                    "no_onion": eff_no_onion,
                    "no_garlic": eff_no_garlic,
                    "excluded": eff_exclude,
                },
            }

        distinct_score = sum(cases) if cases else func.count(RecipeIngredient.id)
        statement = (
            statement.join(RecipeIngredient, RecipeIngredient.recipe_id == Recipe.recipe_id)
            .filter(or_(*term_predicates))
            .group_by(Recipe.recipe_id)
            .order_by(
                distinct_score.desc(),
                func.count(RecipeIngredient.id).desc(),
                Recipe.total_minutes.asc().nullslast(),
                Recipe.recipe_name.asc(),
            )
        )
        if health_goal:
            # Preserve hard ingredient matching while making the preference only
            # a deterministic ordering signal based on the stored diet tag.
            ranks = case(
                HEALTHY_DIET_RANK if health_goal == "healthy" else HIGH_PROTEIN_DIET_RANK,
                value=func.lower(func.trim(func.coalesce(Recipe.diet, ""))), else_=0,
            )
            statement = statement.order_by(ranks.desc(), distinct_score.desc(), func.count(RecipeIngredient.id).desc(), Recipe.total_minutes.asc().nullslast(), Recipe.recipe_name.asc())

        total = statement.order_by(None).count()
        recipes = statement.offset(offset).limit(limit).all()
        ingredient_map = _ingredient_map(db, [r.recipe_id for r in recipes])
        items = _to_items(recipes, ingredient_map, list(all_expanded))

        status = "FOUND" if items else ("BLOCKED_BY_ALLERGY" if rejected_terms and user_profile and user_profile.allergies else "NO_DATABASE_MATCH")
        return {
            "status": status,
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [item.model_dump() for item in items],
            "ignored_ingredients": rejected_terms,
            "applied_filters": {
                "diet": eff_diet,
                "no_onion": eff_no_onion,
                "no_garlic": eff_no_garlic,
                "excluded": eff_exclude,
                "max_time": max_time,
                "cuisine": cuisine,
                "course": _course_values(course),
                "health_goal": health_goal,
            },
        }
