import argparse
import pandas as pd
import json
from pathlib import Path

def run_failure_analysis(scores_file, output_dir):
    """
    Identifies False Positives and False Negatives.
    Generates a report highlighting the worst offenders.
    """
    scores_path = Path(scores_file)
    if not scores_path.exists():
        print(f"Scores file not found: {scores_path}")
        return

    out_path = Path(output_dir) / "failures"
    out_path.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(scores_path)
    
    # Identify Failures
    # False Positive: Label=0 (Real), Score > 0.5
    # False Negative: Label=1 (Fake), Score <= 0.5
    
    fps = df[(df['label'] == 0) & (df['final_score'] > 0.5)].sort_values('final_score', ascending=False)
    fns = df[(df['label'] == 1) & (df['final_score'] <= 0.5)].sort_values('final_score', ascending=True)
    
    print(f"Found {len(fps)} False Positives and {len(fns)} False Negatives.")
    
    # Generate Report
    report_file = out_path / "failure_report.md"
    
    with open(report_file, "w") as f:
        f.write("# Failure Analysis Report\n\n")
        
        f.write("## 1. Top False Positives (Real images flagged as Fake)\n")
        f.write("These are real images that the system incorrectly flagged as suspicious. High priority for review.\n\n")
        
        for idx, row in fps.head(10).iterrows():
            f.write(f"### {row['filename']}\n")
            f.write(f"- **Score**: {row['final_score']:.3f}\n")
            f.write(f"- **Metadata Suspicion**: {row.get('metadata_suspicion', 'N/A')}\n")
            f.write(f"- **Artifact Score**: {row.get('artifact_score', 'N/A')}\n")
            f.write(f"- **Classifier Prob**: {row.get('classifier_prob', 'N/A')}\n\n")
            
        f.write("\n## 2. Top False Negatives (Fake images flagged as Real)\n")
        f.write("These are AI-generated images that bypassed detection.\n\n")
        
        for idx, row in fns.head(10).iterrows():
            f.write(f"### {row['filename']}\n")
            f.write(f"- **Score**: {row['final_score']:.3f}\n")
            f.write(f"- **Metadata Suspicion**: {row.get('metadata_suspicion', 'N/A')}\n")
            f.write(f"- **Artifact Score**: {row.get('artifact_score', 'N/A')}\n")
            f.write(f"- **Classifier Prob**: {row.get('classifier_prob', 'N/A')}\n\n")
            
    print(f"Failure report saved to {report_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores_file", type=str, default="data/evaluation/scores.csv")
    parser.add_argument("--output_dir", type=str, default="data/evaluation")
    args = parser.parse_args()
    
    run_failure_analysis(args.scores_file, args.output_dir)
