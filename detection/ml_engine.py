import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from database.db import insert_alert
from detection.mitre_mapper import get_mitre_mapping

def run_ml_anomaly_detection():
    """
    Runs Scikit-learn IsolationForest anomaly detection on logged events.
    """
    from database.db import get_db_connection
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp ASC", conn)
    conn.close()

    if df.empty or len(df) < 5:
        return []

    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['hour'] = df['timestamp_dt'].dt.hour.fillna(12)
    df['dayofweek'] = df['timestamp_dt'].dt.dayofweek.fillna(0)
    df['is_failed'] = (df['status'] == 'FAILED').astype(int)

    # Calculate user and IP risk counts as features
    ip_failed_counts = df.groupby('source_ip')['is_failed'].transform('sum')
    user_failed_counts = df.groupby('username')['is_failed'].transform('sum')

    df['ip_failed_cnt'] = ip_failed_counts
    df['user_failed_cnt'] = user_failed_counts

    feature_cols = ['hour', 'dayofweek', 'is_failed', 'ip_failed_cnt', 'user_failed_cnt']
    X = df[feature_cols].values

    # Fit IsolationForest
    iso_forest = IsolationForest(contamination=0.15, random_state=42)
    predictions = iso_forest.fit_predict(X)
    scores = iso_forest.decision_function(X)

    df['anomaly'] = predictions  # -1 = anomaly, 1 = normal
    df['anomaly_score'] = scores

    anomalies = df[df['anomaly'] == -1]
    ml_alerts = []

    for _, row in anomalies.iterrows():
        # Only alert if anomaly score is low and event is failed or unusual
        if row['anomaly_score'] < -0.05:
            mitre = get_mitre_mapping("ML_ANOMALY")
            alt_id = f"ALT-ML-{row['source_ip'].replace('.', '')}-{row['username']}-{int(row['timestamp_dt'].timestamp())}"
            alert_obj = {
                "alert_id": alt_id,
                "timestamp": str(row['timestamp']),
                "source_ip": str(row['source_ip']),
                "username": str(row['username']),
                "attack_type": "ML Behavioral Anomaly",
                "severity": "High" if row['is_failed'] == 1 else "Medium",
                "description": f"Scikit-learn IsolationForest flagged event as statistical anomaly (Score: {row['anomaly_score']:.3f}). User '{row['username']}' from IP {row['source_ip']} exhibiting outlier login patterns.",
                "mitre_tactic": mitre['tactic'],
                "mitre_technique_id": mitre['id'],
                "mitre_technique_name": mitre['name']
            }
            insert_alert(alert_obj)
            ml_alerts.append(alert_obj)

    return ml_alerts
