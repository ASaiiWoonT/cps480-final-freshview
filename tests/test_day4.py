from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image

from src.identification import ProduceDetector


def detector(classes, masks):
    obj = ProduceDetector.__new__(ProduceDetector)
    obj.device, obj.confidence = "cpu", 0.25
    obj.candidates, obj.supported = {"banana", "apple"}, {"banana"}
    boxes = [SimpleNamespace(cls=np.array(cls), conf=np.array(.9)) for cls in classes]
    data = []
    for array in masks:
        entry = Mock()
        entry.cpu.return_value.numpy.return_value = array
        data.append(entry)
    result = SimpleNamespace(boxes=boxes, names={0:"bird", 1:"banana", 2:"apple"},
                             masks=SimpleNamespace(data=data) if masks else None)
    obj.model = Mock()
    obj.model.predict.return_value = [result]
    return obj


def test_crop_uses_corresponding_mask_and_preserves_dark_pixels():
    image = Image.new("RGB", (6, 5), (41, 27, 8))
    mask = np.zeros((5, 6))
    mask[1:4, 2:5] = 1
    mask[2, 3] = 0
    result = detector([0,1], [1-mask, mask]).analyze(image)
    assert result["status"] == "segmented"
    assert result["mask"].size == image.size and result["crop_box"] == (2,1,5,4)
    assert result["segmented_image"].getpixel((0,0)) == (41,27,8)
    assert result["segmented_image"].getpixel((1,1)) == (128,128,128)
    assert image.getpixel((3,2)) == (41,27,8)
    assert result["condition_probabilities"] is None


@pytest.mark.parametrize("classes,masks,status", [
    ([0], [], "no_produce_detected"), ([2], [], "unsupported_produce"),
    ([1,2], [], "multiple_objects"), ([1], [], "segmentation_failed"),
    ([1], [np.ones((3,3))], "segmentation_failed"),
    ([1], [np.zeros((5,6))], "segmentation_failed"),
])
def test_failure_has_no_crop(classes,masks,status):
    result = detector(classes,masks).analyze(Image.new("RGB",(6,5)))
    assert result["status"] == status and result["segmented_image"] is None
