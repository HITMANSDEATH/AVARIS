from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Setup database path from environment variable or use default
DATABASE_PATH = os.getenv("DATABASE_PATH", "./database/environment_monitor.db")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    dust = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    risk_level = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False) # normal or anomaly
    description = Column(String, nullable=True) # AI Explanation
    recommended_action = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class CameraEvent(Base):
    __tablename__ = "camera_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False) # e.g., smoke_detected, motion
    frame_path = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False) # INFO, WARNING, ERROR
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class FoodAnalysisLog(Base):
    __tablename__ = "food_analysis_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_path = Column(String, nullable=False)
    food_item = Column(String, nullable=True)
    ingredients = Column(String, nullable=True) # JSON string
    detected_allergens = Column(String, nullable=True) # JSON string
    risk_level = Column(String, nullable=True)
    ai_explanation = Column(String, nullable=True)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
