from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import os

from backend.database.models import get_db, SensorData, RiskPrediction, FoodAnalysisLog
from backend.ai_engine.reasoning import explain_risk, explain_food_risk
from backend.vision.ingredient_detector import detect_ingredients
from ml.allergen_checker import check_ingredients_for_allergens
from backend.camera.esp32_cam import capture_from_esp32, get_esp32_camera
from fastapi import File, UploadFile
import json
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Load Models
RISK_MODEL_PATH = "backend/ml_models/risk_model.pkl"
FORECAST_MODEL_PATH = "backend/ml_models/forecast_model.pkl"

def load_model(path):
    if os.path.exists(path):
        return joblib.load(path)
    return None

risk_model = load_model(RISK_MODEL_PATH)
forecast_model = load_model(FORECAST_MODEL_PATH)

def calculate_rule_based_risk(temperature: float, humidity: float, dust: float) -> tuple[str, float]:
    """
    Calculate risk level using rule-based logic when ML model is not available.
    Returns (risk_level, confidence)
    """
    risk_factors = []
    risk_score = 0
    
    # Temperature risk assessment
    if temperature > 35:
        risk_factors.append("Extreme high temperature")
        risk_score += 3
    elif temperature > 30:
        risk_factors.append("High temperature")
        risk_score += 2
    elif temperature < 10:
        risk_factors.append("Extreme low temperature")
        risk_score += 3
    elif temperature < 15:
        risk_factors.append("Low temperature")
        risk_score += 1
    
    # Humidity risk assessment
    if humidity > 80:
        risk_factors.append("Very high humidity")
        risk_score += 2
    elif humidity > 70:
        risk_factors.append("High humidity")
        risk_score += 1
    elif humidity < 20:
        risk_factors.append("Very low humidity")
        risk_score += 2
    elif humidity < 30:
        risk_factors.append("Low humidity")
        risk_score += 1
    
    # Dust level risk assessment (more sensitive)
    if dust > 120:
        risk_factors.append("Dangerous dust levels")
        risk_score += 4
    elif dust > 100:
        risk_factors.append("Very high dust levels")
        risk_score += 3
    elif dust > 75:
        risk_factors.append("High dust levels")
        risk_score += 2
    elif dust > 50:
        risk_factors.append("Elevated dust levels")
        risk_score += 1
    
    # Determine overall risk level (adjusted thresholds)
    if risk_score >= 7:
        risk_level = "CRITICAL"
        confidence = 0.9
    elif risk_score >= 5:
        risk_level = "HIGH"
        confidence = 0.85
    elif risk_score >= 2:
        risk_level = "MEDIUM"
        confidence = 0.8
    else:
        risk_level = "LOW"
        confidence = 0.75
    
    logger.info(f"Rule-based risk assessment: {risk_level} (score: {risk_score}, factors: {risk_factors})")
    return risk_level, confidence

from pydantic import BaseModel

class SensorPayload(BaseModel):
    temperature: float
    humidity: float
    dust: float
    timestamp: str = None

@router.post("/sensor-data")
def receive_sensor_data(payload: SensorPayload, db: Session = Depends(get_db)):
    """Receive data from ESP32, predict risk, and store."""
    
    try:
        logger.info(f"Received sensor data: T={payload.temperature}°C, H={payload.humidity}%, D={payload.dust}µg/m³")
        
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

        # Risk Prediction - Use hybrid approach (rule-based primary, ML secondary)
        current_risk = "UNKNOWN"
        confidence = 0.0
        
        # Always calculate rule-based risk first (more predictable)
        rule_risk, rule_confidence = calculate_rule_based_risk(payload.temperature, payload.humidity, payload.dust)
        
        if risk_model:
            try:
                # Get ML prediction as secondary validation
                pred_risk = risk_model.predict(features)[0]
                ml_risk = str(pred_risk)
                
                # Use rule-based as primary, but boost confidence if ML agrees
                current_risk = rule_risk
                if ml_risk == rule_risk:
                    confidence = min(0.95, rule_confidence + 0.1)  # Boost confidence when both agree
                    logger.info(f"ML and rule-based agree: {current_risk}")
                else:
                    confidence = rule_confidence
                    logger.info(f"ML ({ml_risk}) vs Rule-based ({rule_risk}) - using rule-based")
                    
            except Exception as e:
                logger.warning(f"ML risk model failed: {e}, using rule-based assessment")
                current_risk = rule_risk
                confidence = rule_confidence
        else:
            # Use rule-based risk assessment when ML model is not available
            current_risk = rule_risk
            confidence = rule_confidence
            logger.info(f"Using rule-based risk assessment: {current_risk}")
        
        # Save Risk Prediction
        db_risk = RiskPrediction(
            risk_level=current_risk,
            confidence=confidence
        )
        db.add(db_risk)
        db.commit()

        logger.info(f"Sensor data processed: Risk={current_risk}")
        return {"status": "success", "risk_level": current_risk}
    except Exception as e:
        import traceback
        logger.error(f"Error in receive_sensor_data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sensor-data/batch")
def receive_sensor_data_batch(payloads: list[SensorPayload], db: Session = Depends(get_db)):
    """Receive multiple sensor readings in batch for efficiency."""
    
    try:
        logger.info(f"Received batch of {len(payloads)} sensor readings")
        results = []
        
        for payload in payloads:
            # Process each reading individually
            result = receive_sensor_data(payload, db)
            results.append(result)
        
        return {"status": "success", "processed": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error in batch sensor data processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sensor-data/health")
def sensor_health_check():
    """Health check endpoint for sensor data reception."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "single": "/api/sensor-data",
            "batch": "/api/sensor-data/batch",
            "latest": "/api/latest-sensor-data"
        }
    }

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
        # If no risk data exists, return a default LOW risk
        return {"risk_level": "LOW", "confidence": 0.5, "timestamp": datetime.utcnow().isoformat()}
    return {
        "risk_level": data.risk_level,
        "confidence": data.confidence,
        "timestamp": data.timestamp.isoformat()
    }

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

@router.get("/latest-sensors")
def get_latest_sensors():
    """Get the latest sensor readings from ESP32 polling service."""
    from backend.services.sensor_poller import get_sensor_poller
    
    poller = get_sensor_poller()
    latest_data = poller.get_latest_data()
    
    if not latest_data:
        raise HTTPException(status_code=503, detail="No sensor data available - ESP32 may be offline")
    
    # Check if data is fresh (within last 30 seconds)
    if not poller.is_data_fresh(max_age_seconds=30):
        raise HTTPException(status_code=503, detail="Sensor data is stale - ESP32 may be offline")
    
    return {
        "temperature": latest_data.get("temperature"),
        "humidity": latest_data.get("humidity"),
        "dust": latest_data.get("dust"),
        "timestamp": latest_data.get("server_timestamp"),
        "esp32_timestamp": latest_data.get("timestamp"),
        "status": "ok"
    }

@router.post("/upload-food-image")
async def upload_food_image(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload food image, analyze for allergens using local Vision Transformer, and store result."""
    try:
        # 1. Save Image
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"food_{timestamp}.jpg"
        upload_dir = "uploads/food_images"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())
            
        logger.info(f"Saved uploaded image to {file_path}")
            
        # 2. Analyze Image using Local Vision Transformer
        analysis = detect_ingredients(file_path)
        
        if "error" in analysis:
            logger.error(f"Image analysis failed: {analysis['error']}")
            raise HTTPException(status_code=500, detail=analysis["error"])
            
        food_item = analysis.get("food_item", "Unknown")
        ingredients = analysis.get("ingredients", [])
        confidence = analysis.get("confidence", 0.0)
        
        logger.info(f"Analysis complete - Food: {food_item}, Ingredients: {ingredients}")
        
        # 3. Check for Allergens using new allergen checker
        detected_allergens, risk_level = check_ingredients_for_allergens(ingredients)
        
        logger.info(f"Allergen check complete - Allergens: {detected_allergens}, Risk: {risk_level}")
        
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
        
        logger.info(f"Analysis logged to database with ID: {db_log.id}")
        
        return {
            "food_item": food_item,
            "ingredients": ingredients,
            "detected_allergens": detected_allergens,
            "risk_level": risk_level,
            "confidence": confidence,
            "ai_explanation": ai_explanation,
            "image_url": f"/uploads/food_images/{filename}"
        }
    except Exception as e:
        logger.error(f"Error in upload_food_image: {e}")
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

@router.post("/capture-food-image")
async def capture_food_image(db: Session = Depends(get_db)):
    """Capture image from ESP32-CAM using robust capture method, analyze for allergens using Gemini Vision API, and store result."""
    try:
        # 1. Capture Image from ESP32-CAM using robust method
        camera = get_esp32_camera()
        
        logger.info("Capturing image from ESP32-CAM using robust capture method...")
        
        # Use the robust capture method with retries
        capture_result = camera.capture_image_robust(use_flash=True)
        
        if not capture_result["success"]:
            logger.error(f"ESP32-CAM capture failed: {capture_result['error']}")
            raise HTTPException(status_code=500, detail=capture_result["error"])
            
        file_path = capture_result["image_path"]
        filename = capture_result["filename"]
        logger.info(f"Captured image from ESP32-CAM: {file_path}")
            
        # 2. Analyze Image using Gemini Vision API
        from backend.ai_engine.gemini_vision import analyze_food_image_gemini
        
        analysis = analyze_food_image_gemini(file_path)
        
        if "error" in analysis:
            logger.error(f"Gemini analysis failed: {analysis['error']}")
            raise HTTPException(status_code=500, detail=analysis["error"])
            
        food_item = analysis.get("food_item", "Unknown")
        ingredients = analysis.get("ingredients", [])
        confidence = analysis.get("confidence", 0.0)
        
        logger.info(f"Gemini analysis complete - Food: {food_item}, Ingredients: {ingredients}")
        
        # 3. Check for Allergens using existing allergen checker
        detected_allergens, risk_level = check_ingredients_for_allergens(ingredients)
        
        logger.info(f"Allergen check complete - Allergens: {detected_allergens}, Risk: {risk_level}")
        
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
        
        logger.info(f"ESP32-CAM analysis logged to database with ID: {db_log.id}")
        
        return {
            "food_item": food_item,
            "ingredients": ingredients,
            "detected_allergens": detected_allergens,
            "risk_level": risk_level,
            "confidence": confidence,
            "ai_explanation": ai_explanation,
            "image_url": f"/uploads/avaris_cam/{filename}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in capture_food_image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/camera/stream-url")
def get_camera_stream_url():
    """Get the ESP32-CAM MJPEG stream URL."""
    camera = get_esp32_camera()
    return {
        "stream_url": camera.get_stream_url(),
        "available": camera.is_available()
    }

@router.post("/analyze-environment")
def analyze_environment(db: Session = Depends(get_db)):
    """
    Generate AI analysis of current environmental conditions using polled sensor data.
    Only called when user presses the Environment Analysis button.
    """
    try:
        # Get latest sensor data from polling service
        from backend.services.sensor_poller import get_sensor_poller
        
        poller = get_sensor_poller()
        latest_data = poller.get_latest_data()
        
        if not latest_data:
            raise HTTPException(status_code=503, detail="No sensor data available - ESP32 may be offline")
        
        if not poller.is_data_fresh(max_age_seconds=30):
            raise HTTPException(status_code=503, detail="Sensor data is stale - ESP32 may be offline")
        
        # Calculate risk level using polled data
        risk_level, confidence = calculate_rule_based_risk(
            latest_data["temperature"],
            latest_data["humidity"], 
            latest_data["dust"]
        )
        
        # Use existing reasoning functions to generate analysis
        analysis = explain_risk(risk_level, latest_data["temperature"], latest_data["humidity"], latest_data["dust"])
        
        return {
            "analysis": analysis,
            "sensor_data": {
                "temperature": latest_data["temperature"],
                "humidity": latest_data["humidity"],
                "dust": latest_data["dust"],
                "timestamp": latest_data["server_timestamp"]
            },
            "risk_level": risk_level,
            "confidence": confidence,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing environment: {e}")
        raise HTTPException(status_code=500, detail=f"Environment analysis failed: {str(e)}")
