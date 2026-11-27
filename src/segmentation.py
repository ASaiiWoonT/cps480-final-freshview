"""Extract a tight RGB crop using a detector mask aligned to the original."""
import numpy as np
from PIL import Image


def extract_crop(image, mask):
    if mask.shape != (image.height, image.width):
        raise ValueError("Detector mask dimensions differ from input image.")
    binary = Image.fromarray(np.uint8(mask > 0.5) * 255)
    bounds = binary.getbbox()
    if bounds is None:
        raise ValueError("Detector returned an empty mask.")
    region = image.crop(bounds)
    background = Image.new("RGB", region.size, (128, 128, 128))
    crop = Image.composite(region, background, binary.crop(bounds))
    return binary, bounds, crop
