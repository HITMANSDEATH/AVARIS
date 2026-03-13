from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
import logging

from backend.api.routes import router as api_router
from backend.database.init_db import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database and AI modules
    logger.info("Initializing Database...")
    init_db()
    
    # Initialize Gemini Vision analyzer
    logger.info("Initializing Gemini Vision analyzer...")
    try:
        from backend.ai_engine.gemini_vision import get_vision_analyzer
        vision_analyzer = get_vision_analyzer()
        if vision_analyzer.is_available():
            logger.info("Gemini Vision analyzer initialized successfully")
        else:
            logger.warning("Gemini Vision analyzer not available - check API key")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Vision analyzer: {e}")
    
    # Initialize Gemini text analyzer
    logger.info("Initializing Gemini text analyzer...")
    try:
        from backend.ai_engine.text_analyzer import get_text_analyzer
        text_analyzer = get_text_analyzer()
        if text_analyzer.is_available():
            logger.info("Gemini text analyzer initialized successfully")
        else:
            logger.warning("Gemini text analyzer not available - using fallback explanations")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini text analyzer: {e}")
    
    # Initialize allergen checker
    logger.info("Initializing allergen checker...")
    try:
        from ml.allergen_checker import get_allergen_checker
        get_allergen_checker()
        logger.info("Allergen checker initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize allergen checker: {e}")
    
    logger.info("AVARIS Backend startup complete")
    yield
    
    # Shutdown logic
    logger.info("Shutting down AVARIS Backend...")

app = FastAPI(title="AVARIS Environmental Monitor API", lifespan=lifespan)

# Allow React frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "Welcome to AVARIS Environment Monitoring System API"}

if __name__ == "__main__":
    print("Starting AVARIS Backend Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
