import requests
import sys
import os

def test_analyze_artifacts(image_path):
    url = "http://127.0.0.1:8000/api/v1/analyze/artifacts"
    
    if not os.path.exists(image_path):
        print(f"Error: File not found {image_path}")
        return

    print(f"Testing {image_path}...")
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            print("SUCCESS")
            data = response.json()
            print(f"  Score: {data['overall_artifact_score']}")
            print(f"  Level: {data['suspicion_level']}")
            print(f"  Flags: {data['flags']}")
            print(f"  Blockiness: {data['compression_analysis']['blockiness_score']:.3f}")
            print(f"  HighFreqRatio: {data['frequency_analysis']['high_freq_ratio']:.3f}")
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_stage3.py <image_path>")
    else:
        test_analyze_artifacts(sys.argv[1])
