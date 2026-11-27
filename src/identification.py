"""Identify and isolate a single instance of the project's supported produce."""
from time import perf_counter

from PIL import Image

from src.config import ROOT, load_config
from src.runtime import configure_cache, select_device
from src.segmentation import extract_crop


class ProduceDetector:
    def __init__(self, device="auto"):
        configure_cache()
        from ultralytics import YOLO

        settings = load_config()["identification"]
        classes = load_config("classes")
        self.device = select_device(device)
        self.model = YOLO(str(ROOT / settings["model"]))
        self.confidence = settings["confidence_threshold"]
        self.candidates = set(classes["recognition_candidates"])
        self.supported = set(classes["supported_produce"])

    def analyze(self, image):
        start = perf_counter()
        output = dict(produce_type=None, detection_confidence=None, mask=None,
                      crop_box=None, segmented_image=None, condition_probabilities=None)

        def finish(status, error=None):
            return dict(output, status=status, error=error,
                        processing_time_ms=round((perf_counter() - start) * 1000, 1))

        if not isinstance(image, Image.Image) or image.mode != "RGB" or min(image.size) < 1:
            return finish("invalid_image", "Expected a nonempty PIL RGB image.")
        result = self.model.predict(image, device=self.device, conf=self.confidence,
                                    imgsz=640, retina_masks=True, verbose=False)[0]
        candidates = []
        for index, box in enumerate(result.boxes):
            name = result.names[int(box.cls.item())]
            if name in self.candidates:
                candidates.append((index, name, float(box.conf.item())))
        if not candidates:
            return finish("no_produce_detected", "No candidate produce detected.")
        if len(candidates) > 1:
            return finish("multiple_objects", "Photograph one produce item at a time.")
        index, name, confidence = candidates[0]
        output.update(produce_type=name, detection_confidence=confidence)
        if name not in self.supported:
            return finish("unsupported_produce", f"Condition assessment does not support {name}.")
        if result.masks is None or index >= len(result.masks.data):
            return finish("segmentation_failed", "Missing instance mask.")
        try:
            mask, bounds, crop = extract_crop(image, result.masks.data[index].cpu().numpy())
        except ValueError as error:
            return finish("segmentation_failed", str(error))
        output.update(mask=mask, crop_box=bounds, segmented_image=crop)
        return finish("segmented")
