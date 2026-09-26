from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductItem
from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.schemas.tools import CompareProductsInput, SearchProductsInput
from app.jiv.tools.base import BaseTool

_SORT_FIELDS = {
    "energy": "energy_100g",
    "protein": "protein_100g",
    "sugar": "sugars_100g",
    "fat": "fat_100g",
    "saturated_fat": "saturated_fat_100g",
    "fiber": "fiber_100g",
    "sodium": "sodium_100g",
    "data_completeness": "data_completeness",
}


def _product_profile_warning(product: Product, profile: Optional[UserProfileSchema]) -> Optional[str]:
    if not profile:
        return None

    raw_text = f"{product.allergens or ''} {product.ingredients_text or ''}".lower()

    for allergy in profile.allergies:
        if allergy.strip() and allergy.strip().lower() in raw_text:
            return f"Contains potential allergen '{allergy}' from your saved profile."

    for exclusion in profile.exclusions:
        if exclusion.strip() and exclusion.strip().lower() in raw_text:
            return f"Contains excluded ingredient '{exclusion}' from your saved profile."

    if profile.no_onion and "onion" in raw_text:
        return "Contains onion, conflicting with your saved no-onion preference."
    if profile.no_garlic and "garlic" in raw_text:
        return "Contains garlic, conflicting with your saved no-garlic preference."

    return None


class SearchProductsTool(BaseTool):
    name = "search_products"
    description = (
        "Search Jivanya's 165-product Indian packaged foods catalog by category, brand, "
        "or keywords. Annotates products with profile-aware allergen warnings."
    )
    args_schema = SearchProductsInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        category = kwargs.get("category")
        query = kwargs.get("query")
        brand = kwargs.get("brand")
        sort = kwargs.get("sort")
        order = kwargs.get("order", "asc")
        limit = kwargs.get("limit", 5)
        offset = kwargs.get("offset", 0)

        statement = db.query(Product)
        if query:
            statement = statement.filter(Product.product_name.ilike(f"%{query.strip()}%"))
        if brand:
            statement = statement.filter(Product.brand.ilike(f"%{brand.strip()}%"))
        if category:
            statement = statement.filter(Product.category.ilike(f"%{category.strip()}%"))

        total = statement.order_by(None).count()

        field = _SORT_FIELDS.get(sort or "")
        if field:
            column = getattr(Product, field)
            statement = statement.order_by((column.desc() if order == "desc" else column.asc()).nullslast())
        else:
            statement = statement.order_by(Product.product_name.asc())

        products = statement.offset(offset).limit(limit).all()
        items = []
        for p in products:
            item_data = ProductItem.model_validate(p).model_dump()
            item_data["warning"] = _product_profile_warning(p, user_profile)
            items.append(item_data)

        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": items,
        }


class CompareProductsTool(BaseTool):
    name = "compare_products"
    description = (
        "Compare 2 to 4 packaged food products side-by-side using barcodes. "
        "Evaluates macro/micronutrients and checks profile constraints and warnings."
    )
    args_schema = CompareProductsInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        barcodes = list(dict.fromkeys(kwargs.get("product_ids", [])))
        if not 2 <= len(barcodes) <= 4:
            return {
                "error": "Comparison requires between 2 and 4 valid product barcodes.",
                "items": [],
            }

        products = db.query(Product).filter(Product.barcode.in_(barcodes)).all()
        by_barcode = {p.barcode: p for p in products}

        missing = [b for b in barcodes if b not in by_barcode]
        if missing:
            return {
                "error": f"Product barcodes not found in database: {missing}",
                "items": [],
            }

        items = []
        for b in barcodes:
            p = by_barcode[b]
            item_data = ProductItem.model_validate(p).model_dump()
            item_data["warning"] = _product_profile_warning(p, user_profile)
            items.append(item_data)

        return {
            "items": items,
            "count": len(items),
            "summary": f"Compared {len(items)} products from the verified catalog.",
        }
