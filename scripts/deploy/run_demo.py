import argparse
import requests
import sys
import json
import os

API_URL = "http://127.0.0.1:8000/api/v1/analyze/fusion"

def run_demo(image_path, explain=True):
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    print(f"--- DeepMediaCheck Demo ---")
    print(f"Target: {image_path}")
    print(f"Connecting to: {API_URL}")
    print("Uploading and Analyzing...\n")

    try:
        url = f"{API_URL}?explain={str(explain).lower()}"
        with open(image_path, "rb") as f:
            response = requests.post(url, files={"file": f})
        
        if response.status_code != 200:
            print(f"Failed: {response.status_code}")
            print(response.text)
            return

        result = response.json()
        
        # Pretty Print Output
        print(f"=== ANALYSIS RESULT ===")
        print(f"Filename: {result.get('filename')}")
        print(f"Score:    {result.get('final_score', 0):.1f} / 100")
        print(f"Verdict:  {result.get('verdict')}")
        print("-" * 20)
        
        breakdown = result.get('breakdown', {})
        print(f"Signals:")
        for k, v in breakdown.get('normalized_scores', {}).items():
            print(f"  - {k}: {v:.2f}")
            
        print("-" * 20)
        
        if result.get('explanation'):
            expl = result['explanation']
            print(f"\n[AI Explanation]:\n{expl['explanation_text']}")
            print(f"\nConfidence: {expl['confidence_label']}")
        
        print("\n=== END DEMO ===")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is start_local.bat running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DeepMediaCheck Demo")
    parser.add_argument("--image", type=str, required=True, help="Path to image file")
    parser.add_argument("--no-explain", action="store_true", help="Disable LLM explanation")
    
    args = parser.parse_args()
    
    run_demo(args.image, explain=not args.no_explain)
