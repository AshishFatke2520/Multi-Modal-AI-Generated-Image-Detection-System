import argparse
import numpy as np
import joblib
import json
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import brier_score_loss, log_loss

def train_classifier(data_dir, model_dir):
    """
    Trains a Logistic Regression model on X.npy and y.npy.
    Applies Platt Scaling (CalibratedClassifierCV).
    Saves model and metadata.
    """
    data_path = Path(data_dir)
    model_path = Path(model_dir)
    model_path.mkdir(parents=True, exist_ok=True)
    
    # Load data
    try:
        X = np.load(data_path / "X.npy")
        y = np.load(data_path / "y.npy")
    except FileNotFoundError:
        print(f"Data not found in {data_dir}. Run prepare_dataset.py first.")
        return

    print(f"Loaded {X.shape[0]} samples. Class balance: {np.mean(y):.2f} (1=Fake)")

    # Split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 1. Base Model: Logistic Regression
    # We use L2 penalty (Ridge) by default. Class weight balanced handles imbalance.
    base_clf = LogisticRegression(C=1.0, class_weight='balanced', solver='lbfgs', max_iter=1000)
    
    # 2. Calibration Wrapper
    # method='sigmoid' is Platt Scaling. method='isotonic' is non-parametric (needs more data).
    # cv='prefit' would mean we trained base_clf outside. 
    # cv=5 means it splits X_train again to train base and calibrator safely.
    calibrated_clf = CalibratedClassifierCV(base_clf, method='sigmoid', cv=5)
    
    print("Training calibrated classifier...")
    calibrated_clf.fit(X_train, y_train)
    
    # Evaluate on Val
    probs = calibrated_clf.predict_proba(X_val)[:, 1]
    brier = brier_score_loss(y_val, probs)
    loss = log_loss(y_val, probs)
    print(f"Validation Brier Score: {brier:.4f}")
    print(f"Validation Log Loss: {loss:.4f}")
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"classifier_v1_{timestamp}.joblib"
    save_path = model_path / model_filename
    
    # We create a symlink or standardized name 'latest.joblib' for the service to pick up easier
    latest_path = model_path / "classifier_latest.joblib"
    
    joblib.dump(calibrated_clf, save_path)
    joblib.dump(calibrated_clf, latest_path) # Overwrite latest
    
    # Save Metadata
    metadata = {
        "model_type": "LogisticRegression + CalibratedClassifierCV(sigmoid)",
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "brier_score": brier,
        "log_loss": loss,
        "features": "CLIP ViT-B/32",
        "timestamp": timestamp
    }
    
    with open(model_path / "classifier_latest_meta.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Model saved to {save_path} and {latest_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/processed")
    parser.add_argument("--model_dir", type=str, default="data/models")
    args = parser.parse_args()
    
    train_classifier(args.data_dir, args.model_dir)
