# MITRE ATT&CK Framework Mapping Helper
# Defensive Educational Mapping for SOC Threat Detection

MITRE_TECHNIQUES = {
    "BRUTE_FORCE": {
        "id": "T1110.001",
        "name": "Brute Force: Password Guessing",
        "tactic": "Credential Access",
        "url": "https://attack.mitre.org/techniques/T1110/001/",
        "description": "Adversaries may attempt to systematically guess passwords of targeted accounts to gain initial access or escalate privileges."
    },
    "PASSWORD_SPRAY": {
        "id": "T1110.003",
        "name": "Brute Force: Password Spraying",
        "tactic": "Credential Access",
        "url": "https://attack.mitre.org/techniques/T1110/003/",
        "description": "Adversaries may attempt a single common password against many different accounts to avoid account lockouts."
    },
    "IMPOSSIBLE_TRAVEL": {
        "id": "T1078",
        "name": "Valid Accounts: Abnormal Location / Travel",
        "tactic": "Defense Evasion / Initial Access",
        "url": "https://attack.mitre.org/techniques/T1078/",
        "description": "Adversaries may obtain and use credentials of existing valid accounts. Sequential logins from geographically distant locations within an impossible timeframe indicate credential abuse."
    },
    "UNUSUAL_TIME": {
        "id": "T1078.004",
        "name": "Valid Accounts: Cloud Accounts / Off-Hours Logins",
        "tactic": "Initial Access",
        "url": "https://attack.mitre.org/techniques/T1078/004/",
        "description": "Logins occurring outside normal business operating hours or during maintenance windows may signal unauthorized access or compromised service credentials."
    },
    "SUSPICIOUS_IP": {
        "id": "T1090",
        "name": "Proxy: Anonymizing Network / Known Malicious IP",
        "tactic": "Command and Control / Initial Access",
        "url": "https://attack.mitre.org/techniques/T1090/",
        "description": "Adversaries may route traffic through anonymizing proxies, TOR nodes, or compromised infrastructure to mask source origin during authentication attempts."
    },
    "ML_ANOMALY": {
        "id": "T1078.003",
        "name": "Valid Accounts: Anomaly Behavior Outlier",
        "tactic": "Persistence / Privilege Escalation",
        "url": "https://attack.mitre.org/techniques/T1078/003/",
        "description": "Machine learning detection identifies statistical outliers in login frequency, time-of-day distributions, and failure density comparing user baseline vs current events."
    }
}

def get_mitre_mapping(attack_type):
    return MITRE_TECHNIQUES.get(attack_type, {
        "id": "T1078",
        "name": "Valid Accounts",
        "tactic": "Initial Access",
        "url": "https://attack.mitre.org/techniques/T1078/",
        "description": "General credential or authentication misuse."
    })

def get_all_mitre_matrix():
    return list(MITRE_TECHNIQUES.values())
