import requests
import sys
import os
import json

def test_fusion(image_path):
    url = "http://127.0.0.1:8000/api/v1/analyze/fusion"
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    print(f"Testing Fusion on {image_path}...")
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(url, files={"file": f})
        
        if resp.status_code == 200:
            data = resp.json()
            print("SUCCESS")
            print(json.dumps(data, indent=2))
            
            # Basic assertions
            if "final_score" in data and "breakdown" in data:
                print("PASS: Structure valid")
            else:
                print("FAIL: Missing keys")
        else:
            print(f"Failed: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_stage6.py <image_path>")
    else:
        test_fusion(sys.argv[1])
