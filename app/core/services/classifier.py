import joblib
import numpy as np
import logging
import json
from pathlib import Path
from typing import Optional

MODEL_PATH = Path("data/models/classifier_latest.joblib")
META_PATH = Path("data/models/classifier_latest_meta.json")

class AIClassifier:
    """
    Service wrapper for the trained Logistic Regression model.
    Provides calibrated probabilities for AI generation.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIClassifier, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.metadata = {}
            cls._instance.logger = logging.getLogger(__name__)
            cls._instance.load_model()
        return cls._instance
    
    def load_model(self):
        """Loads the model from disk if available."""
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                self.logger.info(f"Classifier loaded from {MODEL_PATH}")
                
                if META_PATH.exists():
                    with open(META_PATH, "r") as f:
                        self.metadata = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load classifier: {e}")
                self.model = None
        else:
            self.logger.warning(f"Classifier model not found at {MODEL_PATH}. Inference will return indeterminate results.")
            self.model = None

    def predict_proba(self, embedding: np.ndarray) -> float:
        """
        Predicts the probability that the image is AI-generated.
        
        Args:
           embedding: 1D numpy array of shape (512,) from CLIP.
           
        Returns:
           float: Probability [0.0, 1.0]. Returns 0.5 if model not loaded.
        """
        if self.model is None:
            return 0.5
            
        try:
            # Reshape for single sample
            vec = embedding.reshape(1, -1)
            # [:, 1] is the probability of class 1 (Fake)
            prob = self.model.predict_proba(vec)[0][1]
            return float(prob)
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return 0.5

    def get_metadata(self) -> dict:
        return self.metadata

# Global
classifier_service = AIClassifier()
