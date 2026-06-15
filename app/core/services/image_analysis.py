import os
import io
import time
import logging
import numpy as np
import cv2
from PIL import Image, ImageFile, UnidentifiedImageError
from scipy import fftpack

# Secure loading settings
ImageFile.LOAD_TRUNCATED_IMAGES = False  # Strict loading
MAX_IMAGE_PIXELS = 178956970  # Standard Pillow limit (~178MP), or set lower for safety
MAX_FILE_SIZE_MB = 25

class ImageArtifactAnalyzer:
    """
    Analyzes images for digital manipulation artifacts using deterministic computer vision techniques.
    Focuses on compression anomalies and frequency domain irregularities.
    """
    
    def __init__(self):   #it is a constructor
        self.logger = logging.getLogger(__name__)

    def load_and_validate(self, image_path: str) -> tuple[Image.Image, np.ndarray, dict]:
        """
        Loads an image securely, validates constraints, and returns PIL and OpenCV formats.
         
        Args:
           image_path: Absolute path to the image file.
           
        Returns:
           pil_image: Loaded PIL Image object (converted to RGB).
           cv_image: Loaded OpenCV image (BGR format).
           info: Dictionary containing basic file info.
           
        Raises:
           ValueError: If validation fails (size, corruption, type).
        """
        # 1. File Size Check
        file_size = os.path.getsize(image_path)
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File size {file_size} exceeds limit of {MAX_FILE_SIZE_MB}MB")

        try:
            # 2. Secure PIL Loading
            # Open without loading raster data first to check metadata/size
            with Image.open(image_path) as img:
                if img.format not in ["JPEG", "PNG", "WEBP", "TIFF"]:
                    raise ValueError(f"Unsupported format: {img.format}")
                
                # Check dimensions to prevent decompression bombs
                # Pillow has a default LIMIT, but we verify explicitly if needed or rely on its internal check
                if (img.width * img.height) > MAX_IMAGE_PIXELS:
                    raise ValueError("Image dimensions too large (potential decompression bomb)")

                # 3. Validation & Conversion
                # Copy to memory to detach from file and force full load/verification
                img_copy = img.copy()
                img_copy.verify()  # Check for integrity
                
                # Re-open for actual processing (verify consumes the file pointer)
                img.close()
            
            # Re-load for usage
            pil_image = Image.open(image_path)
            pil_image.load() # Force load pixel data
            
            # Convert to standard RGB to normalize handling
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
                
            # Create OpenCV version (RGB -> BGR)
            # Convert PIL to numpy array
            img_np = np.array(pil_image)
            # Convert RGB to BGR for OpenCV
            cv_image = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            info = {
                "format": pil_image.format,
                "mode": pil_image.mode,
                "size": pil_image.size
            }
            
            return pil_image, cv_image, info

        except UnidentifiedImageError:
            raise ValueError("Cannot identify image file. Possible corruption.")
        except Exception as e:
            raise ValueError(f"Image loading failed: {str(e)}")

    def analyze_compression(self, pil_image: Image.Image) -> dict:
        """
        Analyzes compression artifacts, specifically for JPEGs.
        """
        metrics = {
            "quantization_tables_found": False,
            "quality_estimate": None,
            "double_compression_detected": False,
            "blockiness_score": 0.0,
            "details": {}
        }

        # 1. Quantization Table Analysis (JPEG only)
        if pil_image.format == 'JPEG' or hasattr(pil_image, 'quantization'):
            try:
                qtables = pil_image.quantization
                if qtables:
                    metrics["quantization_tables_found"] = True
                    # Heuristic: Estimate quality from luminance table (table 0)
                    # Standard JPEG tables scale. Lower values = higher quality.
                    # This is a rough estimator.
                    if 0 in qtables:
                        # Average of a few low-freq coefficients is a rough proxy
                        avg_q = np.mean(qtables[0])
                        # Rough mapping: 50 -> ~50, 1 -> ~100. 
                        # This isn't perfect but gives a signal.
                        metrics["quality_estimate"] = max(0, min(100, 100 - avg_q + 50)) # Very rough
                    
                    metrics["details"]["qtables_count"] = len(qtables)
            except Exception:
                pass

        # 2. Blockiness Detection (Grid Artifacts)
        # Convert to grayscale for analysis
        gray = np.array(pil_image.convert('L'))
        
        # Calculate strict 8x8 block boundary differences vs internal differences
        # Rows
        h, w = gray.shape
        # We need dimensions to be multiples of 8 for a clean check, or just crop
        h_crop = h - (h % 8)
        w_crop = w - (w % 8)
        gray_crop = gray[:h_crop, :w_crop]

        # Differences between pixels
        # Axis 0 = vertical diffs, Axis 1 = horizontal diffs
        # We look for consistently higher differences at indices 7, 15, 23... (0-indexed -> 8th pixel boundary)
        
        # Horizontal boundaries (rows 8, 16...)
        row_diffs = np.abs(np.diff(gray_crop, axis=0))
        # Sum across columns
        row_diff_sum = np.sum(row_diffs, axis=1)
        
        # Vertical boundaries (cols 8, 16...)
        col_diffs = np.abs(np.diff(gray_crop, axis=1))
        col_diff_sum = np.sum(col_diffs, axis=0)

        # Signal at boundaries
        row_boundaries = row_diff_sum[7::8]
        row_non_boundaries = np.delete(row_diff_sum, np.arange(7, row_diff_sum.shape[0], 8))
        
        col_boundaries = col_diff_sum[7::8]
        col_non_boundaries = np.delete(col_diff_sum, np.arange(7, col_diff_sum.shape[0], 8))
        
        # Calculate ratio of mean boundary energy to mean non-boundary energy
        # Avoid division by zero
        rb_mean = np.mean(row_boundaries) if row_boundaries.size > 0 else 0
        rnb_mean = np.mean(row_non_boundaries) if row_non_boundaries.size > 0 else 1
        
        cb_mean = np.mean(col_boundaries) if col_boundaries.size > 0 else 0
        cnb_mean = np.mean(col_non_boundaries) if col_non_boundaries.size > 0 else 1

        # A strong JPEG has B > NB.
        blockiness = ((rb_mean / rnb_mean) + (cb_mean / cnb_mean)) / 2.0
        
        # Normalize: > 1.0 implies blockiness. Map 1.0->0.0, 1.5->0.5, 2.0->1.0 (clamped)
        # This is strictly heuristic.
        normalized_blockiness = max(0.0, min(1.0, (blockiness - 1.0) * 2))
        
        metrics["blockiness_score"] = float(normalized_blockiness)
        
        # 3. Double Compression Signatures
        # High blockiness but low quantization values (high quality metadata) suggests mismatch
        if metrics["quality_estimate"] and metrics["quality_estimate"] > 90 and normalized_blockiness > 0.3:
            metrics["double_compression_detected"] = True
            metrics["details"]["reason"] = "High quality metadata but significant block artifacts."

        return metrics

    def analyze_frequency(self, cv_image: np.ndarray) -> dict:
        """
        Performs FFT analysis to detect frequency anomalies.
        """
        metrics = {
            "high_freq_ratio": 0.0,
            "anomalous_peaks_detected": False,
            "noise_distribution_score": 0.0,
            "details": {}
        }
        
        img_gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        h, w = img_gray.shape
        
        # 1. FFT
        f = np.fft.fft2(img_gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
        
        # 2. Spectral Energy Ratio
        # Calculate energy in center (low freq) vs outer (high freq)
        cy, cx = h // 2, w // 2
        # Radius for "low frequency"
        radius = min(h, w) // 8
        
        y, x = np.ogrid[:h, :w]
        mask_area = (x - cx)**2 + (y - cy)**2 <= radius**2
        
        total_energy = np.sum(magnitude_spectrum)
        low_freq_energy = np.sum(magnitude_spectrum[mask_area])
        high_freq_energy = total_energy - low_freq_energy
        
        if total_energy > 0:
            metrics["high_freq_ratio"] = float(high_freq_energy / total_energy)
        
        # 3. Anomalous Peak Detection (Checkerboard artifacts detection)
        # AI generated images (GANs) often have specific peaks in the spectrum.
        # We search for bright spots in the high-frequency range that shouldn't be there naturally.
        # Normalize spectrum 0-1
        spec_norm = cv2.normalize(magnitude_spectrum, None, 0, 1, cv2.NORM_MINMAX)
        
        # Threshold to find peaks
        _, thresh = cv2.threshold(spec_norm, 0.95, 1, cv2.THRESH_BINARY)
        
        # Count peaks in high freq area
        # Invert mask to get high freq area
        high_freq_mask = ~mask_area
        peaks_in_high_freq = np.sum(thresh[high_freq_mask])
        
        # Heuristic: Natural images rarely have super distinct high energy peaks far from center
        # unless there's a strong periodic pattern (text, fence, etc).
        # We flag if count is high.
        if peaks_in_high_freq > 10: # Arbitrary threshold needs tuning
            metrics["anomalous_peaks_detected"] = True
            metrics["details"]["peak_count"] = int(peaks_in_high_freq)

        # 4. Noise Distribution (Azimuthal Integration) - Simplified
        # Natural images have isotropic decay usually.
        # If we take the average magnitude at each radius, it should approximate 1/f.
        # We can implement a simple check of the slope, but keeping it simple for now:
        # Just use the high_freq_ratio as a noise score proxy.
        # Too much high freq energy often means noise or AI artifacts (sometimes).
        # Too little means over-smoothed (like median filter).
        
        # Score: 0 (Normal) to 1 (Abnormal). 
        # Assume typical ratio is around 0.3-0.6 depending on content.
        # Extreme values are suspicious.
        dist_from_05 = abs(metrics["high_freq_ratio"] - 0.4)
        metrics["noise_distribution_score"] = min(1.0, dist_from_05 * 2)

        return metrics

    def compute_artifact_score(self, compression: dict, frequency: dict) -> tuple[float, str, list]:
        """
        Combines metrics into a final score (0-100).
        0 = Clean/Natural, 100 = Highly Artifacted/Suspicious
        """
        score = 0.0
        flags = []
        
        # Weightings
        # Blockiness: +30 max
        score += compression["blockiness_score"] * 30
        if compression["blockiness_score"] > 0.5:
            flags.append("High blockiness detected")
            
        # Double Compression: +20
        if compression["double_compression_detected"]:
            score += 20
            flags.append("Potential double compression")
            
        # Frequency Anomalies: +30
        if frequency["anomalous_peaks_detected"]:
            score += 30
            flags.append("Anomalous frequency peaks (possible generation artifacts)")
            
        # Noise Distribution: +20
        # If noise is very abnormal
        score += frequency["noise_distribution_score"] * 20
        
        score = min(100.0, max(0.0, score))
        
        level = "Low"
        if score > 30: level = "Medium"
        if score > 60: level = "High"
        
        return score, level, flags
