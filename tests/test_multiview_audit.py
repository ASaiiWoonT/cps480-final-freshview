from src.multiview_audit import candidate_sessions


def row(time, label="Not_spoiled", path="a.jpg"):
    return {"source": "tr6_banana", "valid_image": "true", "capture_timestamp": time,
            "image_path": path, "original_label": label}


def test_time_clusters_do_not_become_item_ids_and_keep_conflicting_labels():
    sessions, membership, missing = candidate_sessions([
        row("2025-09-11T10:00:00"), row("2025-09-11T10:01:00", "Spoiled", "b.jpg"),
        row("2025-09-11T14:00:00", path="c.jpg"), row("2025-09-12T10:00:00", path="d.jpg"),
        row("", path="unknown.jpg"),
    ])
    assert len(sessions) == 3 and sessions[0]["image_count"] == 2
    assert sessions[0]["label_conflict"] == "true"
    assert missing == ["unknown.jpg"]
    assert all(r["item_id"] == r["view_id"] == "" for r in membership)
