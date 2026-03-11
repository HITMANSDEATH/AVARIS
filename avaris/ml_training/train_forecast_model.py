import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib
import os

# Create ml_models directory if it doesn't exist
os.makedirs("backend/ml_models", exist_ok=True)

def train_forecast_model():
    print("Loading forecast dataset...")
    try:
        df = pd.read_csv("ml_training/datasets/forecast_dataset.csv", parse_dates=['timestamp'])
    except FileNotFoundError:
        print("Dataset not found. Please run generate_datasets.py first.")
        return

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Simple approach: predict values 30 steps (minutes) ahead using current values
    # In a real scenario, we'd use a window of previous values (LSTM/ARIMA etc.)
    # Here, for simplicity while keeping it working locally, we shift targets
    
    lookahead_steps = 30
    
    # Create target columns by shifting the dataframe
    df['target_temperature'] = df['temperature'].shift(-lookahead_steps)
    df['target_humidity'] = df['humidity'].shift(-lookahead_steps)
    df['target_dust'] = df['dust'].shift(-lookahead_steps)

    # Drop the last 'lookahead_steps' rows where targets are NaN
    df = df.dropna()

    # Features: current values
    X = df[['temperature', 'humidity', 'dust']]
    
    # Targets: future values (+30 mins)
    y = df[['target_temperature', 'target_humidity', 'target_dust']]

    # Split data (time-series aware split, don't shuffle)
    train_size = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

    print(f"Training MultiOutput GradientBoostingRegressor (Forecasting {lookahead_steps} steps ahead)...")
    # Base regressor
    base_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    # Wrap in MultiOutputRegressor to predict multiple values (temp, hum, dust)
    model = MultiOutputRegressor(base_model)
    
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    
    # Basic Evaluation (MAE)
    mae = np.mean(np.abs(y_test.values - y_pred), axis=0)
    
    print("\nModel Evaluation (Mean Absolute Error on Test Set):")
    print(f"Temperature MAE: {mae[0]:.2f}")
    print(f"Humidity MAE:    {mae[1]:.2f}")
    print(f"Dust MAE:        {mae[2]:.2f}")

    # Save model
    model_path = "backend/ml_models/forecast_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved successfully to {model_path}")

if __name__ == "__main__":
    train_forecast_model()
