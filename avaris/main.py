# Python 3.13 compatibility fix for cgi module
import sys
if sys.version_info >= (3, 13):
    try:
        import cgi
    except ImportError:
        # Create a minimal cgi module stub for Python 3.13 compatibility
        import types
        import html
        import email.message
        
        cgi = types.ModuleType('cgi')
        # Provide the most commonly used cgi functions
        cgi.escape = html.escape  # html.escape is the modern replacement
        cgi.parse_qs = lambda qs, keep_blank_values=False, strict_parsing=False: {}
        cgi.parse_qsl = lambda qs, keep_blank_values=False, strict_parsing=False: []
        
        # Add parse_header function that httpx needs
        def parse_header(line):
            """Parse a Content-type like header."""
            parts = line.split(';')
            main_type = parts[0].strip()
            pdict = {}
            for p in parts[1:]:
                if '=' in p:
                    name, value = p.split('=', 1)
                    name = name.strip().lower()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    pdict[name] = value
            return main_type, pdict
        
        cgi.parse_header = parse_header
        
        # Add to sys.modules so other imports can find it
        sys.modules['cgi'] = cgi

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
    
    # Start ESP32 sensor polling service
    logger.info("Starting ESP32 sensor polling service...")
    try:
        from backend.services.sensor_poller import start_sensor_polling
        await start_sensor_polling()
        logger.info("ESP32 sensor polling service started successfully")
    except Exception as e:
        logger.error(f"Failed to start sensor polling service: {e}")
    
    logger.info("AVARIS Backend startup complete")
    yield
    
    # Shutdown logic
    logger.info("Shutting down AVARIS Backend...")
    try:
        from backend.services.sensor_poller import stop_sensor_polling
        await stop_sensor_polling()
        logger.info("Sensor polling service stopped")
    except Exception as e:
        logger.error(f"Error stopping sensor polling service: {e}")

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
