"""Shared local caches and explicit CPU/GPU selection for verification."""
import os

from src.config import ROOT


def configure_cache():
    for key, directory in {
        "HF_HOME": ".cache/huggingface",
        "TORCH_HOME": ".cache/torch",
        "YOLO_CONFIG_DIR": ".cache/ultralytics",
    }.items():
        os.environ.setdefault(key, str(ROOT / directory))
        os.makedirs(os.environ[key], exist_ok=True)


def select_device(requested="auto"):
    import torch

    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable. Use --device cpu or check PyTorch.")
    if requested not in {"cpu", "cuda"}:
        raise ValueError(f"Unknown device: {requested}")
    return requested
