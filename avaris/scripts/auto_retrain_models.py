import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import IsolationForest

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.models import SensorData, RiskPrediction, AnomalyEvent, SessionLocal

def fetch_data():
    """Fetch all sensor data from the database."""
    db = SessionLocal()
    try:
        data = db.query(SensorData).all()
        if not data:
            return None
            
        df = pd.DataFrame([{
            'temperature': d.temperature,
            'humidity': d.humidity,
            'dust': d.dust,
            'timestamp': d.timestamp
        } for d in data])
        return df
    finally:
        db.close()

def evaluate_retraining_trigger(df):
    """Check if we have enough new data rows (e.g., > 500) since last retraining."""
    # In a real system, we'd store the last retraining row count
    # For now, if the DB has > 500 rows, we trigger retraining as requested by requirements
    if df is not None and len(df) > 500:
        return True
    return False

def retrain_risk_model(df):
    print("Retraining Risk Classification Model...")
    # Generate labels dynamically (in a real system, you'd need labeled data or manual review)
    # Reusing the simple rule logic from generate_datasets:
    risk_levels = []
    for t, h, d in zip(df['temperature'], df['humidity'], df['dust']):
        if t > 40 or d > 300: risk_levels.append("CRITICAL")
        elif t > 35 or d > 200 or h > 80: risk_levels.append("HIGH")
        elif t > 30 or d > 100 or h > 70: risk_levels.append("MEDIUM")
        else: risk_levels.append("LOW")
    
    X = df[['temperature', 'humidity', 'dust']]
    y = pd.Series(risk_levels)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, "backend/ml_models/risk_model.pkl")
    print("Risk Classification Model retrained and saved.")

def retrain_anomaly_model(df):
    print("Retraining Anomaly Detection Model...")
    X = df[['temperature', 'humidity', 'dust']]
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X)
    joblib.dump(model, "backend/ml_models/anomaly_model.pkl")
    print("Anomaly Detection Model retrained and saved.")

def retrain_forecast_model(df):
    print("Retraining Forecasting Model...")
    df = df.sort_values('timestamp').reset_index(drop=True)
    lookahead_steps = 30
    df['target_temperature'] = df['temperature'].shift(-lookahead_steps)
    df['target_humidity'] = df['humidity'].shift(-lookahead_steps)
    df['target_dust'] = df['dust'].shift(-lookahead_steps)
    df = df.dropna()

    if len(df) < lookahead_steps:
        print("Not enough data to retrain forecasting model.")
        return

    X = df[['temperature', 'humidity', 'dust']]
    y = df[['target_temperature', 'target_humidity', 'target_dust']]

    base_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model = MultiOutputRegressor(base_model)
    model.fit(X, y)
    
    joblib.dump(model, "backend/ml_models/forecast_model.pkl")
    print("Forecasting Model retrained and saved.")

def main():
    print("Checking if models need retraining...")
    df = fetch_data()
    
    if evaluate_retraining_trigger(df):
        print("Retraining triggered ( sufficient data found )")
        retrain_risk_model(df)
        retrain_anomaly_model(df)
        retrain_forecast_model(df)
        print("All models successfully retrained.")
    else:
        print(f"Not enough data for retraining. Current rows: {len(df) if df is not None else 0}. Required: > 500.")

if __name__ == "__main__":
    main()
