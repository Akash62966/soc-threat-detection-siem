import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scans.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS url_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            url TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_score INTEGER NOT NULL,
            features_json TEXT,
            explanation TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_scan(url, prediction, confidence, risk_score, features_dict, explanation):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO url_scans (url, prediction, confidence, risk_score, features_json, explanation)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        url,
        prediction,
        round(confidence, 4),
        risk_score,
        json.dumps(features_dict),
        explanation
    ))
    conn.commit()
    scan_id = cursor.lastrowid
    conn.close()
    return scan_id

def get_recent_scans(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM url_scans ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_scan_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM url_scans")
    total_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM url_scans WHERE prediction = 'Legitimate'")
    legit_scans = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM url_scans WHERE prediction = 'Potential Phishing'")
    phishing_scans = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(confidence) FROM url_scans")
    avg_conf = cursor.fetchone()[0] or 0.0

    conn.close()

    return {
        "total_scans": total_scans,
        "legit_scans": legit_scans,
        "phishing_scans": phishing_scans,
        "avg_confidence": round(avg_conf * 100, 1)
    }

def clear_scans():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM url_scans")
    conn.commit()
    conn.close()
