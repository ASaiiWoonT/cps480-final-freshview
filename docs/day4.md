# Day 4 produce extraction

Team Member 2 can call the extraction stage independently of the condition classifier. Create one detector and reuse it across the uploaded views. Use the existing upload decoder to apply EXIF orientation and obtain a PIL RGB image.

```python
from src.identification import ProduceDetector
from src.images import read_image

detector = ProduceDetector(device="auto")
result = detector.analyze(read_image(upload))
if result["status"] == "segmented":
    crop = result["segmented_image"]  # PIL RGB, cropped to the mask bounds
    mask = result["mask"]             # PIL L, 0/255, full input dimensions
else:
    message = result["error"]
```

The full assessment entry point in src/pipeline.py still returns its Day 1 placeholder until classifier integration. Use the stage status to decide whether to display a crop. Recognition confidence describes the detected produce class. Condition probabilities are unavailable at this stage.

The stage runs YOLO11 Nano Segmentation once per image at input size 640 with the configured confidence threshold (currently 0.25). It counts configured produce candidates, retains the selected instance's original mask index, and accepts a single supported detection (currently banana). Status values include invalid_image, no_produce_detected, multiple_objects, unsupported_produce and segmentation_failed. A detection miss means the model could not identify a candidate in that view. Model-loading and runtime exceptions propagate to the caller. For a successful extraction, crop_box uses PIL coordinates (left, top, exclusive right, exclusive bottom). Foreground pixels come directly from the input. Background pixels in the crop are gray (128 in each channel).

## Reproduce the checks

From the repository root with the environment activated and Day 2 images downloaded:

```bash
python scripts/extract_produce.py --review-panel --device auto
python scripts/extract_produce.py --image "data/raw/mendeley_banana/Original Image/FreshBanana/FreshBanana (1).jpg" --device cpu
python -m pytest -q
```

The panel CSV under results/day4 records every outcome in sample order. Numbered binary masks and crops are local PNGs under results/smoke/day4/panel. Single-photo outputs go under results/smoke/day4/single.

## Observations on the fixed Day 2 panel

Of 32 GPU inputs, 19 produced crops, five returned multiple_objects and eight returned no_produce_detected. All eight misses carried rotten/spoiled source labels. A separate CPU run extracted the first Mendeley fresh banana. All 19 masks matched the oriented input dimensions, and the crop sizes matched the nonzero mask bounds.

Visual inspection of all 19 crop previews showed dark patches retained in examples 8, 11, 12 and 25–27. Samples 5 and 9 each combined multiple bananas in a single mask. The multiple_objects check therefore catches separately detected instances only. Mask overlap accuracy remains unmeasured because the panel has no reference masks. Keep original images available for Day 5 and report detection failures alongside any results on the extracted subset.

## Collaboration check on November 27

The shared remote exposed main at b1bb521 and feature/data-model at 55f3159 before these local edits. All main commits were present on feature/data-model. No additional branch or pull-request head was visible. The teammate can use this stage from their own branch after incorporating these changes. If their work lives in a separate fork, its branch URL is needed to compare the implementations.
