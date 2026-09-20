from sqlalchemy import BigInteger, Column, Float, String, Text
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    barcode = Column(BigInteger, primary_key=True)
    product_name = Column(String, nullable=False, index=True)
    brand = Column(String, index=True)
    category = Column(String, index=True)
    countries = Column(String)
    energy_100g = Column(Float)
    protein_100g = Column(Float)
    carbohydrates_100g = Column(Float)
    sugars_100g = Column(Float)
    fat_100g = Column(Float)
    saturated_fat_100g = Column(Float)
    fiber_100g = Column(Float)
    sodium_100g = Column(Float)
    ingredients_text = Column(Text)
    allergens = Column(Text)
    labels = Column(Text)
    image_url = Column(String)
    last_updated = Column(String)
    data_completeness = Column(Float)
