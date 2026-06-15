import argparse
import numpy as np
import joblib
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, calibration_curve
from sklearn.model_selection import train_test_split

def evaluate_classifier(data_dir, model_path, output_dir):
    """
    Evaluates the trained model.
    Generates plots for ROC and Calibration.
    """
    model_file = Path(model_path)
    if not model_file.exists():
         # Try default
         model_file = Path("data/models/classifier_latest.joblib")
    
    if not model_file.exists():
        print("Model not found.")
        return

    print(f"Loading {model_file}...")
    clf = joblib.load(model_file)
    
    # Load Data
    X = np.load(Path(data_dir) / "X.npy")
    y = np.load(Path(data_dir) / "y.npy")
    
    # Ideally use a separate test set, but for this script we just split off a chunk
    # (Assuming train_classifier used a distinct split or we just want to verify behavior)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Evaluating on {len(X_test)} samples...")
    
    probs = clf.predict_proba(X_test)[:, 1]
    preds = (probs > 0.5).astype(int)
    
    # Metrics
    print("\nClassification Report:")
    print(classification_report(y_test, preds, target_names=["Real", "Fake"]))
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds))
    
    # Plots
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    # ROC
    fpr, tpr, _ = roc_curve(y_test, probs)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title('ROC Curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend()
    
    # Calibration Curve
    prob_true, prob_pred = calibration_curve(y_test, probs, n_bins=10)
    
    plt.subplot(1, 2, 2)
    plt.plot(prob_pred, prob_true, marker='o', label='Classifier')
    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
    plt.title('Calibration Curve')
    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.legend()
    
    plot_file = out_path / "evaluation_plots.png"
    plt.tight_layout()
    plt.savefig(plot_file)
    print(f"\nPlots saved to {plot_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/processed")
    parser.add_argument("--model_path", type=str, default="data/models/classifier_latest.joblib")
    parser.add_argument("--output_dir", type=str, default="data/evaluation")
    args = parser.parse_args()
    
    evaluate_classifier(args.data_dir, args.model_path, args.output_dir)
