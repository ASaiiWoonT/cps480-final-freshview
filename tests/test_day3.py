from collections import defaultdict

from scripts.prepare_dataset import ROOT, assign_groups, load_config, read_rows


def test_published_split_reproduces_review_and_keeps_groups_together():
    folder = ROOT / "data/manifests"
    review = read_rows(folder / "day3_scene_review.csv")
    selected = read_rows(folder / "day3_splits.csv")
    assert {r["sha256"] for r in selected} == {r["sha256"] for r in review if r["decision"] == "include"}
    assert len({r["sha256"] for r in selected}) == len(selected)
    config = load_config()
    by_group = assign_groups(selected, config["dataset"], config["seed"])
    assert all(by_group[r["capture_group"]] == r["split"] for r in selected)
    labels = defaultdict(set)
    for r in selected:
        labels[r["split"]].add(r["condition_label"])
    assert set(labels) == {"train", "validation", "test"}
    assert all(values == {"apparently_fresh", "visible_spoilage"} for values in labels.values())


def test_demo_views_share_session_and_stay_outside_classifier_split():
    folder = ROOT / "data/manifests"
    membership = {r["image_path"]: r["candidate_session_id"] for r in
                  read_rows(ROOT / "results/day2/multiview/candidate_membership.csv")}
    training_paths = {r["image_path"] for r in read_rows(folder / "day3_splits.csv")}
    sessions = defaultdict(list)
    for r in read_rows(folder / "day3_demo_views.csv"):
        assert r["image_path"] not in training_paths
        assert membership[r["image_path"]] == r["session"]
        sessions[r["session"]].append(int(r["view_order"]))
    assert len(sessions) == 19
    assert all(order == [1, 2, 3] for order in sessions.values())
