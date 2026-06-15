import argparse
import pandas as pd
import json
import logging
from pathlib import Path
from sklearn.metrics import accuracy_score, confusion_matrix

def run_bias_analysis(scores_file, output_dir):
    """
    Analyzes performance differences across subgroups.
    """
    scores_path = Path(scores_file)
    if not scores_path.exists():
        print(f"Scores file not found: {scores_file}")
        return

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(scores_path)
    
    # Define Subgroups
    # 1. Resolution Buckets
    if 'width' in df.columns:
        df['pixels'] = df['width'] * df['height']
        df['res_group'] = pd.cut(df['pixels'], 
                               bins=[0, 1000000, 8000000, float('inf')], 
                               labels=['Low (<1MP)', 'Medium (1-8MP)', 'High (>8MP)'])
    else:
        # Dry run data might not have it or real data might accept defaults
        df['res_group'] = 'Unknown'

    # 2. File Size
    if 'file_size_bytes' in df.columns:
         df['size_group'] = pd.cut(df['file_size_bytes'],
                                 bins=[0, 100000, 1000000, float('inf')],
                                 labels=['Small (<100KB)', 'Medium', 'Large (>1MB)'])

    # Analysis Loop
    groups = ['res_group', 'size_group']
    bias_report = {}
    
    for g in groups:
        if g not in df.columns: continue
        
        print(f"\nAnalyzing Bias by {g}:")
        group_metrics = {}
        
        for name, group in df.groupby(g):
            if len(group) == 0: continue
            
            y_true = group['label']
            y_pred = (group['final_score'] > 0.5).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0,1]).ravel()
            
            acc = accuracy_score(y_true, y_pred)
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
            
            group_metrics[str(name)] = {
                "count": len(group),
                "accuracy": round(acc, 3),
                "fpr": round(fpr, 3),
                "fnr": round(fnr, 3)
            }
            print(f"  {name}: Acc={acc:.2f}, FPR={fpr:.2f}, FNR={fnr:.2f}")
            
        bias_report[g] = group_metrics

    # Save
    with open(out_path / "bias_report.json", "w") as f:
        json.dump(bias_report, f, indent=2)
    
    # Generate Summary Table
    summary_path = out_path / "bias_summary.md"
    with open(summary_path, "w") as f:
        f.write("# Bias Analysis Report\n\n")
        f.write("Evaluation of performance disparities across sample subgroups.\n\n")
        
        for g, metrics in bias_report.items():
            f.write(f"## Group: {g}\n")
            f.write("| Subgroup | Count | Accuracy | FPR (Real as Fake) | FNR (Fake as Real) |\n")
            f.write("|----------|-------|----------|--------------------|--------------------|\n")
            for sub, m in metrics.items():
                f.write(f"| {sub} | {m['count']} | {m['accuracy']} | {m['fpr']} | {m['fnr']} |\n")
            f.write("\n")
            
    print(f"\nBias report saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores_file", type=str, default="data/evaluation/scores.csv")
    parser.add_argument("--output_dir", type=str, default="data/evaluation")
    args = parser.parse_args()
    
    run_bias_analysis(args.scores_file, args.output_dir)
