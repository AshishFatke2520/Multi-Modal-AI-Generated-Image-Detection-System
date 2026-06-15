
#  This is a Clip Model that is used to extract features from images using OpenCLIP 
# No need to get deep knowlege of it, as it is pretrained model


import os
import torch
import open_clip
import hashlib
import json
import logging
import numpy as np
import time
from PIL import Image
from pathlib import Path

# Constants
CACHE_DIR = Path("data/embeddings")
MODEL_NAME = "ViT-B-32"
PRETRAINED = "laion2b_s34b_b79k"  # Good balance of speed/performance

class CLIPFeatureExtractor:
    """
    Extracts semantic feature embeddings from images using a pre-trained CLIP model.
    Uses caching to avoid re-computing embeddings for the same file content.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CLIPFeatureExtractor, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.preprocess = None
            cls._instance.device = None
            cls._instance.logger = logging.getLogger(__name__)
            
            # Ensure cache directory exists
            if not CACHE_DIR.exists():
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                
        return cls._instance

    def load_model(self):
        """
        Lazy loads the CLIP model. 
        """
        if self.model is not None:
            return

        self.logger.info(f"Loading CLIP model: {MODEL_NAME} ({PRETRAINED})...")
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                MODEL_NAME, 
                pretrained=PRETRAINED, 
                device=self.device
            )
            self.model.eval()  # Set to evaluation mode
            
            # Freeze parameters just to be safe (though torch.no_grad handles memory mostly)
            for param in self.model.parameters():
                param.requires_grad = False
                
            self.logger.info(f"Model loaded on {self.device}")
        except Exception as e:
            self.logger.error(f"Failed to load user-specified CLIP model: {e}")
            raise RuntimeError(f"Could not load CLIP model: {e}")

    def _compute_hash(self, image_path: str) -> str:
        """Compute SHA256 hash of the file content for caching."""
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _get_cache_path(self, file_hash: str) -> Path:
        return CACHE_DIR / f"{file_hash}_{MODEL_NAME}.json"

    def extract_embedding(self, image_path: str) -> dict:
        """
        Extracts embedding for a single image, using cache if available.
        Returns dictionary with embedding, cache status, etc.
        """
        start_time = time.time()
        
        # 1. Check Cache
        file_hash = self._compute_hash(image_path)
        cache_path = self._get_cache_path(file_hash)
        
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    cached_data = json.load(f)
                    # Basic versioning check could be added here
                    if cached_data.get("model") == MODEL_NAME:
                        return {
                            "embedding": np.array(cached_data["embedding"]), # Return as numpy
                            "cache_hit": True,
                            "time_ms": (time.time() - start_time) * 1000,
                            "device": "cache"
                        }
            except Exception as e:
                self.logger.warning(f"Cache read failed, re-computing: {e}")

        # 2. Compute
        self.load_model() # Ensure loaded
        
        try:
            image = Image.open(image_path).convert("RGB")
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                
            # Normalize
            image_features /= image_features.norm(dim=-1, keepdim=True)
            
            # Convert to list for storage/return
            embedding_list = image_features.cpu().numpy()[0].tolist()
            
            # 3. Save Cache
            result = {
                "embedding": embedding_list,
                "model": MODEL_NAME,
                "version": "1.0"
            }
            with open(cache_path, "w") as f:
                json.dump(result, f)
                
            return {
                "embedding": np.array(embedding_list),
                "cache_hit": False,
                "time_ms": (time.time() - start_time) * 1000,
                "device": self.device
            }
            
        except Exception as e:
            self.logger.error(f"Inference failed: {e}")
            raise RuntimeError(f"CLIP inference failed: {e}")

# Global instance
clip_extractor = CLIPFeatureExtractor()
