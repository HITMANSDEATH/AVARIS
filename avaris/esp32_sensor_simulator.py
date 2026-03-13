#!/usr/bin/env python3
"""
ESP32 Sensor Server Simulator for AVARIS Testing
Simulates the ESP32 /sensors endpoint for development and testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
import time
from datetime import datetime

app = FastAPI(title="ESP32 Sensor Simulator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulate realistic sensor readings
def generate_sensor_data():
    """Generate realistic sensor readings"""
    # Base values with some variation
    base_temp = 23.0 + random.uniform(-3, 7)  # 20-30°C
    base_humidity = 45.0 + random.uniform(-15, 25)  # 30-70%
    base_dust = 25.0 + random.uniform(-10, 40)  # 15-65 µg/m³
    
    # Add some correlation (higher humidity = slightly higher dust)
    if base_humidity > 60:
        base_dust += random.uniform(0, 15)
    
    # Ensure reasonable ranges
    base_temp = max(15, min(35, base_temp))
    base_humidity = max(20, min(90, base_humidity))
    base_dust = max(0, min(150, base_dust))
    
    return {
        "temperature": round(base_temp, 1),
        "humidity": round(base_humidity, 1),
        "dust": round(base_dust, 1),
        "timestamp": int(time.time() * 1000),  # ESP32 timestamp
        "status": "ok"
    }

@app.get("/")
def root():
    """Root endpoint with basic info"""
    return {
        "message": "ESP32 Sensor Simulator",
        "endpoints": ["/sensors"],
        "status": "running"
    }

@app.get("/sensors")
def get_sensors():
    """Simulate ESP32 /sensors endpoint"""
    return generate_sensor_data()

if __name__ == "__main__":
    print("Starting ESP32 Sensor Simulator...")
    print("Access at: http://localhost:8080/sensors")
    print("Use this for testing when ESP32 hardware is not available")
    uvicorn.run(app, host="0.0.0.0", port=8080)