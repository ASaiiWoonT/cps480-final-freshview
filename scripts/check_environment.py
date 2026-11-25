"""Check imports, configuration, CPU arithmetic and optional CUDA arithmetic."""
import argparse
import importlib
from importlib.metadata import version
from pathlib import Path
import platform
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.runtime import configure_cache

PACKAGES = {
    "torch": "torch", "torchvision": "torchvision", "timm": "timm",
    "ultralytics": "ultralytics", "opencv-python": "cv2", "Pillow": "PIL",
    "numpy": "numpy", "pandas": "pandas", "scikit-learn": "sklearn",
    "matplotlib": "matplotlib", "streamlit": "streamlit", "jupyter": "jupyter_core",
    "ipykernel": "ipykernel", "pytest": "pytest", "PyYAML": "yaml", "tqdm": "tqdm",
    "requests": "requests",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-cuda", action="store_true")
    args = parser.parse_args()
    configure_cache()
    print(f"Python {platform.python_version()} on {platform.system()}: {sys.executable}")
    failures = []
    for package, module in PACKAGES.items():
        try:
            importlib.import_module(module)
            print(f"[OK] {package} {version(package)}")
        except Exception as error:
            failures.append(package)
            print(f"[FAIL] {package}: {error}")
    try:
        import torch
        from src.config import load_config
        config, classes = load_config(), load_config("classes")
        assert config["classifier"]["num_classes"] == len(classes["condition_classes"])
        assert abs(sum(config["dataset"].values()) - 1.0) < 1e-8
        assert set(classes["supported_produce"]) <= set(classes["recognition_candidates"])
        devices = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])
        if args.require_cuda and "cuda" not in devices:
            raise RuntimeError("CUDA is required but unavailable")
        for device in devices:
            matrix = torch.eye(4, device=device)
            assert torch.allclose(matrix @ matrix, matrix)
            print(f"[OK] {device} matrix multiplication")
        if "cuda" in devices:
            print(f"GPU: {torch.cuda.get_device_name(0)}; PyTorch CUDA runtime: {torch.version.cuda}")
    except Exception as error:
        failures.append("runtime/config")
        print(f"[FAIL] runtime/config: {error}")
    print("Environment passed." if not failures else f"Failed: {', '.join(failures)}")
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
