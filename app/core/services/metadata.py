import os
from typing import Dict, Any, List, Optional
from PIL import Image # It is used to open and process the image file
import piexif # It is used to extract EXIF data from the image file
from app.schemas.metadata import ExifData, AnalysisResult # It is used to define the schema for the metadata

class MetadataAnalyzer:
    """
    Analyzes image metadata to detect signs of AI generation or manipulation.
    Focuses on EXIF data consistency, software tags, and missing fields.
    """
    # made an Array of known editing software
    KNOWN_EDITING_SOFTWARE = [
        "Adobe Photoshop", "GIMP", "Lightroom", "Paint.NET", "Affinity Photo"
    ]
    
    # Critical EXIF tags usually present in genuine camera photos
    # 271: Make, 272: Model, 306: DateTime, 36867: DateTimeOriginal
    # 33434: ExposureTime, 33437: FNumber, 34855: ISOSpeedRatings


    # made an object of critical tags
    CRITICAL_TAGS = {
        "Make", "Model", "DateTimeOriginal", "ExposureTime", "FNumber", "ISOSpeedRatings"
    }





    # a function to extract metadata from an image
    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extracts raw EXIF data using piexif and converts it to a readable dictionary.
        Handles missing EXIF gracefully.
        """
        try:
            img = Image.open(image_path)
            exif_dict = piexif.load(img.info.get("exif", b"")) # It loads the EXIF data from the image file # piexif is a library that is used to extract EXIF data from the image file
        except Exception:
            return {}

        readable_exif = {}
        
        # 0th IFD (Image)
        for tag, value in exif_dict.get("0th", {}).items():
            tag_name = piexif.TAGS["0th"].get(tag, {}).get("name", str(tag))
            readable_exif[tag_name] = self._clean_value(value)

        # Exif IFD
        for tag, value in exif_dict.get("Exif", {}).items():
            tag_name = piexif.TAGS["Exif"].get(tag, {}).get("name", str(tag))
            readable_exif[tag_name] = self._clean_value(value)

        # GPS IFD
        if exif_dict.get("GPS"):
             readable_exif["GPS"] = "Present" # Simplified for presence check

        return readable_exif




    # a function to clean the metadata
    def _clean_value(self, value: Any) -> Any:
        # Helper to decode bytes to string
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8").strip('\x00')
            except UnicodeDecodeError:
                return str(value)
        return value




    # a function to analyze the metadata
    def analyze_consistency(self, metadata: Dict[str, Any]) -> AnalysisResult:
        """
        Analyzes the extracted metadata for inconsistencies and assigns a score.
        """
        score = 100.0
        flags = []
        details = {}

        # 1. Check for Software Tag
        software = metadata.get("Software", "")
        if software:
            details["software_detected"] = software
            for tool in self.KNOWN_EDITING_SOFTWARE:
                if tool.lower() in software.lower():
                    score -= 30
                    flags.append(f"Edited with {tool}")
                    break
            else:
                 # Reduce score slightly for any software tag as it implies processing
                 score -= 10
                 flags.append(f"Processed with software: {software}")

        # 2. Check for Missing Critical Tags
        missing_tags = []
        for tag in self.CRITICAL_TAGS:
            if tag not in metadata:
                missing_tags.append(tag)
        
        if missing_tags:
            penalty = len(missing_tags) * 15
            score -= penalty
            flags.append(f"Missing critical camera tags: {', '.join(missing_tags)}")
            details["missing_tags"] = missing_tags

        # 3. AI Generation Indicators (Heuristic)
        # Many AI generators strip all metadata or leave specific signatures
        if not metadata:
             score = 50 # High uncertainty if no metadata, could be stripped or AI
             flags.append("No metadata found")
        
        # Clamp score
        score = max(0.0, min(100.0, score))

        return AnalysisResult(
            authenticity_score=score,
            flags=flags,
            details=details
        )
    




    
    # a function to parse the metadata to a schema
    def parse_to_schema(self, metadata: Dict[str, Any]) -> ExifData:
        return ExifData(
            make=metadata.get("Make"),
            model=metadata.get("Model"),
            software=metadata.get("Software"),
            datetime_original=metadata.get("DateTimeOriginal"),
            exposure_time=str(metadata.get("ExposureTime")) if metadata.get("ExposureTime") else None,
            f_number=float(metadata.get("FNumber")) if metadata.get("FNumber") else None,
            iso=int(metadata.get("ISOSpeedRatings")) if metadata.get("ISOSpeedRatings") else None,
            lens_model=metadata.get("LensModel")
        )

# Singleton instance for easy import
metadata_analyzer = MetadataAnalyzer()
