import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# Create ml_models directory if it doesn't exist
os.makedirs("backend/ml_models", exist_ok=True)

def train_anomaly_model():
    print("Loading anomaly dataset...")
    try:
        df = pd.read_csv("ml_training/datasets/anomaly_dataset.csv")
    except FileNotFoundError:
        print("Dataset not found. Please run generate_datasets.py first.")
        return

    # Features: temperature, humidity, dust
    X = df[['temperature', 'humidity', 'dust']]
    y = df['label'] # For IF, 1 is normal, -1 is anomaly (though unsupervised, we can use labels for basic evaluation)

    print("Training IsolationForest model for Anomaly Detection...")
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    
    # Fit the model (IsolationForest is unsupervised, so we fit on X)
    model.fit(X)

    # Predictions
    y_pred = model.predict(X)
    
    # Simple manual evaluation (just counts of predictions vs true labels)
    correct_normals = sum((y_pred == 1) & (y == 1))
    correct_anomalies = sum((y_pred == -1) & (y == -1))
    
    print("\nModel Evaluation (approximate on training data):")
    print(f"Correctly predicted normals: {correct_normals}/{sum(y == 1)}")
    print(f"Correctly predicted anomalies: {correct_anomalies}/{sum(y == -1)}")

    # Save model
    model_path = "backend/ml_models/anomaly_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved successfully to {model_path}")

if __name__ == "__main__":
    train_anomaly_model()
