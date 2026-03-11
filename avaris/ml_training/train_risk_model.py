import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Create ml_models directory if it doesn't exist
os.makedirs("backend/ml_models", exist_ok=True)

def train_risk_model():
    print("Loading risk dataset...")
    try:
        df = pd.read_csv("ml_training/datasets/risk_dataset.csv")
    except FileNotFoundError:
        print("Dataset not found. Please run generate_datasets.py first.")
        return

    # Features: temperature, humidity, dust
    X = df[['temperature', 'humidity', 'dust']]
    y = df['risk_level']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train RandomForestClassifier
    print("Training RandomForestClassifier for Risk Prediction...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\nModel Evaluation:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Save model
    model_path = "backend/ml_models/risk_model.pkl"
    joblib.dump(model, model_path)
    print(f"\nModel saved successfully to {model_path}")

if __name__ == "__main__":
    train_risk_model()
