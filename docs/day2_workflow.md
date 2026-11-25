# Day 2 — reproduce dataset acquisition and inspection

Run from your cloned repository with `.venv` activated. CPU is sufficient; only the optional detector check benefits from a GPU. The selected subsets occupy about 792 MB plus reports/previews. No full 20 GB archive or dataset account is needed.

## Install and download

Install the appropriate PyTorch build using the README first, then:

```bash
python -m pip install -r requirements.txt
python -m pip check
python scripts/download_dataset.py all --list-only
python scripts/download_dataset.py all
```

The inventory-only command is optional. Select `mendeley_banana` or `tr6_banana` instead of `all` to download one source. `requests` is now an explicit requirement; it was already installed in the Day 1 environment.

Original archive paths are preserved under `data/raw/<source>/`. The downloader requires HTTP Range support and refuses to fetch entire archives silently. Rerun after an interruption: matching files are checked and reused. A differing completed file is preserved and reported; move it aside deliberately before retrying. Receipts are written after the complete selected source succeeds. Do not edit raw files.

## Inspect and audit

```bash
python scripts/inspect_dataset.py
python scripts/inspect_multiview.py
```

Inspection can take several minutes. Progress is printed every 100 images. It checks decoding, class mapping, resolution and duplicates across sources without assigning train/test splits, specimen IDs or view angles.

Baseline: 723 decodable images, 0 exact pixel-duplicate groups, 9 near-duplicate candidate pairs at dHash distance ≤4, and 19 timestamp clusters of 17 images. Investigate changed counts rather than changing expectations to hide an error.

For a partial download use `--source mendeley_banana` or `--source tr6_banana` with the inspection script. These create separate inventories. The multiview and detection commands expect the default combined inventory. Missing folders, count mismatches, corrupt images or unmapped image folders produce diagnostic reports and a nonzero exit status.

| Output | Purpose |
| --- | --- |
| `data/manifests/banana_inventory.csv` | Per-image provenance, labels and checksums; empty item/view/split fields |
| `results/day2/banana_inventory/summary.json` | Overall inspection outcome |
| `results/day2/banana_inventory/class_counts.csv` | Counts and dimension ranges |
| `results/day2/banana_inventory/exact_duplicates.csv` | Identical decoded pixels and label conflicts |
| `results/day2/banana_inventory/near_duplicate_candidates.csv` | Similarity hints, not deletion decisions |
| `results/day2/banana_inventory/invalid_images.csv` | Corrupt/unmapped files; header only when none |
| `results/day2/banana_inventory/previews/` | Four local contact sheets, eight samples per class |
| `results/day2/banana_inventory/preview_samples.csv` | Exact sampled files |
| `results/day2/multiview/` | Capture-time candidates, not independent specimens |
| `results/day2/review/` | Separate recorded visual review |

Generated CSV/JSON outputs are replaced on rerun. Keep curation decisions in separate review files so rerunning inspection does not erase them. Contact sheets and overlays are excluded from Git; each teammate regenerates them locally.

## Real-photo detector check

```bash
python scripts/check_detection_samples.py --device auto
```

Use `--device cpu` for CPU or `--device cuda` to require NVIDIA acceleration. This processes the 32 contact-sheet samples with YOLO11 Nano Segmentation at image size 640 and confidence 0.25. CSV/JSON reports go under `results/day2/detection/`; annotated images go under `results/smoke/day2_detection/`.

Misses are diagnostic findings, not script failures. Several dark bananas were missed or assigned another class. Do not remove them to inflate evaluation results. One detection may cover a bunch; box count does not verify physical-item count. Without ground-truth masks this is not a segmentation-IoU evaluation.

## Check before sharing

```bash
python -m pytest -q
python -m pip check
git diff --check
git status
```

Dataset tests use tiny generated fixtures and mocked HTTP responses; they need no network or real datasets. Commit code, configs, documentation, references and CSV/JSON reports. Raw images, caches, weights and generated previews remain ignored.
