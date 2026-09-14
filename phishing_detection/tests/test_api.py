import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database import init_db, clear_scans

class TestFlaskEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        clear_scans()

    def tearDown(self):
        clear_scans()

    def test_routes_200(self):
        for route in ['/', '/dashboard', '/evaluate', '/dataset']:
            res = self.app.get(route)
            self.assertEqual(res.status_code, 200)

    def test_api_predict_valid_legitimate(self):
        payload = {"url": "https://www.wikipedia.org"}
        res = self.app.post('/api/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("prediction", data)
        self.assertEqual(data["prediction"], "Legitimate")

    def test_api_predict_valid_phishing(self):
        payload = {"url": "http://192.168.1.1/login-banking-security-update/@verify"}
        res = self.app.post('/api/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("prediction", data)
        self.assertEqual(data["prediction"], "Potential Phishing")

    def test_api_predict_empty_input(self):
        payload = {"url": ""}
        res = self.app.post('/api/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_api_kpis(self):
        res = self.app.get('/api/kpis')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("total_scans", data)

if __name__ == '__main__':
    unittest.main()
