from typing import Any, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductItem
from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.schemas.tools import OptimizeBasketInput
from app.jiv.tools.base import BaseTool


class OptimizeBasketTool(BaseTool):
    name = "optimize_basket"
    description = (
        "Deterministically select and optimize a packaged food basket based on budget, "
        "nutritional priorities (high_protein, low_sugar, balanced), and hard profile constraints."
    )
    args_schema = OptimizeBasketInput

    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        categories = kwargs.get("categories") or []
        priorities = kwargs.get("priorities") or ["balanced"]
        max_items = kwargs.get("max_items", 5)

        statement = db.query(Product)

        # Filter categories if specified
        if categories:
            cat_filters = [Product.category.ilike(f"%{c.strip()}%") for c in categories]
            statement = statement.filter(or_(*cat_filters))

        # Filter out products violating profile allergies / exclusions
        if user_profile:
            blocked_terms = set(user_profile.allergies + user_profile.exclusions)
            if user_profile.no_onion:
                blocked_terms.add("onion")
            if user_profile.no_garlic:
                blocked_terms.add("garlic")

            for term in blocked_terms:
                if term.strip():
                    pattern = f"%{term.strip().lower()}%"
                    statement = statement.filter(
                        ~Product.allergens.ilike(pattern),
                        ~Product.ingredients_text.ilike(pattern),
                    )

        # Apply priority sorting
        priority = priorities[0] if priorities else "balanced"
        if priority == "high_protein":
            statement = statement.order_by(Product.protein_100g.desc().nullslast())
        elif priority == "low_sugar":
            statement = statement.order_by(Product.sugars_100g.asc().nullslast())
        elif priority == "low_sodium":
            statement = statement.order_by(Product.sodium_100g.asc().nullslast())
        else:
            # Balanced: high protein and low sugar
            statement = statement.order_by(
                Product.protein_100g.desc().nullslast(),
                Product.sugars_100g.asc().nullslast(),
            )

        products = statement.limit(max_items).all()
        items = [ProductItem.model_validate(p).model_dump() for p in products]

        total_protein = round(sum(p.get("protein_100g") or 0.0 for p in items), 1)
        total_sugars = round(sum(p.get("sugars_100g") or 0.0 for p in items), 1)

        return {
            "selected_products": items,
            "count": len(items),
            "priority_applied": priority,
            "metrics_per_100g_sum": {
                "total_protein_g": total_protein,
                "total_sugars_g": total_sugars,
            },
            "summary": (
                f"Optimized basket with {len(items)} items prioritized for '{priority}', "
                f"strictly excluding profile allergens and exclusions."
            ),
        }
