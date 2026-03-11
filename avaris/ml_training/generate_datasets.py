import pandas as pd
import numpy as np
import os

# Create ml_models directory if it doesn't exist to store trained models
os.makedirs("backend/ml_models", exist_ok=True)
os.makedirs("ml_training/datasets", exist_ok=True)

def generate_risk_dataset(num_samples=1000):
    """Generate dummy dataset for Risk Classification."""
    np.random.seed(42)
    
    # Temperature (10 to 50 Celsius)
    temperature = np.random.uniform(10, 50, num_samples)
    # Humidity (10% to 90%)
    humidity = np.random.uniform(10, 90, num_samples)
    # Dust (0 to 500 ug/m3)
    dust = np.random.uniform(0, 500, num_samples)
    
    # Determine risk level based on simple rules
    risk_levels = []
    for t, h, d in zip(temperature, humidity, dust):
        if t > 40 or d > 300:
            risk = "CRITICAL"
        elif t > 35 or d > 200 or h > 80:
            risk = "HIGH"
        elif t > 30 or d > 100 or h > 70:
            risk = "MEDIUM"
        else:
            risk = "LOW"
        risk_levels.append(risk)
        
    df = pd.DataFrame({
        "temperature": temperature,
        "humidity": humidity,
        "dust": dust,
        "risk_level": risk_levels
    })
    
    df.to_csv("ml_training/datasets/risk_dataset.csv", index=False)
    print("Risk dataset generated: ml_training/datasets/risk_dataset.csv")

def generate_anomaly_dataset(num_samples=1000):
    """Generate dummy dataset for Anomaly Detection (mostly normal + some anomalies)."""
    np.random.seed(42)
    
    # Normal data
    normal_temp = np.random.normal(25, 3, int(num_samples * 0.9))
    normal_hum = np.random.normal(45, 10, int(num_samples * 0.9))
    normal_dust = np.random.normal(30, 10, int(num_samples * 0.9))
    
    # Anomaly data
    anomaly_temp = np.random.uniform(40, 60, int(num_samples * 0.1))
    anomaly_hum = np.random.uniform(80, 100, int(num_samples * 0.1))
    anomaly_dust = np.random.uniform(300, 500, int(num_samples * 0.1))
    
    temperature = np.concatenate([normal_temp, anomaly_temp])
    humidity = np.concatenate([normal_hum, anomaly_hum])
    dust = np.concatenate([normal_dust, anomaly_dust])
    
    # Label 1 for normal, -1 for anomaly (Isolation Forest convention)
    labels = [1] * len(normal_temp) + [-1] * len(anomaly_temp)
    
    df = pd.DataFrame({
        "temperature": temperature,
        "humidity": humidity,
        "dust": dust,
        "label": labels
    })
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    df.to_csv("ml_training/datasets/anomaly_dataset.csv", index=False)
    print("Anomaly dataset generated: ml_training/datasets/anomaly_dataset.csv")

def generate_forecast_dataset(num_samples=1000):
    """Generate time-series dummy dataset for Forecasting."""
    np.random.seed(42)
    
    # Create a time series with some trend and seasonality
    time = np.arange(num_samples)
    
    temperature = 25 + 10 * np.sin(time / 50) + np.random.normal(0, 1, num_samples)
    humidity = 50 + 20 * np.cos(time / 60) + np.random.normal(0, 5, num_samples)
    dust = 20 + time * 0.05 + np.random.normal(0, 5, num_samples)
    
    df = pd.DataFrame({
        "timestamp": pd.date_range(start="2023-01-01", periods=num_samples, freq="1Min"),
        "temperature": temperature,
        "humidity": humidity,
        "dust": dust
    })
    
    df.to_csv("ml_training/datasets/forecast_dataset.csv", index=False)
    print("Forecast dataset generated: ml_training/datasets/forecast_dataset.csv")

if __name__ == "__main__":
    generate_risk_dataset()
    generate_anomaly_dataset()
    generate_forecast_dataset()
