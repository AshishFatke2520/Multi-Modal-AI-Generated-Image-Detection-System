import shutil
import os
import tempfile
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.services.metadata import metadata_analyzer
from app.core.services.image_analysis import ImageArtifactAnalyzer
from app.core.services.clip_extractor import clip_extractor
from app.core.services.classifier import classifier_service
from app.core.services.signal_fusion import fusion_engine
from app.schemas.metadata import MetadataResponse
from app.schemas.artifacts import ArtifactAnalysisResult
from app.schemas.features import FeatureExtractionResponse
from app.schemas.fusion import FusionResponse, FusionBreakdown
from app.api.deps import get_current_user
from fastapi import Depends

router = APIRouter()
artifact_analyzer = ImageArtifactAnalyzer()

# Helper for temp file handling
def save_upload_to_temp(file: UploadFile) -> str:
    suffix = os.path.splitext(file.filename)[1] # It extracts the file extension (like .jpg, .png) from the original filename
    if not suffix or len(suffix) > 10: suffix = ".tmp" # If the file has no extension or the extension is too long, it will be saved as a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp) # It copies the uploaded file to the temporary file
        return tmp.name



#                   /metadata API   
@router.post("/metadata", response_model=MetadataResponse)
async def analyze_metadata(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    tmp_path = save_upload_to_temp(file)
    try:
        raw_metadata = metadata_analyzer.extract_metadata(tmp_path)
        analysis_result = metadata_analyzer.analyze_consistency(raw_metadata)
        exif_data = metadata_analyzer.parse_to_schema(raw_metadata)

        return MetadataResponse(
            filename=file.filename,
            exif=exif_data,
            analysis=analysis_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)






#                   /artifacts API
@router.post("/artifacts", response_model=ArtifactAnalysisResult)
async def analyze_artifacts(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    tmp_path = save_upload_to_temp(file)
    start_time = time.time()
    try:
        pil_image, cv_image, info = artifact_analyzer.load_and_validate(tmp_path)
        compression_metrics = artifact_analyzer.analyze_compression(pil_image)
        frequency_metrics = artifact_analyzer.analyze_frequency(cv_image)
        score, level, flags = artifact_analyzer.compute_artifact_score(compression_metrics, frequency_metrics)
        
        return ArtifactAnalysisResult(
            filename=file.filename,
            is_valid_image=True,
            format=info.get("format", "UNKNOWN"),
            dimensions=info.get("size", (0, 0)),
            compression_analysis=compression_metrics,
            frequency_analysis=frequency_metrics,
            overall_artifact_score=score,
            suspicion_level=level,
            flags=flags,
            processing_time_ms=(time.time() - start_time) * 1000
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Artifact analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass



#               /features API
@router.post("/features", response_model=FeatureExtractionResponse)
async def extract_features(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    tmp_path = save_upload_to_temp(file)
    try:
        result = clip_extractor.extract_embedding(tmp_path)
        
        return FeatureExtractionResponse(
            filename=file.filename,
            model_name="ViT-B-32",
            embedding_dim=len(result["embedding"]),
            embedding=result["embedding"].tolist(),
            cache_hit=result["cache_hit"],
            extraction_time_ms=result["time_ms"],
            device=result["device"]
        )
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass

from app.core.services.explainer import explanation_engine



#           /fusion API 
@router.post("/fusion", response_model=FusionResponse)
async def analyze_fusion(file: UploadFile = File(...), explain: bool = False):
    """
    Orchestrate full analysis pipeline: Metadata -> Artifacts -> features/Classifier -> Fusion.
    Returns a unified suspicion score with explanation.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff", "image/webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    tmp_path = save_upload_to_temp(file)
    start_time = time.time()
    try:
        # ... [Previous steps remain same] ... 
        # For brevity in this replacement I will duplicate the logic structure but condensed
        # Metadata logic...
        raw_metadata = metadata_analyzer.extract_metadata(tmp_path)
        meta_result = metadata_analyzer.analyze_consistency(raw_metadata)
        # Convert authenticity score (0-100, higher is "Authentic") to suspicion (0.0-1.0, higher is "Suspicious")
        metadata_suspicion = (100.0 - meta_result.authenticity_score) / 100.0
        
        # Artifacts logic
        pil_image, cv_image, _ = artifact_analyzer.load_and_validate(tmp_path)
        comp_metrics = artifact_analyzer.analyze_compression(pil_image)
        freq_metrics = artifact_analyzer.analyze_frequency(cv_image)
        artifact_score, _, _ = artifact_analyzer.compute_artifact_score(comp_metrics, freq_metrics)
        
        # Classifier logic
        feat_result = clip_extractor.extract_embedding(tmp_path)
        embedding = feat_result["embedding"]
        classifier_prob = classifier_service.predict_proba(embedding)
        
        # Fusion
        fusion_result = fusion_engine.aggregate(
            metadata_suspicion=metadata_suspicion,
            artifact_score_raw=artifact_score,
            classifier_prob=classifier_prob
        )
        
        verdict = "Low"
        score = fusion_result["final_score"]
        if score > 30: verdict = "Medium"
        if score > 70: verdict = "High"

        # Check for fusion_result having extra fields not matching schema exact? No, it matches FusionBreakdown.
        # But we need to add verdict to the dict we pass to explainer.
        fusion_data_for_explainer = fusion_result.copy()
        fusion_data_for_explainer['verdict'] = verdict

        # Explanation
        explanation = None
        if explain:
            explanation = explanation_engine.generate_explanation(fusion_data_for_explainer)

        # Save to History
        from app.core.database import db
        from datetime import datetime
        
        history_record = {
            "user_id": "guest_user",
            "filename": file.filename,
            "timestamp": datetime.utcnow(),
            "verdict": verdict,
            "final_score": score,
            "breakdown": fusion_result,
            "explanation": explanation.dict() if explanation else None
        }
        await db.db.history.insert_one(history_record)

        return FusionResponse(
            filename=file.filename,
            final_score=score,
            verdict=verdict,
            breakdown=FusionBreakdown(**fusion_result),
            explanation=explanation,
            processing_time_ms=(time.time() - start_time) * 1000
        )

    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Fusion analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass
