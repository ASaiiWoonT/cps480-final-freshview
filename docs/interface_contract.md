# Proposed FreshView interface

The complete condition assessment is pending classifier integration. The implemented [Day 4 extraction stage](day4.md) accepts PIL RGB and returns the aligned mask and crop with stage status `segmented`.

## Single-image pipeline

`src.pipeline.analyze_image(image)` accepts a loaded `PIL.Image.Image` in RGB mode, containing one physical produce item. Uploaded files are decoded and oriented by `src.images.read_image` before use.

The result has these keys:

| Key | Eventual success value |
| --- | --- |
| `status` | `success` |
| `produce_type` | Supported produce label, initially banana if data supports it |
| `detection_confidence` | Float from 0 to 1 |
| `segmented_image` | PIL RGB image; preserve condition-relevant discoloration |
| `condition_probabilities` | Mapping with `apparently_fresh` and `visible_spoilage`, summing to 1 |
| `processing_time_ms` | Nonnegative measured time |
| `error` | `None` on success, explanatory string otherwise |

Error statuses planned: `no_produce_detected`, `unsupported_produce`, `multiple_objects`, `segmentation_failed`, `invalid_image`, and `not_ready`. Unavailable fields are `None`; never substitute fabricated predictions. Keep original images available for evaluation of segmentation effects.

## Later modules

- Identification: RGB image → category, score and selected object.
- Segmentation: RGB image and selected object → aligned mask and extracted RGB crop.
- Classifier: transformed crop → probabilities in the order defined in `configs/classes.yaml`.
- Multiview: 1–3 predictions for the same physical item → mean probabilities and view statistics.
- Uncertainty: fused probabilities and view disagreement → decision or abstention reason.

Do not silently discard failed views or combine different produce types. Agree on handling these cases before integration. Select uncertainty thresholds using validation data, not the held-out test set. The Day 1 app only previews uploads.
