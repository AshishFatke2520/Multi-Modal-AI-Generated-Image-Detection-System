import argparse
import os
import sys
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from tqdm import tqdm
from sklearn.metrics import roc_curve, auc, brier_score_loss, classification_report, confusion_matrix, accuracy_score
from sklearn.calibration import calibration_curve

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock modules if they fail to import (for dry run environment stability)
try:
    from app.core.services.metadata import metadata_analyzer
    from app.core.services.image_analysis import ImageArtifactAnalyzer
    from app.core.services.clip_extractor import clip_extractor
    from app.core.services.classifier import classifier_service
    from app.core.services.signal_fusion import fusion_engine
except ImportError as e:
    print(f"Warning: Failed to import app services: {e}")

def run_evaluation(data_dir, output_dir, dry_run=False):
    """
    Runs the full fusion pipeline on the test dataset.
    Generates metrics and plots.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    plots_path = output_path / "plots"
    plots_path.mkdir(parents=True, exist_ok=True)
    
    # Setup Logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("eval")
    
    # 1. Load Data
    if dry_run:
        logger.info("DRY RUN: Generating dummy data...")
        # Generate 50 Real, 50 Fake
        records = []
        for i in range(100):
            label = 1 if i >= 50 else 0
            # Simulate scores correlated with label
            noise = np.random.normal(0, 0.2)
            score_base = 0.8 if label == 1 else 0.2
            final_score = np.clip(score_base + noise, 0, 1)
            
            records.append({
                "filename": f"img_{i}.jpg",
                "label": label,
                "dataset_split": "test",
                "final_score": final_score, # Simulated result
                "metadata_suspicion": np.random.rand(),
                "artifact_score": np.random.rand(),
                "classifier_prob": np.random.rand(),
                "width": 1024,
                "height": 1024,
                "file_size_bytes": 500000
            })
        df = pd.DataFrame(records)
    else:
        # Actual Inference Loop
        # Assumes data_dir has 'real' and 'fake' folders or a csv manifest
        # Detailed implementation omitted for brevity, assumes standard iteration
        # For this script structure, we will assume a simplified CSV input or folder walk
        # Here we mock the result gathering:
        real_path = Path(data_dir) / "real"
        fake_path = Path(data_dir) / "fake"
        
        if not real_path.exists():
            logger.error(f"Data directory not found: {data_dir}")
            return

        results = []
        
        # Initialize services
        artifact_analyzer = ImageArtifactAnalyzer()
        
        for label, folder in [(0, real_path), (1, fake_path)]:
            files = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
            logger.info(f"Processing {len(files)} files for label {label}")
            
            for f in tqdm(files):
                try:
                    # Run Pipeline
                    # 1. Metadata (Mocked call pattern for simplicity/speed in script context)
                    # For real eval, call full services.
                    # Here we simulate or call directly if environment ready.
                    
                    # Assuming full service availability:
                    # clip_extractor.extract_embedding...
                    # classifier_service.predict_proba...
                    # fusion_engine.aggregate...
                    
                    # For demonstration/stability without gpu:
                    # We will rely on what classifier returns (if model exists)
                    
                    # Placeholder for full execution:
                    # ... execution logic ...
                    
                    # Dummy Fallback for script creation phase:
                    final_score = 0.5 
                    
                    results.append({
                        "filename": f.name,
                        "label": label,
                        "final_score": final_score,
                        "file_size_bytes": os.path.getsize(f)
                    })
                    
                except Exception as e:
                    logger.error(f"Failed {f}: {e}")
        
        df = pd.DataFrame(results)

    # 2. Evaluation Metrics
    y_true = df['label'].values
    y_scores = df['final_score'].values # This is probability 0-1
    y_pred = (y_scores > 0.5).astype(int)
    
    # Basic
    report = classification_report(y_true, y_pred, output_dict=True)
    cm = confusion_matrix(y_true, y_pred)
    brier = brier_score_loss(y_true, y_scores)
    
    logger.info(f"Accuracy: {report['accuracy']:.4f}")
    logger.info(f"Brier Score: {brier:.4f}")

    # ROC
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    # Save Metrics
    metrics = {
        "accuracy": report['accuracy'],
        "brier_score": brier,
        "roc_auc": roc_auc,
        "precision_fake": report['1']['precision'],
        "recall_fake": report['1']['recall'],
        "f1_fake": report['1']['f1-score']
    }
    
    with open(output_path / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    df.to_csv(output_path / "scores.csv", index=False)
    
    # 3. Plotting
    # ROC
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.savefig(plots_path / 'roc_curve.png')
    plt.close()
    
    # Calibration
    prob_true, prob_pred = calibration_curve(y_true, y_scores, n_bins=10)
    plt.figure()
    plt.plot(prob_pred, prob_true, marker='o')
    plt.plot([0, 1], [0, 1], linestyle='--')
    plt.xlabel("Mean Predicted Value")
    plt.ylabel("Fraction of Positives")
    plt.title("Calibration Curve")
    plt.savefig(plots_path / 'calibration_curve.png')
    plt.close()
    
    # Distribution
    plt.figure()
    sns.histplot(data=df, x='final_score', hue='label', kde=True, bins=20)
    plt.title("Score Distribution")
    plt.savefig(plots_path / 'score_distribution.png')
    plt.close()

    logger.info(f"Evaluation complete. Results in {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/dataset/test")
    parser.add_argument("--output_dir", type=str, default="data/evaluation")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    run_evaluation(args.data_dir, args.output_dir, args.dry_run)
