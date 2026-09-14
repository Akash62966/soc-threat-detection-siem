import urllib.request
import json
import time

base_url = "http://127.0.0.1:5050"

def test_endpoints():
    endpoints = ['/', '/logs', '/alerts', '/ip-analysis', '/mitre', '/api/kpis', '/api/chart-data']
    for ep in endpoints:
        req = urllib.request.urlopen(base_url + ep)
        print(f"Endpoint {ep} -> Status {req.status}")
        assert req.status == 200

if __name__ == "__main__":
    print("Testing live endpoints...")
    test_endpoints()
    print("All live endpoints OK!")
