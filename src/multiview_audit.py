"""Describe timestamp clusters without asserting physical-item or view identity."""
from collections import Counter
from datetime import datetime, timedelta
import json


def candidate_sessions(rows, gap_minutes=30):
    if gap_minutes <= 0:
        raise ValueError("Session gap must be positive")
    parsed, missing = [], []
    for row in rows:
        if row["source"] != "tr6_banana" or row["valid_image"] != "true":
            continue
        try:
            parsed.append((datetime.fromisoformat(row["capture_timestamp"]), row))
        except ValueError:
            missing.append(row["image_path"])
    groups = []
    for timestamp, row in sorted(parsed, key=lambda pair: (pair[0], pair[1]["image_path"])):
        if (not groups or timestamp.date() != groups[-1][-1][0].date()
                or timestamp - groups[-1][-1][0] > timedelta(minutes=gap_minutes)):
            groups.append([])
        groups[-1].append((timestamp, row))
    sessions, membership = [], []
    for group in groups:
        first, last = group[0][0], group[-1][0]
        key = "candidate_" + first.strftime("%Y%m%d_%H%M%S")
        labels = Counter(row["original_label"] for _, row in group)
        sessions.append({"candidate_session_id": key, "start": first.isoformat(), "end": last.isoformat(),
                         "image_count": len(group), "label_counts": json.dumps(dict(sorted(labels.items()))),
                         "label_conflict": str(len(labels) > 1).lower(),
                         "item_id": "", "grouping_status": "timestamp_candidate_not_verified_item"})
        membership.extend({"candidate_session_id": key, "image_path": row["image_path"],
                           "capture_timestamp": timestamp.isoformat(), "item_id": "", "view_id": ""}
                          for timestamp, row in group)
    return sessions, membership, missing
