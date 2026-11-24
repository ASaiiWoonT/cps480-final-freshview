from io import BytesIO

from PIL import Image
import pytest
from streamlit.testing.v1 import AppTest

from src.config import ROOT
from src.images import read_image
from src.pipeline import analyze_image


def test_rgba_upload_becomes_independent_rgb_image():
    buffer = BytesIO()
    Image.new("RGBA", (16, 12), (40, 60, 80, 255)).save(buffer, format="PNG")
    decoded = read_image(buffer)
    buffer.close()
    assert decoded.mode == "RGB" and decoded.size == (16, 12)
    assert decoded.getpixel((0, 0)) == (40, 60, 80)


def test_corrupt_upload_is_rejected():
    with pytest.raises(ValueError, match="could not be read"):
        read_image(BytesIO(b"not an image"))


def test_oversized_upload_is_rejected():
    with pytest.raises(ValueError, match="10 MB"):
        read_image(BytesIO(b"x" * (10 * 1024 * 1024 + 1)))


def test_untrained_pipeline_does_not_fabricate_predictions():
    result = analyze_image(Image.new("RGB", (16, 16)))
    assert result["status"] == "not_ready"
    assert result["condition_probabilities"] is None
    assert analyze_image(None)["status"] == "invalid_image"


def test_app_starts_without_models_or_uploads():
    app = AppTest.from_file(str(ROOT / "app" / "streamlit_app.py")).run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "FreshView"
    assert app.button[0].disabled
