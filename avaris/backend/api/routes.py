from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import os

from backend.database.models import get_db, SensorData, RiskPrediction, AnomalyEvent, FoodAnalysisLog
from backend.ai_engine.reasoning import explain_anomaly, explain_risk, explain_food_risk
from backend.vision.ingredient_detector import detect_ingredients
from backend.allergen.allergen_matcher import match_allergens, evaluate_risk, save_to_known_foods, get_ingredients_from_cache
from fastapi import File, UploadFile
import json
import time

router = APIRouter()

# Load Models
RISK_MODEL_PATH = "backend/ml_models/risk_model.pkl"
ANOMALY_MODEL_PATH = "backend/ml_models/anomaly_model.pkl"
FORECAST_MODEL_PATH = "backend/ml_models/forecast_model.pkl"

def load_model(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None

risk_model = load_model(RISK_MODEL_PATH)
anomaly_model = load_model(ANOMALY_MODEL_PATH)
forecast_model = load_model(FORECAST_MODEL_PATH)

from pydantic import BaseModel

class SensorPayload(BaseModel):
    temperature: float
    humidity: float
    dust: float
    timestamp: str = None

@router.post("/sensor-data")
def receive_sensor_data(payload: SensorPayload, db: Session = Depends(get_db)):
    """Receive data from ESP32, predict risk/anomaly, and store."""
    
    try:
        # Storage
        db_sensor = SensorData(
            temperature=payload.temperature,
            humidity=payload.humidity,
            dust=payload.dust
        )
        if payload.timestamp:
            try:
                db_sensor.timestamp = datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
            except ValueError:
                pass # fallback to default now()
        
        db.add(db_sensor)
        db.commit()
        db.refresh(db_sensor)

        # ML Inference preparation
        features = pd.DataFrame([{
            "temperature": payload.temperature,
            "humidity": payload.humidity,
            "dust": payload.dust
        }])

        # 1. Anomaly Detection
        is_anomaly = False
        if anomaly_model:
            pred_anomaly = anomaly_model.predict(features)[0]
            # Isolation Forest: -1 is anomaly, 1 is normal
            is_anomaly = bool(pred_anomaly == -1)
            
            if is_anomaly:
                # Generate AI Explanation
                explanation = explain_anomaly(payload.temperature, payload.humidity, payload.dust)
                
                db_anomaly = AnomalyEvent(
                    status="anomaly",
                    description=f"Automated Alert: Anomaly Detected.\n{explanation}",
                    recommended_action="Inspect area immediately."
                )
                db.add(db_anomaly)
                db.commit()

        # 2. Risk Prediction
        current_risk = "UNKNOWN"
        if risk_model:
            pred_risk = risk_model.predict(features)[0]
            current_risk = str(pred_risk) # Ensure it's a standard string
            
            # Save Risk Prediction
            db_risk = RiskPrediction(
                risk_level=current_risk,
                confidence=0.95 # Mock confidence
            )
            db.add(db_risk)
            db.commit()
            
            # Explain Critical/High Risk
            if current_risk in ["HIGH", "CRITICAL"]:
                risk_explanation = explain_risk(current_risk, payload.temperature, payload.humidity, payload.dust)
                
                db_anomaly_risk = AnomalyEvent(
                    status=current_risk,
                    description=f"Risk Alert: {current_risk}.\n{risk_explanation}",
                    recommended_action="Follow safety protocols."
                )
                db.add(db_anomaly_risk)
                db.commit()

        return {"status": "success", "risk_level": current_risk, "anomaly_detected": is_anomaly}
    except Exception as e:
        import traceback
        print(f"Error in receive_sensor_data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest-sensor-data")
def get_latest_sensor_data(db: Session = Depends(get_db)):
    """Fetch the most recent sensor reading."""
    data = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
    if not data:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return {
        "temperature": data.temperature,
        "humidity": data.humidity,
        "dust": data.dust,
        "timestamp": data.timestamp.isoformat()
    }

@router.get("/risk-prediction")
def get_latest_risk(db: Session = Depends(get_db)):
    """Fetch the most recent risk prediction."""
    data = db.query(RiskPrediction).order_by(RiskPrediction.timestamp.desc()).first()
    if not data:
        return {"risk_level": "LOW", "confidence": 1.0, "timestamp": datetime.utcnow().isoformat()}
    return {
        "risk_level": data.risk_level,
        "confidence": data.confidence,
        "timestamp": data.timestamp.isoformat()
    }

@router.get("/anomaly-events")
def get_anomaly_events(db: Session = Depends(get_db), limit: int = 10):
    """Fetch recent anomaly events and AI explanations."""
    events = db.query(AnomalyEvent).order_by(AnomalyEvent.timestamp.desc()).limit(limit).all()
    return [{"status": e.status, "description": e.description, "action": e.recommended_action, "timestamp": e.timestamp.isoformat()} for e in events]

@router.get("/forecast")
def get_forecast(db: Session = Depends(get_db)):
    """Predict conditions 30 mins from now."""
    if not forecast_model:
        return {"error": "Forecast model not available"}
        
    latest = db.query(SensorData).order_by(SensorData.timestamp.desc()).first()
    if not latest:
        return {"error": "No data available for forecasting"}

    features = pd.DataFrame([{
        "temperature": latest.temperature,
        "humidity": latest.humidity,
        "dust": latest.dust
    }])
    
    prediction = forecast_model.predict(features)[0]
    
    return {
        "predicted_temperature": float(prediction[0]),
        "predicted_humidity": float(prediction[1]),
        "predicted_dust": float(prediction[2]),
        "forecast_time_mins": 30
    }

@router.post("/upload-food-image")
async def upload_food_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload food image, analyze for allergens, and store result."""
    try:
        # 1. Save Image
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"food_{timestamp}.jpg"
        upload_dir = "uploads/food_images"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
            
        # 2. Analyze Image
        # First, try to see if it's a known food (though Gemini is better for visual)
        # For now, always use Gemini for best accuracy as requested.
        analysis = detect_ingredients(file_path)
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
            
        food_item = analysis.get("food_item", "Unknown")
        ingredients = analysis.get("ingredients", [])
        
        # 3. Match Allergens
        allergen_db_path = "database/allergen_db.json"
        known_foods_path = "database/known_foods.json"
        
        detected_allergens = match_allergens(ingredients, allergen_db_path)
        risk_level = evaluate_risk(detected_allergens)
        
        # 4. Generate AI Explanation
        ai_explanation = explain_food_risk(food_item, ingredients, detected_allergens, risk_level)
        
        # 5. Log to Database
        db_log = FoodAnalysisLog(
            image_path=file_path,
            food_item=food_item,
            ingredients=json.dumps(ingredients),
            detected_allergens=json.dumps(detected_allergens),
            risk_level=risk_level,
            ai_explanation=ai_explanation
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        # 6. Save to Known Foods for future reference
        save_to_known_foods(food_item, ingredients, known_foods_path)
        
        return {
            "food_item": food_item,
            "ingredients": ingredients,
            "detected_allergens": detected_allergens,
            "risk_level": risk_level,
            "ai_explanation": ai_explanation,
            "image_url": f"/uploads/food_images/{filename}"
        }
    except Exception as e:
        print(f"Error in upload_food_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest-food-analysis")
def get_latest_food_analysis(db: Session = Depends(get_db)):
    """Fetch the most recent food analysis log."""
    log = db.query(FoodAnalysisLog).order_by(FoodAnalysisLog.timestamp.desc()).first()
    if not log:
        return None
    return {
        "id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "image_path": log.image_path,
        "food_item": log.food_item,
        "ingredients": json.loads(log.ingredients),
        "detected_allergens": json.loads(log.detected_allergens),
        "risk_level": log.risk_level,
        "ai_explanation": log.ai_explanation
    }
