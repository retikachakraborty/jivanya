from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.nutrition import router as nutrition_router
from app.api.vision import router as vision_router
from app.api.recipes import router as recipes_router
from app.api.products import router as products_router

# Import all database models before create_all so local SQLite/dev databases can expose existing tables.
from app.models import Product, Recipe, RecipeIngredient  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jivanya API",
    description="Jivanya food intelligence APIs for nutrition, recipes, products and vision.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(nutrition_router)
app.include_router(vision_router)
app.include_router(recipes_router)
app.include_router(products_router)

@app.get("/")
def root():
    return {"message": "Jivanya API is running", "status": "online", "engines": ["nutrition", "recipes", "products", "vision"]}
