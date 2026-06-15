import os
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import sys

# Add project root to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.services.clip_extractor import clip_extractor

def prepare_dataset(data_dir, output_dir, dry_run=False):
    """
    Scans data_dir for 'real' and 'fake' subfolders.
    Extracts CLIP embeddings.
    Saves X.npy, y.npy, and metadata.
    """
    data_path = Path(data_dir)
    real_path = data_path / "real"
    fake_path = data_path / "fake"
    
    if not real_path.exists() or not fake_path.exists():
        print(f"Error: Directory structure not found. Expected {real_path} and {fake_path}")
        # Create dummy data if dry run
        if dry_run:
            print("DRY RUN: Creating dummy embeddings...")
            X = np.random.rand(100, 512).astype(np.float32)
            y = np.array([0]*50 + [1]*50)
            paths = [f"dummy_real_{i}.jpg" for i in range(50)] + [f"dummy_fake_{i}.jpg" for i in range(50)]
            
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            np.save(output_path / "X.npy", X)
            np.save(output_path / "y.npy", y)
            pd.DataFrame({"path": paths, "label": y}).to_csv(output_path / "metadata.csv", index=False)
            print(f"Saved dummy dataset to {output_dir}")
            return

        return

    image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".tiff"}
    
    records = []
    vectors = []
    
    print("Loading model...")
    clip_extractor.load_model()
    
    for label, folder in [(0, real_path), (1, fake_path)]:
        files = [f for f in folder.iterdir() if f.suffix.lower() in image_extensions]
        print(f"Processing {len(files)} files in {folder}...")
        
        for f in tqdm(files):
            try:
                # Extract
                result = clip_extractor.extract_embedding(str(f))
                vectors.append(result["embedding"])
                records.append({
                    "path": str(f),
                    "label": label,
                    "filename": f.name
                })
            except Exception as e:
                print(f"Failed {f}: {e}")
                
    if not vectors:
        print("No vectors extracted.")
        return

    X = np.array(vectors)
    y = np.array([r["label"] for r in records])
    
    print(f"Dataset shape: {X.shape}")
    
    # Save
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    np.save(out_path / "X.npy", X)
    np.save(out_path / "y.npy", y)
    pd.DataFrame(records).to_csv(out_path / "metadata.csv", index=False)
    
    print(f"Saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/dataset", help="Root data dir containing 'real' and 'fake'")
    parser.add_argument("--output_dir", type=str, default="data/processed", help="Output dir for .npy files")
    parser.add_argument("--dry-run", action="store_true", help="Generate dummy data if folders missing")
    args = parser.parse_args()
    
    prepare_dataset(args.data_dir, args.output_dir, args.dry_run)
