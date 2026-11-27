"""Run the Day 4 detector on one photo or the fixed Day 2 review panel."""
import argparse
from collections import Counter
import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.dataset_inspection import write_csv
from src.identification import ProduceDetector
from src.images import read_image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--image", type=Path)
    inputs.add_argument("--review-panel", action="store_true")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()
    if args.review_panel:
        with (ROOT / "results/day2/banana_inventory/preview_samples.csv").open(newline="") as handle:
            images = [Path(row["image_path"]) for row in csv.DictReader(handle)]
    else:
        images = [args.image.resolve()]
    detector = ProduceDetector(args.device)
    rows = []
    mode = "panel" if args.review_panel else "single"
    output = ROOT / "results/smoke/day4" / mode
    output.mkdir(parents=True, exist_ok=True)
    for i, path in enumerate(images, start=1):
        mask_path = output / f"{i:02d}_mask.png"
        crop_path = output / f"{i:02d}_crop.png"
        try:
            with (ROOT / path).open("rb") as handle:
                image = read_image(handle)
        except (OSError, ValueError) as error:
            result = dict(status="invalid_image", error=str(error))
        else:
            result = detector.analyze(image)
        if result["status"] == "segmented":
            result["mask"].save(mask_path)
            result["segmented_image"].save(crop_path)
        else:
            mask_path.unlink(missing_ok=True)
            crop_path.unlink(missing_ok=True)
        rows.append(dict(image_path=path.as_posix(), status=result["status"],
                         produce_type=result.get("produce_type"), confidence=result.get("detection_confidence"),
                         crop_box=result.get("crop_box"), error=result.get("error")))
    report = ROOT / "results/day4/review_panel.csv" if args.review_panel else output / "result.csv"
    write_csv(report, list(rows[0]), rows)
    print(dict(Counter(row["status"] for row in rows)), report, flush=True)
    if args.image:
        print(rows[0].get("error") or crop_path)
    return int(any(r["status"] == "invalid_image" for r in rows))


if __name__ == "__main__":
    raise SystemExit(main())
