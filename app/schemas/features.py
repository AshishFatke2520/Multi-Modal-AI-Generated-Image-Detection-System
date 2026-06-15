from pydantic import BaseModel, Field
from typing import List, Optional

class FeatureExtractionResponse(BaseModel):
    filename: str
    model_name: str
    embedding_dim: int
    embedding: List[float] = Field(..., description="Normalized feature embedding vector.")
    cache_hit: bool
    extraction_time_ms: float
    device: str
