"""Run YOLO on the Day 2 contact-sheet samples; report failures without relabeling data."""
from collections import Counter
import csv
import json
from pathlib import Path
import sys
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, load_config
from src.dataset_inspection import write_csv
from src.runtime import configure_cache, select_device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()
    samples_path = ROOT / "results/day2/banana_inventory/preview_samples.csv"
    if not samples_path.is_file():
        parser.error("Run scripts/inspect_dataset.py with both datasets first")
    with samples_path.open(newline="") as handle:
        samples = list(csv.DictReader(handle))
    if not samples:
        parser.error("No valid image samples were found")
    configure_cache()
    from ultralytics import YOLO
    config = load_config()
    model = YOLO(str(ROOT / config["identification"]["model"]))
    device = select_device(args.device)
    confidence = config["identification"]["confidence_threshold"]
    output = ROOT / "results/smoke/day2_detection"
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, sample in enumerate(samples, start=1):
        path = ROOT / sample["image_path"]
        result = model.predict(source=str(path), device=device, conf=confidence, imgsz=640, verbose=False)[0]
        bananas = [box for box in result.boxes if model.names[int(box.cls.item())] == "banana"]
        status = ("no_banana" if not bananas else "multiple_bananas" if len(bananas) > 1
                  else "one_banana_detection_with_mask" if result.masks is not None else "no_mask")
        annotated = output / f"sample_{index:02d}.jpg"
        result.save(filename=str(annotated))
        rows.append({"image_path": sample["image_path"], "banana_detections": len(bananas),
                     "max_banana_confidence": round(max((float(b.conf.item()) for b in bananas), default=0), 6),
                     "all_class_detections": len(result.boxes),
                     "detected_classes": ";".join(sorted({model.names[int(box.cls.item())] for box in result.boxes})),
                     "all_class_masks": 0 if result.masks is None else len(result.masks),
                     "status": status, "annotated_path": annotated.relative_to(ROOT).as_posix()})
        print(f"{index}/{len(samples)}: {status} — {path.name}", flush=True)
    report = ROOT / "results/day2/detection"
    write_csv(report / "sample_detections.csv", list(rows[0]), rows)
    summary = {"model": config["identification"]["model"], "device": device,
               "confidence_threshold": confidence, "image_size": 640, "sample_count": len(rows),
               "statuses": dict(Counter(r["status"] for r in rows)),
               "interpretation": "Convenience-sample execution and failure review only, not detection accuracy or mask IoU. No mask ground truth; no dataset labels changed."}
    (report / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
