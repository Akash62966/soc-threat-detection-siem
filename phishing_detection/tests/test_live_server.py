import urllib.request
import json

base_url = "http://127.0.0.1:5051"

def test_endpoints():
    endpoints = ['/', '/dashboard', '/evaluate', '/dataset', '/api/kpis']
    for ep in endpoints:
        req = urllib.request.urlopen(base_url + ep)
        print(f"Endpoint {ep} -> Status {req.status}")
        assert req.status == 200

if __name__ == "__main__":
    print("Testing live endpoints for Phishing Detector...")
    test_endpoints()
    print("All live endpoints OK!")
