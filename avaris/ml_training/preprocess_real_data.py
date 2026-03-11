import pandas as pd
import numpy as np
import os

# Paths
AQ_DATASET = "../Air-Quality-Dataset.csv"
POLLUTION_DATASET = "../Indoor Air Pollution_Data.csv"
OUTPUT_DIR = "ml_training/datasets"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess_aq_dataset():
    """Preprocess Air-Quality-Dataset.csv for Risk and Forecast."""
    print(f"Loading {AQ_DATASET}...")
    try:
        # Delimiter is ';' and decimal is ','
        df = pd.read_csv(AQ_DATASET, sep=';', decimal=',')
    except Exception as e:
        print(f"Error loading {AQ_DATASET}: {e}")
        return None

    # Rename columns to match AVARIS requirements
    df = df.rename(columns={
        'TEMPERATURE': 'temperature',
        'HUMIDITY': 'humidity',
        'PM2,5': 'dust',
        'TIME': 'timestamp',
        'PM2,5 CATEGORY': 'risk_cat'
    })

    # Map Risk Category to AVARIS risk levels
    risk_mapping = {
        'GOOD': 'LOW',
        'Moderate': 'MEDIUM',
        'Unhealthy': 'HIGH',
        'Very Unhealthy': 'CRITICAL'
    }
    df['risk_level'] = df['risk_cat'].map(risk_mapping).fillna('LOW')

    # Keep only relevant columns
    cols = ['timestamp', 'temperature', 'humidity', 'dust', 'risk_level']
    df = df[cols]
    
    # Simple cleaning
    df = df.dropna()
    
    return df

def preprocess_pollution_dataset():
    """Preprocess Indoor Air Pollution_Data.csv for Anomaly Detection."""
    print(f"Loading {POLLUTION_DATASET}...")
    try:
        df = pd.read_csv(POLLUTION_DATASET)
        print(f"Pollution dataset columns: {df.columns.tolist()}")
        # Strip any accidental whitespace from headers
        df.columns = [c.strip() for c in df.columns]
    except Exception as e:
        print(f"Error loading {POLLUTION_DATASET}: {e}")
        return None

    # Rename columns (check for alternates if necessary)
    rename_map = {
        'Temp': 'temperature',
        'Humidity': 'humidity',
        'PM2.5': 'dust',
        'Label': 'anomaly_label'
    }
    
    # Check which columns actually exist from our mapping
    actual_rename = {k: v for k, v in rename_map.items() if k in df.columns}
    print(f"Renaming pollution columns: {actual_rename}")
    df = df.rename(columns=actual_rename)

    if 'anomaly_label' in df.columns:
        # Map Anomaly labels (0 -> 1 Normal, 1 -> -1 Anomaly)
        # Note: Some datasets might have strings or different integers
        df['label'] = pd.to_numeric(df['anomaly_label'], errors='coerce').map({0: 1, 1: -1}).fillna(1)
    else:
        print("Warning: 'anomaly_label' not found after rename. Available columns:", df.columns.tolist())
        return None
    
    # Keep only relevant columns
    cols = ['temperature', 'humidity', 'dust', 'label']
    # Filter to only existing columns to avoid KeyError
    cols = [c for c in cols if c in df.columns]
    df = df[cols]
    
    # Simple cleaning
    df = df.dropna()
    
    return df

def run_preprocessing():
    print("Starting data preprocessing...")
    
    aq_df = preprocess_aq_dataset()
    poll_df = preprocess_pollution_dataset()
    
    if aq_df is not None:
        # Save Risk Dataset
        risk_df = aq_df[['temperature', 'humidity', 'dust', 'risk_level']]
        risk_df.to_csv(os.path.join(OUTPUT_DIR, "risk_dataset.csv"), index=False)
        print(f"Saved risk_dataset.csv to {OUTPUT_DIR}")
        
        # Save Forecast Dataset
        forecast_df = aq_df[['timestamp', 'temperature', 'humidity', 'dust']]
        forecast_df.to_csv(os.path.join(OUTPUT_DIR, "forecast_dataset.csv"), index=False)
        print(f"Saved forecast_dataset.csv to {OUTPUT_DIR}")
        
    if poll_df is not None:
        # Save Anomaly Dataset
        anomaly_df = poll_df[['temperature', 'humidity', 'dust', 'label']]
        anomaly_df.to_csv(os.path.join(OUTPUT_DIR, "anomaly_dataset.csv"), index=False)
        print(f"Saved anomaly_dataset.csv to {OUTPUT_DIR}")

if __name__ == "__main__":
    run_preprocessing()
