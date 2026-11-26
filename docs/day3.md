# Day 3 banana pilot

From the project root, activate the Day 1 environment and run:

    python scripts/download_dataset.py all
    python scripts/prepare_dataset.py
    python -m pytest -q

The reviewed CSVs are included in Git. Preparation checks the selected raw files against Day 2 SHA-256 values, corrects EXIF orientation, converts to RGB, and fits the full image inside a 224 × 224 square with gray padding. PNG outputs live under the ignored data/processed/day3 directory. Use the processed_path and class_id columns of data/manifests/day3_splits.csv for the original-image baseline. Apply any random augmentation only to training examples at load time.

## Curation and split

All 400 Mendeley thumbnails were visually screened. The review CSV records one decision per original. We kept 180 single-banana images with a usable capture time and retained their source label. We excluded 186 multi-banana scenes, held out 31 fresh-labeled images with ambiguous discoloration for team review, and set aside three other single-banana photos lacking a capture time. Screening may favor clear examples. Source label quality, background and resolution differences remain limitations.

| Partition | Apparently fresh | Visible spoilage | Total |
| --- | ---: | ---: | ---: |
| Train | 42 | 87 | 129 |
| Validation | 9 | 27 | 36 |
| Test | 5 | 10 | 15 |

We sorted eligible photos by their EXIF capture time and started a new group after a gap exceeding 30 minutes. All eight resulting capture groups are preserved intact. Using seed 42 for tie ordering, the script chooses the group assignment closest to 70/15/15 by squared class-proportion error, with both classes present in each partition. Multiple captures of one specimen could still span sessions. Report any subsequent scores as exploratory capture-group results. The 15 test photos give limited evidence about performance on new bananas. Detector success played no part in selection.

## Team Member 2

Use data/manifests/day3_demo_views.csv to find 19 three-photo demonstrations under the downloaded TR-6 tree. Each uses the first, sixth and eleventh chronological images in one of the Day 2 capture sessions. All 57 thumbnails were visually checked for a single banana and a change in appearance across views. Use view_order 1 for one input, 1–2 for two, or 1–3 for three. Repeated sessions may show the same physical banana over time. Keep these sessions for demonstrating uploads and fusion and out of classifier training and quantitative independent-item comparisons.

Day 4 can now test the detector and mask extraction on single bananas, including the dark examples it previously missed. Preserve original-image inputs for comparison.
