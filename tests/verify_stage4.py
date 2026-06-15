import requests
import sys
import os
import time

def test_features(image_path):
    url = "http://127.0.0.1:8000/api/v1/analyze/features"
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    print(f"--- Run 1: Cold start (should compute) ---")
    start = time.time()
    try:
        with open(image_path, "rb") as f:
            resp = requests.post(url, files={"file": f})
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"Success! Time: {time.time() - start:.2f}s")
            print(f"Embedding Dim: {data['embedding_dim']}")
            print(f"Cache Hit: {data['cache_hit']}")
            print(f"Device: {data['device']}")
            
            # Run 2
            print(f"\n--- Run 2: Hot cache (should be fast) ---")
            start = time.time()
            with open(image_path, "rb") as f:
                resp2 = requests.post(url, files={"file": f})
            data2 = resp2.json()
            print(f"Success! Time: {time.time() - start:.2f}s")
            print(f"Cache Hit: {data2['cache_hit']}")
            
            if data2['cache_hit'] == True:
                print("PASS: Cache working.")
            else:
                print("FAIL: Cache not hit on second run.")
                
            # Compare embeddings (just first few elements)
            emb1 = data['embedding'][:5]
            emb2 = data2['embedding'][:5]
            print(f"\nEmbedding Head Run 1: {emb1}")
            print(f"Embedding Head Run 2: {emb2}")
            
        else:
            print(f"Failed: {resp.status_code} {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_stage4.py <image_path>")
    else:
        test_features(sys.argv[1])
