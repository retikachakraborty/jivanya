from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.nutrition import router as nutrition_router
from app.api.vision import router as vision_router

# Ensure tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jivanya API",
    description="Nutrition Engine API powered by ICMR-NIN IFCT 2017 analyzed data.",
    version="1.0.0"
)

app.include_router(nutrition_router)
app.include_router(vision_router)

@app.get("/")
def root():
    return {
        "message": "Jivanya Nutrition Engine API is running",
        "status": "online",
        "dataset": "ICMR-NIN IFCT 2017"
    }
