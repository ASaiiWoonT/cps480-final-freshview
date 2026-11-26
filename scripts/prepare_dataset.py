"""Build the reviewed single-banana pilot dataset from unchanged Day 2 files."""
import csv
import itertools
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, load_config
from src.dataset_inspection import file_sha256, write_csv


def read_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def assign_groups(rows, ratios, seed):
    # Exhaustive search is practical for the small number of reviewed capture sessions.
    names = ("train", "validation", "test")
    counts = defaultdict(Counter)
    for row in rows:
        counts[row["capture_group"]][row["condition_label"]] += 1
    groups = sorted(counts)
    random.Random(seed).shuffle(groups)
    totals = Counter(row["condition_label"] for row in rows)
    best = None
    for assignment in itertools.product(names, repeat=len(groups)):
        sizes = {name: Counter() for name in names}
        for group, split in zip(groups, assignment):
            sizes[split].update(counts[group])
        if any(sizes[s][label] == 0 for s in names for label in totals):
            continue
        score = sum((sizes[s][label] / total - ratios[s+"_ratio"]) ** 2
                    for s in names for label, total in totals.items())
        if best is None or score < best[0]:
            best = score, dict(zip(groups, assignment))
    if best is None:
        raise ValueError("Insufficient capture groups for both labels in every split")
    return best[1]


def main():
    manifests = ROOT / "data/manifests"
    inventory = {r["image_path"]: r for r in read_rows(manifests / "banana_inventory.csv")
                 if r["source"] == "mendeley_banana"}
    review = read_rows(manifests / "day3_scene_review.csv")
    if len(review) != len(inventory) or {r["image_path"] for r in review} != set(inventory):
        raise ValueError("Scene review must cover the Mendeley inventory exactly once")
    selected = []
    for r in review:
        original = inventory[r["image_path"]]
        if original["sha256"] != r["sha256"]:
            raise ValueError("Inventory changed since review")
        if r["decision"] == "include":
            if not r["capture_group"] or file_sha256(ROOT / r["image_path"]) != r["sha256"]:
                raise ValueError(f"Missing capture group or changed original: {r['image_path']}")
            selected.append({**r, "condition_label": original["condition_label"]})
    cfg = load_config()
    groups = assign_groups(selected, cfg["dataset"], cfg["seed"])
    labels = {v:k for k,v in load_config("classes")["condition_classes"].items()}
    size = cfg["classifier"]["image_size"]
    for r in selected:
        r["split"] = groups[r["capture_group"]]
        r["class_id"] = labels[r["condition_label"]]
        target = Path("data/processed/day3") / str(size) / (r["sha256"] + ".png")
        destination = ROOT / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(ROOT / r["image_path"]) as im:
            rgb = ImageOps.exif_transpose(im).convert("RGB")
            output = ImageOps.pad(rgb, (size,size), method=Image.Resampling.LANCZOS, color=(128,128,128))
            output.save(destination.with_suffix(".tmp"), format="PNG")
            destination.with_suffix(".tmp").replace(destination)
        r["processed_path"] = target.as_posix()
    write_csv(manifests / "day3_splits.csv", list(selected[0]), selected)
    print("Images per split and label:", sorted(Counter((r["split"],r["condition_label"]) for r in selected).items()))
    print("Capture groups:", len(groups), "Decisions:", dict(Counter(r["decision"] for r in review)))


if __name__ == "__main__":
    main()
