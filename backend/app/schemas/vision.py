from pydantic import BaseModel, Field

from app.schemas.nutrition import FoodItemResponse


class VisionPrediction(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    bbox: list[float] | None = None
    segmentation: list[list[float]] | None = None


class VisionNutritionMatch(BaseModel):
    label: str
    canonical_name: str | None = None
    matched_food: FoodItemResponse | None = None


class VisionPredictionResponse(BaseModel):
    model: str
    module: str
    model_type: str
    status: str
    predictions: list[VisionPrediction] = Field(default_factory=list)
    image_width: int | None = None
    image_height: int | None = None
    processing_ms: float | None = None
    nutrition_matches: list[VisionNutritionMatch] | None = None
    error: str | None = None


class VisionModelInfo(BaseModel):
    name: str
    module: str
    model_type: str
    task: str | None = None
    checkpoint: str
    available: bool
    loaded: bool
