from flask import Flask, render_template, request, jsonify, redirect, flash, url_for
import os
import pandas as pd
import io
from database.db import (
    init_db, get_logs, get_alerts, update_alert_status,
    get_alert_by_id, get_related_logs_for_alert, get_ip_intel,
    get_kpis, get_chart_data, insert_logs, clear_all_data
)
from detection.rules import run_rule_engine
from detection.ml_engine import run_ml_anomaly_detection
from detection.mitre_mapper import get_all_mitre_matrix

app = Flask(__name__)
app.secret_key = "soc-siem-dashboard-secret-key-safe-lab"

# Ensure database is initialized on startup
with app.app_context():
    init_db()

@app.route('/')
def dashboard():
    kpis = get_kpis()
    recent_alerts = get_alerts(limit=5)
    return render_template('index.html', kpis=kpis, recent_alerts=recent_alerts)

@app.route('/logs')
def logs_page():
    status_filter = request.args.get('status', 'ALL')
    username_filter = request.args.get('username', '')
    ip_filter = request.args.get('ip', '')
    logs_list = get_logs(limit=200, status=status_filter, username=username_filter, ip=ip_filter)
    return render_template('logs.html', logs=logs_list, status_filter=status_filter, username_filter=username_filter, ip_filter=ip_filter)

@app.route('/alerts')
def alerts_page():
    severity_filter = request.args.get('severity', 'ALL')
    status_filter = request.args.get('status', 'ALL')
    alerts_list = get_alerts(severity=severity_filter, status=status_filter, limit=200)
    return render_template('alerts.html', alerts=alerts_list, severity_filter=severity_filter, status_filter=status_filter)

@app.route('/investigate/<alert_id>')
def investigate_page(alert_id):
    alert = get_alert_by_id(alert_id)
    if not alert:
        flash("Alert not found.", "danger")
        return redirect(url_for('alerts_page'))

    related_logs = get_related_logs_for_alert(
        source_ip=alert['source_ip'],
        username=alert['username'],
        alert_timestamp=alert['timestamp']
    )

    # Automated root cause / explanation synthesis
    explanation = generate_automated_explanation(alert, related_logs)

    return render_template('investigate.html', alert=alert, logs=related_logs, explanation=explanation)

@app.route('/ip-analysis')
def ip_analysis_page():
    intel_data = get_ip_intel()
    return render_template('ip_analysis.html', intel_data=intel_data)

@app.route('/mitre')
def mitre_page():
    matrix = get_all_mitre_matrix()
    return render_template('mitre.html', matrix=matrix)

# ================= REST API ENDPOINTS =================

@app.route('/api/kpis', methods=['GET'])
def api_kpis():
    return jsonify(get_kpis())

@app.route('/api/chart-data', methods=['GET'])
def api_chart_data():
    return jsonify(get_chart_data())

@app.route('/api/upload-logs', methods=['POST'])
def api_upload_logs():
    if 'log_file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['log_file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV log files are supported"}), 400

    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8", errors="ignore")))
        required_cols = ['timestamp', 'username', 'source_ip', 'status']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({"error": f"Missing required CSV column: '{col}'"}), 400

        logs_data = df.to_dict('records')
        inserted = insert_logs(logs_data)

        # Run threat detection rules and ML anomaly engine
        rule_alerts = run_rule_engine()
        ml_alerts = run_ml_anomaly_detection()

        return jsonify({
            "message": "Logs successfully ingested and analyzed.",
            "inserted_logs": inserted,
            "rule_alerts_generated": len(rule_alerts),
            "ml_alerts_generated": len(ml_alerts)
        })

    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV file: {str(e)}"}), 500

@app.route('/api/load-sample-data', methods=['POST'])
def api_load_sample_data():
    try:
        sample_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_auth_logs.csv")
        if not os.path.exists(sample_path):
            return jsonify({"error": "Sample data file not found"}), 44

        df = pd.read_csv(sample_path)
        logs_data = df.to_dict('records')
        inserted = insert_logs(logs_data)

        # Trigger detection engines
        rule_alerts = run_rule_engine()
        ml_alerts = run_ml_anomaly_detection()

        return jsonify({
            "message": "Sample authentication logs successfully loaded!",
            "inserted_logs": inserted,
            "rule_alerts_generated": len(rule_alerts),
            "ml_alerts_generated": len(ml_alerts)
        })
    except Exception as e:
        return jsonify({"error": f"Error loading sample data: {str(e)}"}), 500

@app.route('/api/alerts/<alert_id>/status', methods=['POST'])
def api_update_alert_status(alert_id):
    data = request.get_json() or {}
    new_status = data.get('status', 'INVESTIGATING')
    success = update_alert_status(alert_id, new_status)
    if success:
        return jsonify({"message": f"Alert status updated to {new_status}"})
    return jsonify({"error": "Alert not found"}), 44

@app.route('/api/clear-data', methods=['POST'])
def api_clear_data():
    clear_all_data()
    return jsonify({"message": "Database successfully reset."})

def generate_automated_explanation(alert, related_logs):
    """
    Generates a clear human-readable SOC analyst breakdown explaining why an alert was flagged.
    """
    attack_type = alert['attack_type']
    ip = alert['source_ip']
    user = alert['username']
    sev = alert['severity']
    desc = alert['description']

    failed_count = sum(1 for l in related_logs if l['status'] == 'FAILED')
    success_count = sum(1 for l in related_logs if l['status'] == 'SUCCESS')

    lines = [
        f"Incident Investigation Summary for {alert['alert_id']}:",
        f"• Flagged Attack Pattern: {attack_type} (Severity Level: {sev})",
        f"• Key Entities: Source IP [{ip}] | Target User [{user}]",
        f"• Trigger Rationale: {desc}",
        f"• Contextual Log Evidence: Found {len(related_logs)} total log events associated with this entity pair ({failed_count} FAILED, {success_count} SUCCESSFUL).",
    ]

    if attack_type == "Brute Force Attack":
        lines.append("• SOC Assessment: High density of authentication failures over a short timeframe indicates automated credential guessing / password spray tool execution.")
    elif attack_type == "Impossible Travel Anomaly":
        lines.append("• SOC Assessment: User authenticated successfully from two geographically disparate networks in rapid succession. High probability of compromised credentials or unapproved VPN usage.")
    elif attack_type == "Password Spraying":
        lines.append("• SOC Assessment: Single IP addressing multiple distinct corporate user accounts indicates horizontal password spraying attempt.")
    elif attack_type == "Suspicious IP Indicator":
        lines.append("• SOC Assessment: Originating IP matches known TOR egress or anonymous proxy infrastructure.")
    else:
        lines.append("• SOC Assessment: Statistical outlier flagged by IsolationForest machine learning model comparing user baseline behavior vs incoming event properties.")

    return "\n".join(lines)

if __name__ == '__main__':
    app.run(debug=True, port=5050)
