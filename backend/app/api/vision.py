from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.nutrition import FoodItem, IngredientAlias
from app.schemas.nutrition import FoodItemResponse
from app.schemas.vision import VisionModelInfo, VisionNutritionMatch, VisionPredictionResponse
from app.services.vision_config import PROJECT_ROOT
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
        module=config.module,
        model_type=config.model_type,
        task=config.task,
        checkpoint=str(config.checkpoint.relative_to(PROJECT_ROOT)),
        available=vision_service.checkpoint_available(config),
        loaded=vision_service.is_loaded(config.name),
    ) for config in vision_service.configs()]


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


@router.post("/predict", response_model=VisionPredictionResponse)
async def predict_image(
    image: Annotated[UploadFile, File(description="Image to analyze")],
    model_name: Annotated[str, Form(description="Registered model name; defaults to vegetables")] = "vegetables",
    include_nutrition: Annotated[bool, Form(description="Attempt an exact IFCT database match")] = False,
    db: Session = Depends(get_db),
) -> VisionPredictionResponse:
    if not image.filename:
        raise HTTPException(status_code=422, detail="Image filename is missing")
    try:
        payload = await image.read()
        result = vision_service.predict(model_name, payload)
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
