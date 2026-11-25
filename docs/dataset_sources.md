# Dataset sources and Day 2 selection

Reviewed November 25, 2026. Banana is selected for initial development. These are inspection data, not an approved training split.

| Source | Version / license | Inspected subset | Decision |
| --- | --- | --- | --- |
| [Fresh and Rotten Fruits — Mendeley](https://data.mendeley.com/datasets/bdd69gyhv8/1) | V1; DOI `10.17632/bdd69gyhv8.1`; CC BY 4.0 | Original archive: 200 FreshBanana + 200 RottenBanana | Single-view development candidate, pending item/repeat and multi-object review |
| [TriModal Ripeness 6 — Figshare](https://doi.org/10.6084/m9.figshare.30783827.v1) | V1; CC BY 4.0 | Classified banana RGB: 153 Not_spoiled + 170 Spoiled | Multiview demonstration candidate; independent-item evaluation not yet justified |

Mendeley's publisher describes expert-assisted labels and separate original/augmented archives. Only originals were selected to avoid importing pre-generated augmentations into evaluation. Authors: Nusrat Sultana, Musfika Jahan and Mohammad Shorif Uddin. [Source record](https://data.mendeley.com/datasets/bdd69gyhv8/1)

TR-6 describes repeated visual, thermal and sensor acquisition. We selected classified RGB only, excluding thermal data, gas readings and the parallel Normal tree. Authors: T Bagyammal, Yogini Aishwaryaa P T S, Krishna Deepak and Devika Unnikrishnan. Its versioned metadata records CC BY 4.0. [Source metadata](https://api.figshare.com/v2/articles/30783827/versions/1)

Retain attribution, version and license links with shared subsets/derivatives, and describe changes. Local originals are unchanged; contact sheets and detector overlays are derived inspection outputs. Raw data and previews are excluded from Git. Consult the source license before separate redistribution; this repository has not selected a code license.

## Other candidates

- **Freshness44:** its paper describes a merged freshness dataset, but the public Kaggle view/list/download API routes checked here returned HTTP 404. Neither files nor a dataset license were verified, so it is not a reproducible dependency for this checkout. This does not prove permanent unavailability. Do not infer dataset licensing from the article license. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12526848/), [listed dataset](https://www.kaggle.com/datasets/siavash93/freshness44)
- **Fruits-360 original size:** the current README documents rotation imagery and CC BY-SA 4.0. It is a recognition source, not an established fresh/spoiled label source for this task. Not downloaded. [Source README](https://github.com/fruits-360/fruits-360-original-size/blob/main/README.md)

## Label mapping

| Original label | Provisional FreshView label | Class |
| --- | --- | --- |
| Mendeley `FreshBanana` | `apparently_fresh` | 0 |
| Mendeley `RottenBanana` | `visible_spoilage` | 1 |
| TR-6 `Not_spoiled` | `apparently_fresh` | 0 |
| TR-6 `Spoiled` | `visible_spoilage` | 1 |

These are source-label proxies, not validated visual thresholds or food-safety assessments. Spotting overlaps between labels. No image was relabeled from a thumbnail or detector prediction. The manifest retains original labels, `mapping_status=provisional_source_label_proxy`, and `review_status=pending`: sample review is not full-dataset approval.

## Traceability

- `configs/datasets.yaml`: versions, URLs, exact directories, expected counts and publisher archive hashes.
- `docs/dataset_evidence/`: source metadata and access/overlap observations.
- `data/manifests/downloads/`: extracted-member CRC32 and local SHA-256 receipts.
- `data/manifests/banana_inventory.csv`: 723 image records; item/view/split fields remain empty.
- `results/day2/`: counts, duplicates, session candidates and detector sample results.
- `paper/dataset_references.bib`: dataset and paper references.

The downloader verifies selected ZIP-member CRC32 values and records SHA-256. It retrieves byte ranges, so the publisher's full-archive hash is recorded but **not claimed as verified**.

## Split and multiview decision

No split is created on Day 2. Mendeley filenames do not establish specimen identity; repeated arrangements are visible. Review likely same-item images and keep them together or exclude repeats before splitting. Deduplication alone does not prove specimen independence. Apply augmentation only to the training partition.

TR-6 has 19 timestamp clusters of 17 images, but no verified specimen IDs or view-angle indices in the inspected filenames. Similar markings across days suggest repeated specimens: a capture session is not an independent fruit. Keep TR-6 separate from development splits and limit it to a demonstration unless stronger identity evidence becomes available. Do not combine Normal and Classified copies as additional independent observations.

Before quantitative evaluation, document grouping evidence, label/multi-object decisions and remaining uncertainty. If independent items cannot be established, narrow the claims. See [Day 2 findings](day2_report.md) and [reproduction instructions](day2_workflow.md).
