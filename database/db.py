import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "siem.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            username TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            event_type TEXT NOT NULL,
            status TEXT NOT NULL,
            user_agent TEXT,
            location TEXT,
            failure_reason TEXT,
            ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT UNIQUE NOT NULL,
            timestamp DATETIME NOT NULL,
            source_ip TEXT NOT NULL,
            username TEXT NOT NULL,
            attack_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'NEW',
            mitre_tactic TEXT,
            mitre_technique_id TEXT,
            mitre_technique_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # IP Intelligence Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ip_intel (
            ip_address TEXT PRIMARY KEY,
            total_events INTEGER DEFAULT 0,
            failed_events INTEGER DEFAULT 0,
            risk_score INTEGER DEFAULT 0,
            first_seen DATETIME,
            last_seen DATETIME,
            is_suspicious INTEGER DEFAULT 0,
            threat_tags TEXT
        )
    ''')

    conn.commit()
    conn.close()

def clear_all_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    cursor.execute("DELETE FROM alerts")
    cursor.execute("DELETE FROM ip_intel")
    conn.commit()
    conn.close()

def insert_logs(logs_data):
    """
    logs_data: list of dicts with keys: timestamp, username, source_ip, event_type, status, user_agent, location, failure_reason
    """
    if not logs_data:
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()

    inserted_count = 0
    for item in logs_data:
        # Check duplicate
        cursor.execute('''
            SELECT id FROM logs WHERE timestamp = ? AND username = ? AND source_ip = ? AND event_type = ? AND status = ?
        ''', (item['timestamp'], item['username'], item['source_ip'], item.get('event_type', 'LOGIN'), item['status'].upper()))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO logs (timestamp, username, source_ip, event_type, status, user_agent, location, failure_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['timestamp'],
                item['username'],
                item['source_ip'],
                item.get('event_type', 'LOGIN'),
                item['status'].upper(),
                item.get('user_agent', 'Mozilla/5.0'),
                item.get('location', 'Unknown'),
                item.get('failure_reason', '')
            ))
            inserted_count += 1

    conn.commit()
    conn.close()

    # Update IP Intel summary after inserting logs
    update_ip_intelligence()

    return inserted_count

def update_ip_intelligence():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            source_ip,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed,
            MIN(timestamp) as first_seen,
            MAX(timestamp) as last_seen
        FROM logs
        GROUP BY source_ip
    ''')
    rows = cursor.fetchall()

    for row in rows:
        ip = row['source_ip']
        total = row['total']
        failed = row['failed']
        first_seen = row['first_seen']
        last_seen = row['last_seen']

        failure_rate = (failed / total) * 100 if total > 0 else 0
        risk_score = min(100, int((failed * 10) + (failure_rate * 0.5)))
        is_suspicious = 1 if (failed >= 5 or risk_score >= 50) else 0

        tags = []
        if failed >= 5:
            tags.append("High Failed Volume")
        if failure_rate > 70 and total >= 3:
            tags.append("High Failure Ratio")
        if is_suspicious:
            tags.append("Threat Flagged")

        tag_str = ", ".join(tags) if tags else "Clean"

        cursor.execute('''
            INSERT INTO ip_intel (ip_address, total_events, failed_events, risk_score, first_seen, last_seen, is_suspicious, threat_tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ip_address) DO UPDATE SET
                total_events = excluded.total_events,
                failed_events = excluded.failed_events,
                risk_score = excluded.risk_score,
                first_seen = excluded.first_seen,
                last_seen = excluded.last_seen,
                is_suspicious = excluded.is_suspicious,
                threat_tags = excluded.threat_tags
        ''', (ip, total, failed, risk_score, first_seen, last_seen, is_suspicious, tag_str))

    conn.commit()
    conn.close()

def insert_alert(alert_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    alt_id = alert_data.get('alert_id', f"ALT-{uuid.uuid4().hex[:8].upper()}")
    cursor.execute('''
        SELECT id FROM alerts WHERE alert_id = ? OR (timestamp = ? AND source_ip = ? AND username = ? AND attack_type = ?)
    ''', (alt_id, alert_data['timestamp'], alert_data['source_ip'], alert_data['username'], alert_data['attack_type']))
    
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO alerts (alert_id, timestamp, source_ip, username, attack_type, severity, description, status, mitre_tactic, mitre_technique_id, mitre_technique_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alt_id,
            alert_data['timestamp'],
            alert_data['source_ip'],
            alert_data['username'],
            alert_data['attack_type'],
            alert_data['severity'],
            alert_data['description'],
            alert_data.get('status', 'NEW'),
            alert_data.get('mitre_tactic', 'Credential Access'),
            alert_data.get('mitre_technique_id', 'T1110'),
            alert_data.get('mitre_technique_name', 'Brute Force')
        ))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_logs(limit=100, status=None, username=None, ip=None):
    conn = get_db_connection()
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    if status and status != 'ALL':
        query += " AND status = ?"
        params.append(status.upper())
    if username:
        query += " AND username LIKE ?"
        params.append(f"%{username}%")
    if ip:
        query += " AND source_ip LIKE ?"
        params.append(f"%{ip}%")

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_alerts(severity=None, status=None, limit=100):
    conn = get_db_connection()
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if severity and severity != 'ALL':
        query += " AND severity = ?"
        params.append(severity)
    if status and status != 'ALL':
        query += " AND status = ?"
        params.append(status.upper())

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_alert_status(alert_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET status = ? WHERE alert_id = ? OR id = ?", (new_status.upper(), alert_id, alert_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def get_alert_by_id(alert_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts WHERE alert_id = ? OR id = ?", (alert_id, alert_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_related_logs_for_alert(source_ip, username, alert_timestamp, window_minutes=30):
    """
    Returns logs around the incident timestamp for investigation
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
        SELECT * FROM logs 
        WHERE (source_ip = ? OR username = ?)
        ORDER BY timestamp ASC
    '''
    cursor.execute(query, (source_ip, username))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ip_intel():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ip_intel ORDER BY risk_score DESC, total_events DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_kpis():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM logs")
    total_logins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE status = 'SUCCESS'")
    successful_logins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM logs WHERE status = 'FAILED'")
    failed_logins = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ip_intel WHERE is_suspicious = 1")
    suspicious_ips = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'Critical' AND status = 'NEW'")
    critical_unresolved = cursor.fetchone()[0]

    conn.close()

    return {
        "total_logins": total_logins,
        "successful_logins": successful_logins,
        "failed_logins": failed_logins,
        "total_alerts": total_alerts,
        "suspicious_ips": suspicious_ips,
        "critical_unresolved": critical_unresolved
    }

def get_chart_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Activity by Hour (or date)
    cursor.execute('''
        SELECT 
            substr(timestamp, 1, 13) || ':00' as time_bucket,
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as fail_count
        FROM logs
        GROUP BY time_bucket
        ORDER BY time_bucket ASC
        LIMIT 24
    ''')
    timeline_rows = cursor.fetchall()

    labels = [r['time_bucket'] for r in timeline_rows]
    success_data = [r['success_count'] for r in timeline_rows]
    fail_data = [r['fail_count'] for r in timeline_rows]

    # Threat Severity Distribution
    cursor.execute('''
        SELECT severity, COUNT(*) as cnt 
        FROM alerts 
        GROUP BY severity
    ''')
    severity_rows = cursor.fetchall()
    sev_map = {r['severity']: r['cnt'] for r in severity_rows}
    severity_distribution = {
        'Low': sev_map.get('Low', 0),
        'Medium': sev_map.get('Medium', 0),
        'High': sev_map.get('High', 0),
        'Critical': sev_map.get('Critical', 0)
    }

    # Top Attack Types
    cursor.execute('''
        SELECT attack_type, COUNT(*) as cnt 
        FROM alerts 
        GROUP BY attack_type 
        ORDER BY cnt DESC 
        LIMIT 5
    ''')
    attack_rows = cursor.fetchall()
    attack_types = {r['attack_type']: r['cnt'] for r in attack_rows}

    # Top Flagged IPs
    cursor.execute('''
        SELECT ip_address, risk_score, failed_events 
        FROM ip_intel 
        WHERE is_suspicious = 1 
        ORDER BY risk_score DESC 
        LIMIT 5
    ''')
    ip_rows = cursor.fetchall()
    top_ips = [{"ip": r['ip_address'], "risk": r['risk_score'], "failed": r['failed_events']} for r in ip_rows]

    conn.close()

    return {
        "timeline": {
            "labels": labels,
            "success": success_data,
            "failed": fail_data
        },
        "severity": severity_distribution,
        "attack_types": attack_types,
        "top_ips": top_ips
    }
