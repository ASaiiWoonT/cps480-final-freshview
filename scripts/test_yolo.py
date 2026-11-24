"""Run pretrained YOLO segmentation; downloads weights on first use."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, load_config
from src.runtime import configure_cache, select_device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--image", type=Path, help="Optional real produce photo")
    args = parser.parse_args()
    if args.image and not args.image.is_file():
        parser.error(f"Image not found: {args.image}")
    configure_cache()
    import numpy as np
    from ultralytics import YOLO
    config = load_config()
    path = ROOT / config["identification"]["model"]
    path.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(path))
    assert model.task == "segment"
    candidates = set(load_config("classes")["recognition_candidates"])
    assert candidates <= set(model.names.values())
    print("Recognized produce:", {i: name for i, name in model.names.items() if name in candidates})
    device = select_device(args.device)
    source = str(args.image) if args.image else np.zeros((320, 320, 3), dtype=np.uint8)
    results = model.predict(source=source, device=device, imgsz=320,
                            conf=config["identification"]["confidence_threshold"],
                            save=bool(args.image), project=str(ROOT / "results" / "smoke"),
                            name="yolo", verbose=False)
    assert len(results) == 1 and results[0].boxes is not None
    print(f"YOLO inference passed on {device}; detections: {len(results[0].boxes)}")
    print("Segmentation masks:", 0 if results[0].masks is None else len(results[0].masks))
    if not args.image:
        print("Synthetic blank input verifies execution only; produce/mask quality remains untested.")


if __name__ == "__main__":
    main()
