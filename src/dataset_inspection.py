"""Deterministic image inventory and duplicate screening; never assigns splits or item IDs."""
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import warnings

from PIL import Image, ImageDraw, ImageOps

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
FIELDS = ["image_path", "source", "source_version", "source_image_id", "produce_type",
          "original_label", "condition_label", "mapping_status", "item_id", "view_id",
          "capture_timestamp", "split", "review_status", "width", "height", "mode", "bytes",
          "sha256", "pixel_sha256", "dhash", "valid_image", "label_known", "error",
          "exact_duplicate_group"]


def file_sha256(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def difference_hash(image):
    """64-bit horizontal dHash. Similarity is only a manual-review hint."""
    small = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = small.tobytes()
    value = 0
    for y in range(8):
        for x in range(8):
            value = (value << 1) | (pixels[y * 9 + x] > pixels[y * 9 + x + 1])
    return f"{value:016x}"


def inspect_image(path, root, source_name, spec):
    relative = path.relative_to(root / spec["root"])
    label = spec["labels"].get(relative.parent.as_posix())
    row = dict.fromkeys(FIELDS, "")
    row.update(image_path=path.relative_to(root).as_posix(), source=source_name,
               source_version=spec["version"], source_image_id=relative.as_posix(),
               produce_type=spec["produce_type"], mapping_status="provisional_source_label_proxy",
               original_label=label["original_label"] if label else "",
               condition_label=label["condition_label"] if label else "",
               review_status="pending", valid_image="false", label_known=str(bool(label)).lower())
    if source_name == "tr6_banana":
        try:
            row["capture_timestamp"] = datetime.strptime(path.stem, "%Y%m%d_%H%M%S").isoformat()
        except ValueError:
            pass  # Do not invent acquisition times from an unfamiliar filename.
    try:
        if path.is_symlink() or not path.resolve().is_relative_to((root / spec["root"]).resolve()):
            raise ValueError("Symlink or path outside source root")
        row["bytes"] = path.stat().st_size
        row["sha256"] = file_sha256(path)
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as probe:
                probe.verify()
            with Image.open(path) as raw:
                row["mode"] = raw.mode
                image = ImageOps.exif_transpose(raw).convert("RGB")
                image.load()
                row["width"], row["height"] = image.size
                digest = hashlib.sha256(f"{image.width}x{image.height}:RGB:".encode())
                digest.update(image.tobytes())
                row["pixel_sha256"] = digest.hexdigest()
                row["dhash"] = difference_hash(image)
                row["valid_image"] = "true"
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as error:
        row["error"] = f"{type(error).__name__}: {error}"
    return row


def duplicate_reports(rows, threshold=4):
    """Find exact decoded-pixel groups and all dHash candidate pairs, across sources."""
    if not 0 <= threshold <= 64:
        raise ValueError("dHash threshold must be between 0 and 64")
    groups = defaultdict(list)
    valid = [r for r in rows if r["valid_image"] == "true"]
    for row in valid:
        groups[row["pixel_sha256"]].append(row)
    exact = []
    for digest, group in sorted(groups.items()):
        if len(group) < 2:
            continue
        group_id = f"pixels_{digest[:16]}"
        conflict = len({r["condition_label"] for r in group if r["condition_label"]}) > 1
        for row in group:
            row["exact_duplicate_group"] = group_id
            exact.append({"group": group_id, "image_path": row["image_path"],
                          "condition_label": row["condition_label"], "label_conflict": str(conflict).lower()})
    # One representative per exact group avoids repeating every near-pair for identical pixels.
    representatives = [group[0] for _, group in sorted(groups.items())]
    near = []
    for index, left in enumerate(representatives):
        for right in representatives[index + 1:]:
            distance = (int(left["dhash"], 16) ^ int(right["dhash"], 16)).bit_count()
            if distance <= threshold:
                near.append({"image_a": left["image_path"], "image_b": right["image_path"],
                             "dhash_distance": distance,
                             "different_labels": str(left["condition_label"] != right["condition_label"]).lower(),
                             "review_status": "candidate_not_confirmed"})
    return exact, near


def write_csv(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def preview_sheets(root, rows, output, per_class=8):
    """Save evenly spaced labeled samples for manual inspection, without altering originals."""
    groups = defaultdict(list)
    for row in rows:
        if row["valid_image"] == "true" and row["label_known"] == "true":
            groups[(row["source"], row["original_label"])].append(row)
    selected = []
    output.mkdir(parents=True, exist_ok=True)
    for (source, label), group in sorted(groups.items()):
        count = min(per_class, len(group))
        indices = sorted({round(i * (len(group) - 1) / max(1, count - 1)) for i in range(count)})
        sheet = Image.new("RGB", (4 * 240, ((len(indices) + 3) // 4) * 225), "white")
        draw = ImageDraw.Draw(sheet)
        for number, index in enumerate(indices):
            row = group[index]
            with Image.open(root / row["image_path"]) as image:
                thumb = ImageOps.exif_transpose(image).convert("RGB")
                thumb.thumbnail((230, 180))
            x, y = (number % 4) * 240, (number // 4) * 225
            sheet.paste(thumb, (x + (240 - thumb.width) // 2, y))
            draw.text((x + 5, y + 182), f"{number + 1}: {Path(row['image_path']).name[:31]}", fill="black")
            draw.text((x + 5, y + 198), f"{source} / {label}", fill="black")
            selected.append({"sheet": f"{source}_{label}.jpg", "position": number + 1,
                             "image_path": row["image_path"], "review_status": "pending"})
        sheet.save(output / f"{source}_{label}.jpg", quality=90)
    return selected


def inspect_sources(root, specs, manifest, report_dir, threshold=4):
    root, report_dir = Path(root).resolve(), Path(report_dir)
    rows, missing_roots = [], []
    for name, spec in specs.items():
        folder = root / spec["root"]
        if not folder.is_dir():
            missing_roots.append(spec["root"])
            continue
        for path in sorted(folder.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTENSIONS and (path.is_file() or path.is_symlink()):
                rows.append(inspect_image(path, root, name, spec))
                if len(rows) % 100 == 0:
                    print(f"Inspected {len(rows)} images...", flush=True)
    rows.sort(key=lambda row: row["image_path"])
    exact, near = duplicate_reports(rows, threshold)
    counts = Counter((r["source"], r["original_label"]) for r in rows)
    inventory = []
    for name, spec in specs.items():
        for rule in spec["labels"].values():
            group = [r for r in rows if r["source"] == name and r["original_label"] == rule["original_label"]]
            valid = [r for r in group if r["valid_image"] == "true"]
            inventory.append({"source": name, "original_label": rule["original_label"],
                              "condition_label": rule["condition_label"], "expected": rule["expected_images"],
                              "found": counts[(name, rule["original_label"])], "decodable": len(valid),
                              "unique_pixels": len({r["pixel_sha256"] for r in valid}),
                              "width_min": min((r["width"] for r in valid), default=0),
                              "width_max": max((r["width"] for r in valid), default=0),
                              "height_min": min((r["height"] for r in valid), default=0),
                              "height_max": max((r["height"] for r in valid), default=0)})
    summary = {
        "scope": "Day 2 inventory, not a cleaned training set or an assigned split",
        "total_images": len(rows), "decodable_images": sum(r["valid_image"] == "true" for r in rows),
        "corrupt_images": sum(r["valid_image"] != "true" for r in rows),
        "unknown_labels": sum(r["label_known"] != "true" for r in rows),
        "missing_roots": missing_roots,
        "counts_match_expected": bool(inventory) and all(i["found"] == i["expected"] for i in inventory),
        "exact_duplicate_groups": len({r["group"] for r in exact}),
        "exact_duplicate_members": len(exact),
        "exact_conflicting_label_groups": len({r["group"] for r in exact if r["label_conflict"] == "true"}),
        "near_duplicate_candidate_pairs": len(near), "dhash_threshold": threshold,
        "near_duplicate_method": "64-bit horizontal dHash, one representative per exact pixel group; candidates need visual review; not rotation/crop invariant",
        "verified_item_ids": 0, "splits_assigned": False, "inventory": inventory,
    }
    write_csv(manifest, FIELDS, rows)
    write_csv(report_dir / "class_counts.csv", list(inventory[0]) if inventory else ["source"], inventory)
    write_csv(report_dir / "exact_duplicates.csv", ["group", "image_path", "condition_label", "label_conflict"], exact)
    write_csv(report_dir / "near_duplicate_candidates.csv", ["image_a", "image_b", "dhash_distance", "different_labels", "review_status"], near)
    write_csv(report_dir / "invalid_images.csv", FIELDS, [r for r in rows if r["valid_image"] != "true" or r["label_known"] != "true"])
    samples = preview_sheets(root, rows, report_dir / "previews")
    write_csv(report_dir / "preview_samples.csv", ["sheet", "position", "image_path", "review_status"], samples)
    (report_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
