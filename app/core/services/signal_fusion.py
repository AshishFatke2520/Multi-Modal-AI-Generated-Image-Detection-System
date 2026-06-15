import logging
import numpy as np
from typing import Dict, List, Tuple
from app.core.config import settings

class SignalFusionEngine:
    """
    Deterministically combines multiple probabilistic signals into a final verdict.
    """
    
    def __init__(self):
        self.weights = {
            "metadata": settings.WEIGHT_METADATA,
            "artifacts": settings.WEIGHT_ARTIFACTS,
            "classifier": settings.WEIGHT_CLASSIFIER
        }
        self.logger = logging.getLogger(__name__)

    def normalize_signals(self, 
                          metadata_prob: float = None, 
                          artifact_score: float = None, 
                          classifier_prob: float = None) -> Dict[str, float]:
        """
        Normalizes all inputs to [0.0, 1.0] range where 1.0 = FAKE/SUSPICIOUS.
        """
        scores = {}
        
        # Metadata Prob: 0.0=Fake, 1.0=Real (usually). So we invert it?
        # WAIT: In previous steps, metadata returned a "consistency score".
        # Let's assume MetadataAnalyzer returns a "Real Probability".
        # If so, Suspicion = 1.0 - Real_Prob.
        # Checking implementation: metadata.py analyze_consistency returns dict.
        # We need to map that to a scalar. For now, let's assume valid=low suspicion.
        # If 'likelihood' is in metadata, use it.
        # For this engine, we expect inputs to already be vaguely "score-like".
        
        if metadata_prob is not None:
            # If input is "Probability of Real", invert.
            # If input is "Suspicion", keep.
            # Convention: We will pass "Suspicion Score" here. 
            scores["metadata"] = max(0.0, min(1.0, float(metadata_prob)))
            
        if artifact_score is not None:
             # Artifact score is 0-100. Normalize to 0-1.
            scores["artifacts"] = max(0.0, min(1.0, float(artifact_score) / 100.0))
            
        if classifier_prob is not None:
            # Classifier returns "Probability of Fake".
            scores["classifier"] = max(0.0, min(1.0, float(classifier_prob)))
            
        return scores

    def detect_conflicts(self, scores: Dict[str, float]) -> List[str]:
        conflicts = []
        if not scores:
            return conflicts
        
        values = list(scores.values())
        if len(values) < 2:
            return conflicts

        # 1. High Variance Check
        variance = np.var(values)
        if variance > 0.15: # Arbitrary threshold
            conflicts.append("High variance between signals")

        # 2. Polarity Conflict (One very high, one very low)
        max_val = max(values)
        min_val = min(values)
        if max_val > 0.8 and min_val < 0.2:
            conflicts.append("Strong polarity conflict (High vs Low signal)")

        return conflicts

    def aggregate(self, 
                  metadata_suspicion: float = None, 
                  artifact_score_raw: float = None, 
                  classifier_prob: float = None) -> Dict:
        
        # 1. Normalize
        norm_scores = self.normalize_signals(metadata_suspicion, artifact_score_raw, classifier_prob)
        
        if not norm_scores:
            return {
                "final_score": 0.0, 
                "uncertainty": 1.0, 
                "breakdown": {}, 
                "conflicts": ["No signals provided"]
            }

        # 2. Dynamic Weighting (Handle missing signals)
        active_weights = {k: self.weights.get(k, 0.33) for k in norm_scores.keys()}
        total_weight = sum(active_weights.values())
        
        if total_weight == 0:
             final_score = 0.0
        else:
            # 3. Weighted Average
            weighted_sum = sum(norm_scores[k] * active_weights[k] for k in norm_scores)
            final_score = weighted_sum / total_weight

        # 4. Uncertainty Estimation
        # Base uncertainty is inversely proportional to number of signals
        base_uncertainty = 1.0 - (len(norm_scores) / 3.0) 
        
        # Add uncertainty from variance
        variance_uncertainty = 0.0
        if len(norm_scores) > 1:
            variance_uncertainty = np.std(list(norm_scores.values()))
            
        total_uncertainty = min(1.0, base_uncertainty + variance_uncertainty)

        # 5. Conflict Detection
        conflicts = self.detect_conflicts(norm_scores)
        
        # 6. Adjust for Conflicts (Prioritize Fake Signal to minimize False Negatives)
        if conflicts:
            # If any signal (like the classifier) strongly indicates FAKE, don't let clean metadata hide it
            max_suspicion = max(norm_scores.values())
            if max_suspicion > 0.7:
                final_score = max(final_score, max_suspicion)

        return {
            "final_score": float(final_score * 100.0), # Scale to 0-100
            "uncertainty": float(total_uncertainty),
            "normalized_scores": {k: float(v) for k, v in norm_scores.items()},
            "weights_used": {k: float(active_weights[k]/total_weight) for k in active_weights},
            "conflicts": conflicts
        }

fusion_engine = SignalFusionEngine()
