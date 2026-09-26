from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.nutrition import FoodItem, IngredientAlias
from app.models.recipe import RecipeIngredient
from app.schemas.nutrition import FoodItemResponse
from app.schemas.vision import VisionModelInfo, VisionNutritionMatch, VisionPredictionResponse
from app.services.vision_config import PROJECT_ROOT, vision_display_name
from app.services.vision_service import (
    InvalidVisionImage,
    UnsupportedVisionModel,
    VisionInferenceError,
    VisionModelLoadError,
    vision_service,
)

router = APIRouter(prefix="/api/v1/vision", tags=["Vision Engine"])


@router.get("/models", response_model=list[VisionModelInfo])
def list_vision_models() -> list[VisionModelInfo]:
    return [VisionModelInfo(
        name=config.name,
        display_name=vision_display_name(config.name),
        module=config.module,
        model_type=config.model_type,
        task=config.task,
        checkpoint=str(config.checkpoint.relative_to(PROJECT_ROOT)),
        available=vision_service.checkpoint_available(config),
        loaded=vision_service.is_loaded(config.name),
    ) for config in vision_service.configs()]


@router.get("/supported-foods", response_model=list[str])
def list_supported_foods(model_name: str | None = None) -> list[str]:
    """Return user-facing classes from metadata shipped with available local models."""
    return vision_service.supported_classes_for_model(model_name) if model_name else vision_service.supported_classes()


def _nutrition_matches(labels: list[str], db: Session) -> list[VisionNutritionMatch]:
    matches: list[VisionNutritionMatch] = []
    for label in labels:
        raw = label.strip().lower()
        alias = db.query(IngredientAlias).filter(IngredientAlias.alias == raw).first()
        canonical = alias.canonical if alias else raw
        food = db.query(FoodItem).filter(FoodItem.food_name.ilike(f"%{canonical}%")).first()
        if not food and canonical != raw:
            food = db.query(FoodItem).filter(FoodItem.food_name.ilike(f"%{raw}%")).first()
        matches.append(VisionNutritionMatch(
            label=label,
            canonical_name=canonical if food else None,
            matched_food=FoodItemResponse.model_validate(food) if food else None,
        ))
    return matches


def _normalize_label(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


def _resolve_recipe_ingredient(label: str, db: Session) -> str | None:
    """Resolve a model class only when Jivanya can use it as an ingredient."""
    raw = _normalize_label(label)
    if not raw:
        return None

    # Most model classes already use the recipe ingredient vocabulary.  Check
    # that path first so ordinary detections do not load the entire alias table.
    raw_recipe_ingredient = db.query(RecipeIngredient).filter(
        or_(
            func.lower(func.trim(RecipeIngredient.ingredient)) == raw,
            func.lower(func.trim(RecipeIngredient.ingredient_raw)) == raw,
        )
    ).first()
    if raw_recipe_ingredient:
        return raw

    canonical_candidates = [raw]
    aliases = db.query(IngredientAlias).filter(
        func.lower(IngredientAlias.alias).like(f"%{raw}%")
    ).all()
    for row in aliases:
        for alias in (part.strip() for part in row.alias.split(",")):
            if _normalize_label(alias) == raw:
                canonical_candidates.extend(
                    _normalize_label(part) for part in row.canonical.split(",") if _normalize_label(part)
                )

    # Recipe matching is the source of truth for vision handoff.  Prefer the
    # model label itself when it is already a recipe ingredient; this avoids
    # turning a class such as ``carrot`` into an IFCT variant like
    # ``carrot, orange`` that would become two recipe query terms.
    for canonical in dict.fromkeys(canonical_candidates):
        recipe_ingredient = db.query(RecipeIngredient).filter(
            or_(
                func.lower(func.trim(RecipeIngredient.ingredient)) == canonical,
                func.lower(func.trim(RecipeIngredient.ingredient_raw)) == canonical,
            )
        ).first()
        if recipe_ingredient:
            return canonical

    for canonical in dict.fromkeys(canonical_candidates):
        food = db.query(FoodItem).filter(
            func.lower(func.trim(FoodItem.food_name)) == canonical
        ).first()
        if food:
            return canonical
    return None


@router.post("/predict", response_model=VisionPredictionResponse)
async def predict_image(
    image: Annotated[UploadFile, File(description="Image to analyze")],
    model_name: Annotated[str, Form(description="Internal model name; auto routes across available local models")] = "auto",
    include_nutrition: Annotated[bool, Form(description="Attempt an exact IFCT database match")] = False,
    db: Session = Depends(get_db),
) -> VisionPredictionResponse:
    if not image.filename:
        raise HTTPException(status_code=422, detail="Image filename is missing")
    try:
        payload = await image.read()
        if model_name.strip().lower() == "auto":
            result = vision_service.predict_auto(
                payload, resolve_ingredient=lambda label: _resolve_recipe_ingredient(label, db)
            )
        else:
            result = vision_service.predict(model_name, payload)
            result = vision_service.validate_selected_predictions(
                model_name, result, lambda label: _resolve_recipe_ingredient(label, db)
            )
    except UnsupportedVisionModel as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidVisionImage as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except VisionModelLoadError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except VisionInferenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if include_nutrition:
        result["nutrition_matches"] = _nutrition_matches(
            [prediction["label"] for prediction in result["predictions"]], db
        )
    return VisionPredictionResponse.model_validate(result)
