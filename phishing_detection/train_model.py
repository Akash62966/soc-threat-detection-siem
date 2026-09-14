import os
import json
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from feature_extraction import get_feature_vector, FEATURE_NAMES

def train_and_evaluate_models():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "dataset", "phishing_urls.csv")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)

    # Extract feature matrix X and label vector y
    X_list = [get_feature_vector(url) for url in df["url"]]
    X = np.array(X_list)
    y = df["label"].values

    print(f"Feature matrix shape: {X.shape}, Labels shape: {y.shape}")

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Standard Scaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Dictionary of classifiers to evaluate
    classifiers = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Support Vector Machine": SVC(probability=True, random_state=42)
    }

    results = {}
    best_model_name = None
    best_f1 = -1.0
    best_model_obj = None

    print("\n--- Model Training & Comparison ---")
    for name, model in classifiers.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "confusion_matrix": cm
        }

        print(f"[{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | F1: {f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = model

    print(f"\nTop Model Selected: {best_model_name} (F1-Score: {best_f1:.4f})")

    # Feature Importance for Random Forest
    rf_model = classifiers["Random Forest"]
    importances = rf_model.feature_importances_.tolist()
    feature_imp_map = dict(zip(FEATURE_NAMES, [round(val, 4) for val in importances]))

    model_dir = os.path.join(base_dir, "model")
    os.makedirs(model_dir, exist_ok=True)

    # Serialize top model & scaler
    model_save_path = os.path.join(model_dir, "phishing_model.joblib")
    scaler_save_path = os.path.join(model_dir, "scaler.joblib")
    metrics_save_path = os.path.join(model_dir, "model_metrics.json")

    joblib.dump(best_model_obj, model_save_path)
    joblib.dump(scaler, scaler_save_path)

    metrics_payload = {
        "best_model": best_model_name,
        "models": results,
        "feature_importances": feature_imp_map,
        "feature_names": FEATURE_NAMES,
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }

    with open(metrics_save_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=4)

    print(f"Model successfully saved to {model_save_path}")
    print(f"Scaler saved to {scaler_save_path}")
    print(f"Metrics written to {metrics_save_path}")

    return metrics_payload

if __name__ == "__main__":
    train_and_evaluate_models()
