# Day 2 dataset worksheet

No training dataset has been selected or downloaded during Day 1. Banana is provisional. Review the actual label definitions: visible ripening marks do not automatically establish spoilage.

For each candidate source record:

| Field | Entry |
| --- | --- |
| Dataset title, URL, version and access date | Pending |
| License, citation and redistribution terms | Pending |
| Produce types and original condition labels | Pending |
| Mapping to the two FreshView labels, with rationale | Pending |
| Number of usable images per class | Pending |
| Physical specimen IDs and view/time identifiers | Pending |
| Exact/near duplicates and overlapping sources | Pending |
| Broken images, resolution and background observations | Pending |
| Proposed split unit and leakage prevention | Pending |
| Agreed supported produce | Pending |

Suggested manifest columns: `image_path,source,source_image_id,item_id,view_id,produce_type,original_label,condition_label,split`. Paths should be project-relative. Leave unknown physical-item IDs unknown; do not invent item groups from unrelated photos.

Keep downloads under `data/raw/`, derived data under `data/processed/`, and reviewed manifests under `data/manifests/`. If authentic grouped views cannot be verified, narrow multiview claims to a demonstration and evaluate single-view performance honestly.
