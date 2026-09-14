import pandas as pd
from datetime import datetime, timedelta
from database.db import insert_alert
from detection.mitre_mapper import get_mitre_mapping

KNOWN_SUSPICIOUS_INDICATORS = ["tor node", "proxy", "anonymous", "vpn exit", "malicious"]

def run_rule_engine():
    """
    Fetches all logs from database, converts to DataFrame, and runs threat detection rules.
    Returns list of generated alerts.
    """
    from database.db import get_db_connection
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY timestamp ASC", conn)
    conn.close()

    if df.empty:
        return []

    df['timestamp_dt'] = pd.to_datetime(df['timestamp'], errors='coerce')
    generated_alerts = []

    # Rule 1 & 2: Brute Force & Password Spraying
    generated_alerts.extend(detect_brute_force_and_spray(df))

    # Rule 3: Impossible Travel
    generated_alerts.extend(detect_impossible_travel(df))

    # Rule 4: Unusual Time / Off-Hours Logins
    generated_alerts.extend(detect_unusual_time(df))

    # Rule 5: Blacklisted / Suspicious IP Activity
    generated_alerts.extend(detect_suspicious_ips(df))

    # Insert generated alerts into database
    new_alert_count = 0
    for alt in generated_alerts:
        if insert_alert(alt):
            new_alert_count += 1

    return generated_alerts

def detect_brute_force_and_spray(df):
    alerts = []
    failed_df = df[df['status'] == 'FAILED'].copy()
    if failed_df.empty:
        return alerts

    # Check Password Spraying: 1 IP targeting multiple users
    ip_user_counts = failed_df.groupby('source_ip')['username'].nunique()
    for ip, user_cnt in ip_user_counts.items():
        if user_cnt >= 4:
            ip_logs = failed_df[failed_df['source_ip'] == ip]
            latest_time = ip_logs['timestamp'].iloc[-1]
            mitre = get_mitre_mapping("PASSWORD_SPRAY")
            alerts.append({
                "alert_id": f"ALT-SPRAY-{ip.replace('.', '')}",
                "timestamp": latest_time,
                "source_ip": ip,
                "username": f"Multiple ({user_cnt} users)",
                "attack_type": "Password Spraying",
                "severity": "Critical",
                "description": f"Password Spraying detected: Source IP {ip} attempted logins against {user_cnt} distinct user accounts within log window.",
                "mitre_tactic": mitre['tactic'],
                "mitre_technique_id": mitre['id'],
                "mitre_technique_name": mitre['name']
            })

    # Check Brute Force: >= 5 failed attempts per (IP, User) combination within 10-minute window
    grouped = failed_df.groupby(['source_ip', 'username'])
    for (ip, user), group in grouped:
        if len(group) >= 5:
            group = group.sort_values('timestamp_dt')
            # Sliding window check
            timestamps = group['timestamp_dt'].tolist()
            for i in range(len(timestamps) - 4):
                time_window = (timestamps[i+4] - timestamps[i]).total_seconds() / 60.0
                if time_window <= 10:
                    latest_ts = str(group.iloc[i+4]['timestamp'])
                    mitre = get_mitre_mapping("BRUTE_FORCE")
                    alerts.append({
                        "alert_id": f"ALT-BF-{ip.replace('.', '')}-{user}",
                        "timestamp": latest_ts,
                        "source_ip": ip,
                        "username": user,
                        "attack_type": "Brute Force Attack",
                        "severity": "High",
                        "description": f"Brute Force attack detected: {len(group)} failed login attempts from IP {ip} targeting user '{user}' within a 10-minute window.",
                        "mitre_tactic": mitre['tactic'],
                        "mitre_technique_id": mitre['id'],
                        "mitre_technique_name": mitre['name']
                    })
                    break

    return alerts

def detect_impossible_travel(df):
    alerts = []
    # Check for consecutive logins for same user from different countries/locations in < 30 mins
    success_df = df[df['status'] == 'SUCCESS'].copy()
    if success_df.empty:
        return alerts

    grouped = success_df.groupby('username')
    for user, group in grouped:
        if len(group) < 2:
            continue

        group = group.sort_values('timestamp_dt')
        rows = group.to_dict('records')
        for i in range(len(rows) - 1):
            curr = rows[i]
            nxt = rows[i+1]

            t1 = curr['timestamp_dt']
            t2 = nxt['timestamp_dt']
            if pd.isnull(t1) or pd.isnull(t2):
                continue

            time_diff_mins = (t2 - t1).total_seconds() / 60.0
            loc1 = str(curr.get('location', 'Unknown'))
            loc2 = str(nxt.get('location', 'Unknown'))
            ip1 = curr['source_ip']
            ip2 = nxt['source_ip']

            # If locations or IPs differ and time difference is < 30 mins
            if (loc1 != loc2 or ip1 != ip2) and time_diff_mins < 30 and time_diff_mins >= 0:
                mitre = get_mitre_mapping("IMPOSSIBLE_TRAVEL")
                alerts.append({
                    "alert_id": f"ALT-TRAVEL-{user}-{int(t2.timestamp())}",
                    "timestamp": nxt['timestamp'],
                    "source_ip": ip2,
                    "username": user,
                    "attack_type": "Impossible Travel Anomaly",
                    "severity": "Critical",
                    "description": f"Impossible Travel detected for user '{user}': Successful login from '{loc1}' ({ip1}) followed by login from '{loc2}' ({ip2}) in {int(time_diff_mins)} minutes.",
                    "mitre_tactic": mitre['tactic'],
                    "mitre_technique_id": mitre['id'],
                    "mitre_technique_name": mitre['name']
                })

    return alerts

def detect_unusual_time(df):
    alerts = []
    for _, row in df.iterrows():
        ts_dt = row['timestamp_dt']
        if pd.isnull(ts_dt):
            continue

        hour = ts_dt.hour
        status = row['status']
        user = row['username']
        ip = row['source_ip']
        location = row.get('location', 'Unknown')

        # Off-hours: 00:00 to 05:00 UTC and failed status
        if 0 <= hour < 5 and status == 'FAILED':
            mitre = get_mitre_mapping("UNUSUAL_TIME")
            alerts.append({
                "alert_id": f"ALT-TIME-{ip.replace('.', '')}-{user}-{ts_dt.strftime('%H%M%S')}",
                "timestamp": str(row['timestamp']),
                "source_ip": ip,
                "username": user,
                "attack_type": "Unusual Time Login Attempt",
                "severity": "Medium",
                "description": f"Suspicious off-hours failed login attempt for user '{user}' at {row['timestamp']} from {location} ({ip}).",
                "mitre_tactic": mitre['tactic'],
                "mitre_technique_id": mitre['id'],
                "mitre_technique_name": mitre['name']
            })

    return alerts

def detect_suspicious_ips(df):
    alerts = []
    for _, row in df.iterrows():
        location = str(row.get('location', '')).lower()
        ip = row['source_ip']
        user = row['username']
        
        is_suspicious = any(ind in location for ind in KNOWN_SUSPICIOUS_INDICATORS)
        if is_suspicious:
            mitre = get_mitre_mapping("SUSPICIOUS_IP")
            alerts.append({
                "alert_id": f"ALT-SUSP-IP-{ip.replace('.', '')}-{user}",
                "timestamp": str(row['timestamp']),
                "source_ip": ip,
                "username": user,
                "attack_type": "Suspicious IP Indicator",
                "severity": "High",
                "description": f"Authentication attempt originating from high-risk/suspicious node indicator ({row.get('location')}) by IP {ip}.",
                "mitre_tactic": mitre['tactic'],
                "mitre_technique_id": mitre['id'],
                "mitre_technique_name": mitre['name']
            })

    return alerts
