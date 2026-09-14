from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
import joblib
import numpy as np
import pandas as pd

from feature_extraction import extract_features_from_url, get_feature_vector, explain_features, FEATURE_NAMES
from database import init_db, insert_scan, get_recent_scans, get_scan_kpis, clear_scans

app = Flask(__name__)
app.secret_key = "phishing-url-detector-secret-key-safe-lab"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "phishing_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.joblib")
METRICS_PATH = os.path.join(BASE_DIR, "model", "model_metrics.json")

# Load serialized model & scaler
model = None
scaler = None
model_metrics = {}

with app.app_context():
    init_db()
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            model_metrics = json.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    kpis = get_scan_kpis()
    recent = get_recent_scans(limit=20)
    return render_template('dashboard.html', kpis=kpis, recent_scans=recent)

@app.route('/evaluate')
def evaluate_page():
    return render_template('evaluate.html', metrics=model_metrics)

@app.route('/dataset')
def dataset_page():
    dataset_path = os.path.join(BASE_DIR, "dataset", "phishing_urls.csv")
    sample_rows = []
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        sample_rows = df.head(50).to_dict('records')
    
    importances = model_metrics.get("feature_importances", {})
    return render_template('dataset_view.html', samples=sample_rows, importances=importances)

# ================= REST API ENDPOINTS =================

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json() or {}
    raw_url = data.get('url', '').strip()

    if not raw_url:
        return jsonify({"error": "Please enter a valid URL to analyze."}), 400

    if len(raw_url) > 2048:
        return jsonify({"error": "URL exceeds maximum permitted length (2048 characters)."}), 400

    # Ensure model is ready
    if model is None or scaler is None:
        return jsonify({"error": "Machine learning model is not loaded. Please run train_model.py first."}), 500

    try:
        # Extract features (defensive passive evaluation only - NO external network connection)
        feats_dict = extract_features_from_url(raw_url)
        vector = [feats_dict[name] for name in FEATURE_NAMES]

        vector_scaled = scaler.transform([vector])
        pred_class = int(model.predict(vector_scaled)[0])

        # Get class probabilities
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(vector_scaled)[0]
            phishing_prob = float(probs[1])
        else:
            phishing_prob = 1.0 if pred_class == 1 else 0.0

        label = "Potential Phishing" if pred_class == 1 else "Legitimate"
        confidence = round(phishing_prob if pred_class == 1 else (1.0 - phishing_prob), 4)
        risk_score = int(phishing_prob * 100)

        explanations = explain_features(raw_url)
        exp_text = " | ".join(explanations)

        # Save scan result to local SQLite DB
        scan_id = insert_scan(
            url=raw_url,
            prediction=label,
            confidence=confidence,
            risk_score=risk_score,
            features_dict=feats_dict,
            explanation=exp_text
        )

        return jsonify({
            "scan_id": scan_id,
            "url": raw_url,
            "prediction": label,
            "is_phishing": bool(pred_class == 1),
            "confidence_percent": round(confidence * 100, 1),
            "risk_score": risk_score,
            "features": feats_dict,
            "explanations": explanations,
            "disclaimer": "Defensive educational result. This model evaluates structural/lexical probability and does not guarantee complete security."
        })

    except Exception as e:
        return jsonify({"error": f"Error processing URL prediction: {str(e)}"}), 500

@app.route('/api/kpis', methods=['GET'])
def api_kpis():
    return jsonify(get_scan_kpis())

@app.route('/api/clear-history', methods=['POST'])
def api_clear_history():
    clear_scans()
    return jsonify({"message": "Scan history successfully reset."})

if __name__ == '__main__':
    app.run(debug=True, port=5051)
