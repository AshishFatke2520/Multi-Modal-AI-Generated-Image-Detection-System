import requests
import sys
import os
import json

def test_explanation(image_path):
    url = "http://127.0.0.1:8000/api/v1/analyze/fusion?explain=true"
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    print(f"Testing Fusion+Explanation on {image_path}...")
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(url, files={"file": f})
        
        if resp.status_code == 200:
            data = resp.json()
            print("SUCCESS")
            
            # Check for explanation
            if "explanation" in data and data["explanation"]:
                expl = data["explanation"]
                print("\n--- Explanation ---")
                print(f"Text: {expl['explanation_text']}")
                print(f"Confidence: {expl['confidence_label']}")
                print(f"Factors: {expl['key_factors']}")
                print(f"Model: {expl['llm_model_version']}")
            else:
                print("FAIL: Explanation missing or null")
                
        else:
            print(f"Failed: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_stage7.py <image_path>")
    else:
        test_explanation(sys.argv[1])
