import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from feature_extraction import extract_features_from_url, get_feature_vector, explain_features

class TestFeatureExtraction(unittest.TestCase):

    def test_legitimate_url_features(self):
        url = "https://www.wikipedia.org/wiki/Main_Page"
        feats = extract_features_from_url(url)

        self.assertEqual(feats["has_https"], 1)
        self.assertEqual(feats["has_ip"], 0)
        self.assertEqual(feats["at_symbol_count"], 0)
        self.assertEqual(feats["num_subdomains"], 1)  # www

    def test_phishing_url_features(self):
        url = "http://192.168.1.1/login-banking-security-update/@verify"
        feats = extract_features_from_url(url)

        self.assertEqual(feats["has_https"], 0)
        self.assertEqual(feats["has_ip"], 1)
        self.assertTrue(feats["at_symbol_count"] >= 1)
        self.assertTrue(feats["suspicious_keyword_count"] >= 3)  # login, banking, verify

    def test_explain_features(self):
        url = "http://192.168.1.1/login-banking-security-update/@verify"
        explanations = explain_features(url)
        self.assertTrue(len(explanations) > 0)
        self.assertTrue(any("IP address" in e for e in explanations))

if __name__ == '__main__':
    unittest.main()
