"""Day 1 interface stub. No condition predictions are available yet."""
from PIL import Image


def analyze_image(image):
    valid = isinstance(image, Image.Image) and image.mode == "RGB"
    return {
        "status": "not_ready" if valid else "invalid_image",
        "produce_type": None,
        "detection_confidence": None,
        "segmented_image": None,
        "condition_probabilities": None,
        "processing_time_ms": None,
        "error": ("Model integration and condition training are pending."
                  if valid else "Expected a PIL RGB image."),
    }
