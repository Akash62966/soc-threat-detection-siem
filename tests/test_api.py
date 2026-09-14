import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.db import init_db, clear_all_data

class TestFlaskEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_db()
        clear_all_data()

    def tearDown(self):
        clear_all_data()

    def test_dashboard_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SOC Threat Detection', response.data)

    def test_pages_routes(self):
        for route in ['/logs', '/alerts', '/ip-analysis', '/mitre']:
            res = self.app.get(route)
            self.assertEqual(res.status_code, 200)

    def test_sample_data_loading_api(self):
        res = self.app.post('/api/load-sample-data')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('inserted_logs', data)
        self.assertTrue(data['inserted_logs'] > 0)

    def test_chart_data_api(self):
        # Load sample data first
        self.app.post('/api/load-sample-data')
        res = self.app.get('/api/chart-data')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('timeline', data)
        self.assertIn('severity', data)

    def test_kpis_api(self):
        res = self.app.get('/api/kpis')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('total_logins', data)

if __name__ == '__main__':
    unittest.main()
