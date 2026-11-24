"""Decode uploaded images without trusting the filename extension."""
import warnings

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 20_000_000


def read_image(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_BYTES:
        raise ValueError("Each image must be 10 MB or smaller.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(file) as image:
                if image.format not in {"JPEG", "PNG"}:
                    raise ValueError("Please upload a JPEG or PNG image.")
                if image.width * image.height > MAX_PIXELS:
                    raise ValueError("Please resize this image to 20 megapixels or smaller.")
                return ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as error:
        raise ValueError("This file could not be read as an image.") from error
