import unittest
import pandas as pd
import os
import sys

# Ensure parent directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_db, clear_all_data, insert_logs, get_alerts
from detection.rules import (
    detect_brute_force_and_spray,
    detect_impossible_travel,
    detect_unusual_time,
    detect_suspicious_ips,
    run_rule_engine
)

class TestDetectionEngine(unittest.TestCase):

    def setUp(self):
        init_db()
        clear_all_data()

    def tearDown(self):
        clear_all_data()

    def test_brute_force_detection(self):
        # Create 6 failed logins for user 'test_user' from IP '10.0.0.1' within 5 mins
        logs = []
        for i in range(6):
            logs.append({
                "timestamp": f"2026-09-15 10:0{i}:00",
                "username": "test_user",
                "source_ip": "10.0.0.1",
                "event_type": "LOGIN",
                "status": "FAILED",
                "user_agent": "Mozilla/5.0",
                "location": "Local Lab",
                "failure_reason": "Bad Password"
            })
        
        df = pd.DataFrame(logs)
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        alerts = detect_brute_force_and_spray(df)

        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[0]['attack_type'], "Brute Force Attack")
        self.assertEqual(alerts[0]['severity'], "High")

    def test_impossible_travel_detection(self):
        logs = [
            {
                "timestamp": "2026-09-15 10:00:00",
                "username": "traveler",
                "source_ip": "1.1.1.1",
                "event_type": "LOGIN",
                "status": "SUCCESS",
                "location": "New York US"
            },
            {
                "timestamp": "2026-09-15 10:10:00",
                "username": "traveler",
                "source_ip": "2.2.2.2",
                "event_type": "LOGIN",
                "status": "SUCCESS",
                "location": "Tokyo JP"
            }
        ]
        df = pd.DataFrame(logs)
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        alerts = detect_impossible_travel(df)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['attack_type'], "Impossible Travel Anomaly")
        self.assertEqual(alerts[0]['severity'], "Critical")

    def test_unusual_time_detection(self):
        logs = [{
            "timestamp": "2026-09-15 02:15:00",
            "username": "nightowl",
            "source_ip": "10.0.0.5",
            "event_type": "LOGIN",
            "status": "FAILED",
            "location": "Berlin DE"
        }]
        df = pd.DataFrame(logs)
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        alerts = detect_unusual_time(df)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['attack_type'], "Unusual Time Login Attempt")

    def test_suspicious_ip_detection(self):
        logs = [{
            "timestamp": "2026-09-15 12:00:00",
            "username": "victim",
            "source_ip": "185.220.101.5",
            "event_type": "LOGIN",
            "status": "FAILED",
            "location": "TOR Node Exit"
        }]
        df = pd.DataFrame(logs)
        df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
        alerts = detect_suspicious_ips(df)

        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['attack_type'], "Suspicious IP Indicator")

    def test_end_to_end_rule_engine(self):
        sample_logs = [
            {"timestamp": f"2026-09-15 11:0{i}:00", "username": "admin", "source_ip": "198.51.100.44", "status": "FAILED"} for i in range(6)
        ]
        insert_logs(sample_logs)
        alerts = run_rule_engine()
        self.assertTrue(len(alerts) > 0)
        db_alerts = get_alerts()
        self.assertTrue(len(db_alerts) > 0)

if __name__ == '__main__':
    unittest.main()
