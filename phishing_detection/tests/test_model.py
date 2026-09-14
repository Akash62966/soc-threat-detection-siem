import unittest
import os
import sys
import joblib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from feature_extraction import get_feature_vector

class TestModelInference(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        model_path = os.path.join(base_dir, "model", "phishing_model.joblib")
        scaler_path = os.path.join(base_dir, "model", "scaler.joblib")
        cls.model = joblib.load(model_path)
        cls.scaler = joblib.load(scaler_path)

    def test_legitimate_url_prediction(self):
        url = "https://www.google.com/search?q=python"
        vec = get_feature_vector(url)
        vec_scaled = self.scaler.transform([vec])
        pred = self.model.predict(vec_scaled)[0]
        self.assertEqual(pred, 0)  # 0 = Legitimate

    def test_phishing_url_prediction(self):
        url = "http://192.168.1.1/login-banking-security-update/@verify"
        vec = get_feature_vector(url)
        vec_scaled = self.scaler.transform([vec])
        pred = self.model.predict(vec_scaled)[0]
        self.assertEqual(pred, 1)  # 1 = Phishing

if __name__ == '__main__':
    unittest.main()
