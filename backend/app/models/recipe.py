from sqlalchemy import Boolean, Column, Integer, String, Text
from app.core.database import Base

class Recipe(Base):
    __tablename__ = "recipes"
    recipe_id = Column(String, primary_key=True)
    recipe_name = Column(String, nullable=False, index=True)
    ingredients_raw = Column(Text)
    instructions = Column(Text)
    cuisine = Column(String, index=True)
    course = Column(String)
    diet = Column(String, index=True)
    prep_minutes = Column(Integer)
    cook_minutes = Column(Integer)
    total_minutes = Column(Integer)
    servings = Column(Integer)
    source_url = Column(String)
    missing_ingredients = Column(Boolean)
    long_prep_time = Column(Boolean)
    large_serving = Column(Boolean)

class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    id = Column(Integer, primary_key=True)
    recipe_id = Column(String, nullable=False, index=True)
    ingredient_raw = Column(String, nullable=False)
    ingredient = Column(String, nullable=False, index=True)
