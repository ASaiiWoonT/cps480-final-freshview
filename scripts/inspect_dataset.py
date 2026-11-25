"""Inventory the downloaded banana datasets, validate images and screen duplicates."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml

from src.config import ROOT
from src.dataset_inspection import inspect_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["all", "mendeley_banana", "tr6_banana"], default="all")
    parser.add_argument("--dhash-threshold", type=int, default=4)
    args = parser.parse_args()
    specs = yaml.safe_load((ROOT / "configs/datasets.yaml").read_text())["sources"]
    if args.source != "all":
        specs = {args.source: specs[args.source]}
    name = "banana_inventory" if args.source == "all" else args.source
    summary = inspect_sources(ROOT, specs, ROOT / f"data/manifests/{name}.csv",
                              ROOT / "results/day2" / name, args.dhash_threshold)
    print(json.dumps(summary, indent=2))
    print(f"Manifest: data/manifests/{name}.csv")
    print(f"Reports: results/day2/{name}/; raw files were not modified.")
    if (not summary["total_images"] or summary["missing_roots"] or not summary["counts_match_expected"]
            or summary["corrupt_images"] or summary["unknown_labels"]):
        print("Inventory is incomplete or contains invalid/unmapped files; review reports before continuing.")
        return 1
    print("Inventory complete. Duplicate candidates and labels still need review before Day 3 splitting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
