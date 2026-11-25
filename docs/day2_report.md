# Day 2 results — November 25, 2026

**Outcome:** dataset research, selective acquisition, inspection tools, manifests, a multiview feasibility audit and real-photo detector checks are complete. The project is ready for **Day 3 curation**, not model training or a claim of item-independent evaluation. Work is on local branch `feature/data-model`; nothing was committed or pushed by this task.

## Acquired and inspected

| Source / original class | Images | Decodable | Width range | Height range |
| --- | ---: | ---: | --- | --- |
| Mendeley FreshBanana | 200 | 200 | 549–1600 | 551–1662 |
| Mendeley RottenBanana | 200 | 200 | 1533–4160 | 1209–4160 |
| TR-6 Not_spoiled | 153 | 153 | 3000 | 4000 |
| TR-6 Spoiled | 170 | 170 | 3000 | 4000 |

All 723 images decoded; no unmapped image folders, corrupt files or exact decoded-pixel duplicates were found. Dimensions are measured after EXIF orientation. The original image bytes are unchanged. Raw files total 791,587,448 bytes (about 792 MB); thermal images, augmented images, the duplicate-looking Normal tree and unrelated produce were not downloaded.

Use [the source register](dataset_sources.md) for licenses, citations, selection rationale and mappings. Freshness44's public download routes were unavailable in this session, so a directly accessible original source was selected. Both acquired sources publish CC BY 4.0 metadata. Full-archive hashes were recorded, but only selected-member CRC32 checks and local SHA-256 hashes were verified.

## Duplicate and sample review

The dHash screen flagged nine candidate pairs at distance ≤4: four Mendeley pairs and five TR-6 pairs. All nine pairs were visually reviewed by Codex; the observations are in `results/day2/review/near_duplicate_review.csv`. Mendeley pairs show very similar multi-banana arrangements; TR-6 pairs show similar appearance across acquisition times. These are likely correlated observations, not proven independent specimens. One TR-6 pair spans the two source labels and different dates: temporal deterioration is a plausible explanation, so it was not automatically relabeled.

The screen is not rotation/crop invariant and is not an exhaustive specimen-ID detector. Zero exact duplicates does not mean no leakage risk. Keep candidate relationships together during review, inspect additional adjacent-looking frames, and document conservative grouping/exclusion decisions before any split.

Four deterministic contact sheets (eight samples per source/class) were also visually reviewed. The file list and separate observations are retained in `results/day2/review/sample_review.csv`.

- Mendeley contains both individual bananas and bunches. Seven of the sixteen inspected Mendeley samples visibly contain multiple bananas. This conflicts with the proposed one-item-per-image interface and requires an explicit Day 3 retain/exclude/crop policy.
- Dark spots appear in fresh/not-spoiled samples as well as rotten/spoiled samples. In particular, `FreshBanana (99).jpg` has substantial dark discoloration despite its source label. Keep it for label-policy review; do not infer a new label or food safety from appearance alone.
- Mendeley's fresh and rotten classes have markedly different resolution ranges. Background/capture differences could become shortcuts for a classifier. Resizing does not by itself remove all acquisition bias.
- TR-6's inspected samples show a single banana against a similar background, with markings and deterioration consistent with repeated observations. This supports cautious demonstration use, not verified independent-item evaluation.

Only the 32 samples and nine pairs received this visual review; the full dataset is not manually labeled or approved. All image-level training review fields remain pending.

## Multiview feasibility

The timestamp audit finds **19 candidate sessions of 17 images each**, with no within-session source-label conflict. Times are parsed from filenames and carry no verified timezone. The 30-minute gap is an explicit grouping heuristic, not a publisher-provided specimen identifier. Session and membership tables are under `results/day2/multiview/`.

No independent specimen IDs or view-angle indices were verified. Different sessions/days must not be treated as different fruits. The archive index also lists 323 Normal/Banana RGB filenames matching the Classified subset by basename and size; those copies were excluded rather than counted as new data. This overlap finding uses archive metadata, not an independent pixel comparison of the Normal tree.

**Decision:** keep TR-6 separate from model-development splits and use it as a limited multiview demonstration candidate. Team Member 2 should verify the identity and viewpoint selection for any demonstrated sequence. Do not claim multiview accuracy gains on independent fruit from these session counts. If further identity evidence is unavailable, retain the restricted claim explicitly.

## Real-photo YOLO check

YOLO11 Nano Segmentation was run on the same 32 samples, on the RTX 4060, at image size 640 and confidence 0.25.

| Source / class | One banana detection with mask | Multiple banana detections | No banana detection |
| --- | ---: | ---: | ---: |
| Mendeley FreshBanana | 5 | 3 | 0 |
| Mendeley RottenBanana | 3 | 2 | 3 |
| TR-6 Not_spoiled | 8 | 0 | 0 |
| TR-6 Spoiled | 3 | 0 | 5 |
| Total | 19 | 5 | 8 |

These are detector outputs, **not accuracy estimates**. There are no ground-truth boxes/masks and the sample is not a randomized test set. One detection may cover several physical bananas. Six annotated outputs were visually inspected (samples 1, 2, 9, 17, 25 and 28): masks were produced on light/spotted examples, a bunch could be merged, and a dark banana in sample 28 was labeled as a bird. The CSV records all predicted class names, including other missed dark examples labeled as birds.

The eight misses are retained in the data. Do not filter out hard spoiled images before reporting results. Day 4 must address detector failure handling and compare an original-image baseline with any segmentation-assisted pipeline. The current app still previews uploads and does not expose an untrained condition prediction.

## Validation performed

- Full acquisition: 400 Mendeley images and 323 TR-6 images plus its README; ZIP CRC32 checked per selected member, local SHA-256 recorded.
- Resume/reuse: a second acquisition run verified existing files and reused them; only archive index ranges were fetched (about 0.3 MB Mendeley and 2.7 MB TR-6).
- Full inventory: all 723 decoded, original class counts matched, empty invalid-image report, deterministic metadata and duplicate screening.
- Multiview audit: all 323 timestamps parsed into 19 candidate sessions; no physical IDs invented.
- Actual model execution on 32 images: completed, with failures recorded instead of hidden.
- Automated tests: 19 passed, including the five existing app tests plus download, inspection and multiview-audit tests. No internet or real dataset is required by the test suite.
- Dependency check: `pip check` passed. `requests` was promoted from an existing transitive dependency to an explicit pinned requirement; the lock already contains the same version.
- Ignore rules keep raw images, `.part` files, weights, caches, contact sheets and detector overlays out of Git.

## Day 3 handoff

1. Retain banana as the initial category. Review whether source-label proxies fit the intended visible-condition definition; record ambiguous cases without inventing clinical or safety labels.
2. Review the Mendeley multi-object scenes and repeated captures. Define conservative image groups or exclusions and document what remains uncertain. Do not infer item IDs from sequential filenames alone.
3. Establish a reproducible split only after grouping. Use the configured 70/15/15 proportions as targets, stratify when feasible, keep related captures together, and do not mix TR-6 sessions into ordinary training/test images.
4. Preserve original images for the classification baseline. Do not drop spoiled images solely because YOLO failed to recognize them.
5. Team Member 2 reviews the session audit and limits multiview claims to verified evidence. If independent specimens cannot be demonstrated, state that limit in experiments and the paper.

Reproduce the work using [day2_workflow.md](day2_workflow.md). Training, splitting, model integration and uncertainty calibration are intentionally left for their planned later days.
