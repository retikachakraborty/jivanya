from sqlalchemy import Column, Integer, String, Float, Index
from app.core.database import Base

class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(String, unique=True, index=True, nullable=False)
    food_name = Column(String, index=True, nullable=False)
    food_group = Column(String, index=True)
    
    # Macronutrients per 100g
    energy_kcal = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbohydrate_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    
    # Micronutrients per 100g
    calcium_mg = Column(Float, default=0.0)
    iron_mg = Column(Float, default=0.0)
    sodium_mg = Column(Float, default=0.0)
    potassium_mg = Column(Float, default=0.0)
    vitamin_c_mg = Column(Float, default=0.0)
    folate_ug = Column(Float, default=0.0)


class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"

    id = Column(Integer, primary_key=True, index=True)
    canonical = Column(String, index=True, nullable=False)
    alias = Column(String, index=True, nullable=False)

    __table_args__ = (
        Index("idx_canonical_alias", "canonical", "alias"),
    )

