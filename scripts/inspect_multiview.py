"""Audit TR-6 capture-time clusters; do not turn them into independent specimens."""
import argparse
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.dataset_inspection import write_csv
from src.multiview_audit import candidate_sessions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gap-minutes", type=float, default=30)
    args = parser.parse_args()
    path = ROOT / "data/manifests/banana_inventory.csv"
    if not path.is_file():
        parser.error("Run python scripts/inspect_dataset.py first")
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    sessions, membership, missing = candidate_sessions(rows, args.gap_minutes)
    if not sessions:
        parser.error("No valid TR-6 timestamps found in the inventory")
    output = ROOT / "results/day2/multiview"
    write_csv(output / "candidate_sessions.csv", list(sessions[0]), sessions)
    write_csv(output / "candidate_membership.csv", list(membership[0]), membership)
    summary = {"session_gap_minutes": args.gap_minutes, "candidate_sessions": len(sessions),
               "images_with_timestamps": len(membership), "images_without_timestamps": missing,
               "session_sizes": sorted({s["image_count"] for s in sessions}),
               "label_conflict_sessions": sum(s["label_conflict"] == "true" for s in sessions),
               "verified_independent_items": 0,
               "decision": "Demonstration candidate only. Verify specimen and view identity before evaluating multiview accuracy; never split repeated sessions as independent items."}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return int(bool(missing))


if __name__ == "__main__":
    raise SystemExit(main())
