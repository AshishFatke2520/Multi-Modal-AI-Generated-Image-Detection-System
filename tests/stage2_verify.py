import os
import io
from fastapi.testclient import TestClient
from PIL import Image
import piexif
from app.main import app

client = TestClient(app)

def create_test_image(add_software_tag=False):
    # Create valid JPEG
    img = Image.new('RGB', (100, 100), color = 'red')
    
    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    if add_software_tag:
        exif_dict["0th"][piexif.ImageIFD.Software] = "Adobe Photoshop Generative Fill"

    exif_bytes = piexif.dump(exif_dict)
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif_bytes)
    buf.seek(0)
    return buf

def test_metadata_analysis_clean():
    img_buf = create_test_image(add_software_tag=False)
    response = client.post(
        "/api/v1/analyze/metadata",
        files={"file": ("clean_test.jpg", img_buf, "image/jpeg")}
    )
    print(f"Clean Image Response Code: {response.status_code}")
    print(f"Clean Image JSON: {response.json()}")
    assert response.status_code == 200
    assert response.json()["analysis"]["authenticity_score"] > 0

def test_metadata_analysis_software():
    img_buf = create_test_image(add_software_tag=True)
    response = client.post(
        "/api/v1/analyze/metadata",
        files={"file": ("edited_test.jpg", img_buf, "image/jpeg")}
    )
    print(f"Edited Image Response Code: {response.status_code}")
    print(f"Edited Image JSON: {response.json()}")
    assert response.status_code == 200
    assert "Adobe Photoshop" in str(response.json()["analysis"]["details"])

if __name__ == "__main__":
    try:
        test_metadata_analysis_clean()
        test_metadata_analysis_software()
        print("Stage 2 Tests Passed!")
    except Exception as e:
        print(f"Tests Failed: {e}")
        exit(1)
