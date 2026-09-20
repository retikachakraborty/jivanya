from pydantic import BaseModel, ConfigDict
from typing import Optional

class ProductItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    barcode: int
    product_name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    countries: Optional[str] = None
    energy_100g: Optional[float] = None
    protein_100g: Optional[float] = None
    carbohydrates_100g: Optional[float] = None
    sugars_100g: Optional[float] = None
    fat_100g: Optional[float] = None
    saturated_fat_100g: Optional[float] = None
    fiber_100g: Optional[float] = None
    sodium_100g: Optional[float] = None
    ingredients_text: Optional[str] = None
    allergens: Optional[str] = None
    labels: Optional[str] = None
    image_url: Optional[str] = None
    last_updated: Optional[str] = None
    data_completeness: Optional[float] = None

class ProductListResponse(BaseModel):
    items: list[ProductItem]
    total: int
    offset: int
    limit: int

class ProductCompareRequest(BaseModel):
    barcodes: list[int]

class ProductCompareResponse(BaseModel):
    items: list[ProductItem]
