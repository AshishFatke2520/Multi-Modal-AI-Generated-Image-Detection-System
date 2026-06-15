from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CompressionMetrics(BaseModel):
    quantization_tables_found: bool = Field(..., description="Whether JPEG quantization tables were found.")
    quality_estimate: Optional[float] = Field(None, description="Estimated JPEG quality factor (0-100).")
    double_compression_detected: bool = Field(False, description="Flag if double compression signatures are detected.")
    blockiness_score: float = Field(..., description="Measure of blocking artifacts (0.0 to 1.0 scale usually).")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional low-level compression details.")

class FrequencyMetrics(BaseModel):
    high_freq_ratio: float = Field(..., description="Ratio of high frequency energy to total energy.")
    anomalous_peaks_detected: bool = Field(False, description="True if abnormal localized peaks are found in FFT.")
    noise_distribution_score: float = Field(..., description="Score representing the naturalness of noise distribution.")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional frequency domain measurements.")

class ArtifactAnalysisResult(BaseModel):
    filename: str
    is_valid_image: bool
    format: str
    dimensions: tuple[int, int]
    
    compression_analysis: CompressionMetrics
    frequency_analysis: FrequencyMetrics
    
    overall_artifact_score: float = Field(..., description="0-100 score. Higher means more artifacts/suspicious.")
    suspicion_level: str = Field(..., description="Low, Medium, High based on score.")
    
    flags: List[str] = Field(default_factory=list, description="List of specific warning flags raised.")
    
    processing_time_ms: float
