"""Resolve project resources independently of the current working directory."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_config(name="experiment"):
    if name not in {"experiment", "classes"}:
        raise ValueError(f"Unknown configuration: {name}")
    with (ROOT / "configs" / f"{name}.yaml").open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)
