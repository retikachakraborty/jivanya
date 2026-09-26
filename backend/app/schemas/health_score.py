from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from app.schemas.product import ProductItem

class ProductRuleWarning(BaseModel):
    code: str
    label: str  # e.g. "High Added Sugar"
    severity: str  # "warning" | "danger"
    description: str

class CleanHighlight(BaseModel):
    code: str  # e.g. "HIGH_PROTEIN", "HIGH_FIBER", "WHOLE_GRAIN", "PALM_OIL_FREE", "LOW_SUGAR"
    label: str
    description: str

class ProfileWarning(BaseModel):
    type: str  # "allergy" | "exclusion" | "diet"
    message: str

class ScoreFactor(BaseModel):
    label: str
    points: int
    reason: str

class HealthySwap(BaseModel):
    product: ProductItem
    score: int
    grade: str  # "A" | "B" | "C" | "D" | "E"
    sugar_diff_pct: Optional[float] = None  # e.g. -65.5%
    sat_fat_diff_pct: Optional[float] = None
    protein_multiplier: Optional[float] = None  # e.g. 2.4x
    highlights: List[str]

class HealthScorecard(BaseModel):
    score: int  # 0 - 100
    grade: str  # "A" | "B" | "C" | "D" | "E"
    grade_label: str  # "Excellent" | "Good" | "Moderate" | "Poor" | "Ultra-Processed"
    summary: str
    rule_warnings: List[ProductRuleWarning]
    clean_highlights: List[CleanHighlight]
    profile_warnings: List[ProfileWarning]
    contains_palm_oil: bool
    contains_maida: bool
    healthy_swaps: List[HealthySwap]
    score_breakdown: List[ScoreFactor]
    grade_thresholds: Dict[str, str]

class ProductScoreResponse(BaseModel):
    product: ProductItem
    scorecard: HealthScorecard
