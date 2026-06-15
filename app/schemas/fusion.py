from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class RawSignalScores(BaseModel):
    metadata_score: Optional[float] = Field(None, description="Metadata consistency score (0-1.0)")
    artifact_score: Optional[float] = Field(None, description="Artifact analysis score (0-100.0, to be normalized)")
    classifier_score: Optional[float] = Field(None, description="Classifier probability (0-1.0)")

class FusionBreakdown(BaseModel):
    normalized_scores: Dict[str, float] = Field(..., description="Scores normalized to 0-1 range")
    weights_used: Dict[str, float] = Field(..., description="Weights applied to each signal")
    uncertainty: float = Field(..., description="Estimated uncertainty (0-1.0)")
    conflicts: List[str] = Field(..., description="Detected conflicts between signals")

class ExplanationResponse(BaseModel):
    explanation_text: str = Field(..., description="Natural language summary of the findings.")
    confidence_label: str = Field(..., description="Semantic confidence level.")
    key_factors: List[str] = Field(default_factory=list, description="Bulleted list of main drivers.")
    uncertainty_notes: Optional[str] = Field(None, description="Notes on why the model is uncertain.")
    llm_model_version: str = Field("gemini-1.5-flash", description="Model used for generation.")
    generation_time_ms: float

class FusionResponse(BaseModel):
    filename: str
    final_score: float = Field(..., description="Final aggegated probability (0-100)")
    verdict: str = Field(..., description="Low, Medium, High suspicion")
    breakdown: FusionBreakdown
    explanation: Optional[ExplanationResponse] = Field(None, description="Optional LLM-generated explanation.")
    processing_time_ms: float
