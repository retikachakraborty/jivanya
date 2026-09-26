import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.nutrition import router as nutrition_router
from app.api.vision import router as vision_router
from app.api.recipes import router as recipes_router
from app.api.products import router as products_router
from app.api.meal_plan import router as meal_plan_router
from app.api.speech import router as speech_router
from app.jiv import jiv_router

# Import all database models before create_all so local SQLite/dev databases can expose existing tables.
from app.models import Product, Recipe, RecipeIngredient  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jivanya API",
    description="Jivanya food intelligence APIs for nutrition, recipes, products, vision, meal plan and Jiv agent.",
    version="1.2.0",
)

cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

configured_origins = os.getenv("CORS_ORIGINS", "")
if configured_origins:
    cors_origins.extend(
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(nutrition_router)
app.include_router(vision_router)
app.include_router(recipes_router)
app.include_router(products_router)
app.include_router(meal_plan_router)
app.include_router(speech_router)
app.include_router(jiv_router)

@app.get("/")
def root():
    return {"message": "Jivanya API is running", "status": "online", "engines": ["nutrition", "recipes", "products", "vision", "jiv"]}
