import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AVARIS Environmental Monitor"
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./database/environment_monitor.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MISTRAL_MODEL_PATH: str = os.getenv("MISTRAL_MODEL_PATH", "./models/mistral_4b")
    CAMERA_STREAM_URL: str = os.getenv("CAMERA_STREAM_URL", "http://ESP32CAM_IP/stream")
    ESP32_CAM_IP: str = os.getenv("ESP32_CAM_IP", "192.168.1.100")
    FRONTEND_URL: str = "http://localhost:5173" # Default Vite port

    class Config:
        case_sensitive = True

settings = Settings()
