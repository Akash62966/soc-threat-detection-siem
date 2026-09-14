# SOC Threat Detection & SIEM Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Framework-Flask-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![Scikit-Learn](https://img.shields.io/badge/ML-IsolationForest-orange)
![MITRE ATT&CK](https://img.shields.io/badge/Mapping-MITRE%20ATT%26CK-red)

A realistic, production-ready Security Operations Center (SOC) dashboard and Security Information and Event Management (SIEM) application built in Python Flask. Analyzes authentication and system log streams to detect suspicious activity such as brute-force attacks, password spraying, impossible travel anomalies, suspicious IP indicators, and machine learning behavioral outliers.

---

## 📌 Features & Highlights

1. **SOC Executive Dashboard**:
   - Real-time KPI metrics: Total log events, successful logins, failed logins, active security alerts, flagged suspicious IPs, and critical unresolved incidents.
   - Dynamic Chart.js visualizations: 24-hour authentication activity timeline, alert severity doughnut breakdown, top attack vectors, and Machine Learning status.

2. **Log Ingestion Engine**:
   - Supports custom CSV authentication log uploads with schema validation.
   - Built-in one-click realistic sample log generator containing multi-stage attack scenarios.
   - Automatic timestamp parsing, IP extraction, status tracking, and device fingerprinting.

3. **Rule-Based Threat Detection Engine**:
   - **Brute-Force Attack (T1110.001)**: Identifies $\ge 5$ failed logins within a rolling 10-minute window for a specific user/IP pair.
   - **Password Spraying (T1110.003)**: Detects a single IP targeting multiple distinct user accounts.
   - **Impossible Travel Anomaly (T1078)**: Flags rapid successive logins from disparate geographic locations within an impossible timeframe.
   - **Off-Hours Authentication (T1078.004)**: Identifies failed login attempts occurring during unusual non-business hours (00:00 - 05:00 UTC).
   - **Suspicious IP Indicator (T1090)**: Flags requests originating from TOR exit nodes, anonymizing proxies, or high-failure IP addresses.

4. **Machine Learning Anomaly Detection**:
   - Uses Scikit-learn's **IsolationForest** model to analyze multi-dimensional feature vectors (hour of day, day of week, login status, failure rate density).
   - Automatically detects non-linear statistical outliers and assigns risk scores.

5. **Security Alert Queue & Triage**:
   - Generates structured security alerts assigned one of 4 severity levels: `Low`, `Medium`, `High`, `Critical`.
   - Allows analysts to update incident triage states (`NEW` -> `INVESTIGATING` -> `RESOLVED`).

6. **Incident Deep-Dive & Timeline View**:
   - Provides a comprehensive forensics view with automated incident explanation generation.
   - Chronological event timeline showing logs preceding and following the flagged alert.

7. **IP Threat Intelligence Directory**:
   - Passive local metric aggregation for source IP addresses.
   - Calculates dynamic risk scores (0–100) and assigns threat tags without intrusive external scanning.

8. **MITRE ATT&CK Framework Mapping**:
   - Maps every detection rule to standardized MITRE ATT&CK tactics and technique IDs for educational defensive training.

---

## 🏗️ System Architecture

```
soc-siem-dashboard/
├── app.py                     # Main Flask application entry point & API endpoints
├── requirements.txt           # Python dependencies
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLite schema setup & queries
│   └── siem.db                # Auto-created SQLite database
├── detection/
│   ├── __init__.py
│   ├── rules.py               # Rule-based detection logic
│   ├── ml_engine.py           # IsolationForest anomaly model
│   └── mitre_mapper.py        # MITRE ATT&CK technique mapping
├── sample_data/
│   └── sample_auth_logs.csv   # Pre-populated realistic attack dataset
├── static/
│   ├── css/
│   │   └── style.css          # Dark SOC Theme styling
│   └── js/
│       ├── dashboard.js       # Chart.js charts & AJAX controls
│       └── alerts.js          # Alert triage interactions
├── templates/
│   ├── base.html              # Core layout template
│   ├── index.html             # Main Dashboard
│   ├── logs.html              # Ingestion & Data Grid
│   ├── alerts.html            # Alert Triage Queue
│   ├── investigate.html       # Incident Deep-Dive View
│   ├── ip_analysis.html       # IP Intelligence Table
│   └── mitre.html             # MITRE ATT&CK Matrix View
└── tests/
    ├── test_detection.py      # Detection engine unit tests
    ├── test_api.py            # API integration tests
    └── test_live_server.py    # Live server verification script
```

---

## 🛠️ Installation & Quick Start

### 1. Clone & Setup Environment
```bash
git clone <repository-url>
cd "ai project"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m unittest discover tests
```

### 4. Launch Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🧪 Sample Attack Scenarios Included

When you click **"Load Sample Data"** on the dashboard, the application populates the following realistic attack scenarios into SQLite:

1. **Admin Brute Force Attack**:
   - IP `198.51.100.44` executes 8 consecutive failed logins against user `admin` within 2 minutes before gaining access.
   - *Resulting Alert*: `ALT-BF-1985110044-admin` (High Severity, T1110.001).

2. **Password Spraying Campaign**:
   - IP `203.0.113.88` attempts logins against 8 different corporate user accounts (`user1` through `user8`).
   - *Resulting Alert*: `ALT-SPRAY-203011388` (Critical Severity, T1110.003).

3. **Impossible Travel Anomaly**:
   - User `johndoe` logs in from New York at 10:00:00, then logs in from Tokyo at 10:10:05.
   - *Resulting Alert*: `ALT-TRAVEL-johndoe` (Critical Severity, T1078).

4. **Off-Hours / TOR Node Egress**:
   - IP `185.220.101.5` (TOR Exit Node) attempts authentication at 03:04:00 AM UTC.
   - *Resulting Alert*: `ALT-SUSP-IP-1852201015-root` (High Severity, T1090).

---

## 🖼️ Screenshots & UI Overview

- **Dashboard**: High-level KPIs, 24-hour activity line chart, threat severity doughnut, top attack vectors.
- **Security Alerts**: Filterable alert queue with quick triage actions (`NEW` -> `INVESTIGATING` -> `RESOLVED`).
- **Incident Investigation**: Detailed timeline view with automated SOC analyst rationale explanations.
- **IP Intelligence**: Profiling table displaying dynamic risk scores (0–100) and failure ratio bars.
- **MITRE ATT&CK Matrix**: Educational cards linking detected behaviors to official MITRE techniques.

---

## 🚀 Future Enhancements
- Integration with live syslog / Windows Event Log receivers (UDP/TCP syslog standard).
- Rule builder UI allowing analysts to define custom threshold rules without modifying code.
- Automated email / Slack webhook alerts for Critical incidents.
- Support for GeoIP map visualization using Leaflet.js.
