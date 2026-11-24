"""Verify ConvNeXt V2 with a new, untrained two-class head."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import load_config
from src.runtime import configure_cache, select_device


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--no-pretrained", action="store_true", help="Offline architecture test only")
    args = parser.parse_args()
    configure_cache()
    import timm
    import torch
    config = load_config()
    spec = config["classifier"]
    torch.manual_seed(config["seed"])
    device = select_device(args.device)
    pretrained = spec["pretrained"] and not args.no_pretrained
    model = timm.create_model(spec["architecture"], pretrained=pretrained,
                              num_classes=spec["num_classes"]).to(device).eval()
    sample = torch.randn(1, 3, spec["image_size"], spec["image_size"], device=device)
    with torch.inference_mode():
        logits = model(sample)
    assert logits.shape == (1, spec["num_classes"]) and torch.isfinite(logits).all()
    print(f"ConvNeXt V2 passed on {device}; pretrained backbone: {pretrained}; output: {tuple(logits.shape)}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print("The condition head is untrained. This test does not assess freshness.")


if __name__ == "__main__":
    main()
