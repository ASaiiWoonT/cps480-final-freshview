import csv
from pathlib import Path

from PIL import Image

from src.dataset_inspection import inspect_sources, file_sha256


def spec(root, fresh=1, rotten=1):
    return {"root": root, "version": "1", "produce_type": "banana", "labels": {
        "fresh": {"original_label": "fresh", "condition_label": "apparently_fresh", "expected_images": fresh},
        "rotten": {"original_label": "rotten", "condition_label": "visible_spoilage", "expected_images": rotten},
    }}


def save(root, name, color="yellow", **kwargs):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (20, 12), color).save(path, **kwargs)
    return path


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_pixel_duplicates_cross_source_conflicts_and_raw_preservation(tmp_path):
    a = save(tmp_path, "data/raw/a/fresh/a.png", compress_level=0)
    b = save(tmp_path, "data/raw/b/rotten/b.png", compress_level=9)
    assert a.read_bytes() != b.read_bytes()
    hashes = [file_sha256(a), file_sha256(b)]
    manifest = tmp_path / "manifest.csv"
    report = tmp_path / "reports"
    specs = {"a": spec("data/raw/a", 1, 0), "b": spec("data/raw/b", 0, 1)}
    summary = inspect_sources(tmp_path, specs, manifest, report)
    assert summary["counts_match_expected"]
    assert summary["exact_duplicate_groups"] == 1
    assert summary["exact_conflicting_label_groups"] == 1
    rows = read_csv(manifest)
    assert all(r["item_id"] == r["view_id"] == r["split"] == "" for r in rows)
    assert all(r["review_status"] == "pending" for r in rows)
    assert [file_sha256(a), file_sha256(b)] == hashes
    before = manifest.read_bytes()
    inspect_sources(tmp_path, specs, manifest, report)
    assert manifest.read_bytes() == before


def test_corrupt_unknown_and_missing_sources_are_reported(tmp_path):
    broken = tmp_path / "data/raw/a/fresh/broken.jpg"
    broken.parent.mkdir(parents=True)
    broken.write_bytes(b"not a photograph")
    save(tmp_path, "data/raw/a/unmapped/image.png")
    manifest = tmp_path / "manifest.csv"
    summary = inspect_sources(tmp_path, {"a": spec("data/raw/a"), "missing": spec("data/raw/missing")},
                              manifest, tmp_path / "reports")
    assert summary["corrupt_images"] == 1
    assert summary["unknown_labels"] == 1
    assert summary["missing_roots"] == ["data/raw/missing"]
    assert not summary["counts_match_expected"]
    assert len(read_csv(tmp_path / "reports/invalid_images.csv")) == 2


def test_near_duplicates_are_only_candidates_not_removed(tmp_path):
    save(tmp_path, "data/raw/a/fresh/a.png", "yellow")
    save(tmp_path, "data/raw/a/rotten/b.png", "green")
    manifest = tmp_path / "manifest.csv"
    summary = inspect_sources(tmp_path, {"a": spec("data/raw/a")}, manifest, tmp_path / "reports")
    assert summary["exact_duplicate_groups"] == 0
    assert summary["near_duplicate_candidate_pairs"] == 1
    assert len(read_csv(manifest)) == 2
    assert not summary["splits_assigned"]


def test_empty_dataset_is_not_success(tmp_path):
    summary = inspect_sources(tmp_path, {"missing": spec("data/raw/missing")},
                              tmp_path / "manifest.csv", tmp_path / "reports")
    assert summary["total_images"] == 0 and not summary["counts_match_expected"]
