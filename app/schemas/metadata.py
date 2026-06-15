from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ExifData(BaseModel):
    make: Optional[str] = Field(None, description="Camera manufacturer")
    model: Optional[str] = Field(None, description="Camera model")
    software: Optional[str] = Field(None, description="Software used to process the image")
    datetime_original: Optional[str] = Field(None, description="Original timestamp")
    exposure_time: Optional[str] = Field(None, description="Exposure time")
    f_number: Optional[float] = Field(None, description="F-stop")
    iso: Optional[int] = Field(None, description="ISO speed")
    lens_model: Optional[str] = Field(None, description="Lens model")

class AnalysisResult(BaseModel):
    authenticity_score: float = Field(..., ge=0, le=100, description="Confidence score 0-100")
    flags: List[str] = Field(default_factory=list, description="Detected warning flags")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed analysis breakdown")

class MetadataResponse(BaseModel):
    filename: str
    exif: ExifData
    analysis: AnalysisResult
