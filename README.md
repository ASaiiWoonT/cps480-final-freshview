# FreshView

Multiview produce identification, segmentation, and visible-condition assessment for CPS480.

## Day 1 status

This is an environment and interface starter, not a trained freshness system. The app accepts 1–3 JPEG/PNG views of the same item and previews them. YOLO11 Nano Segmentation and ConvNeXt V2 Atto have separate verification scripts. The new two-class condition head requires training before its output can be used.

Banana is the provisional first produce type, pending Day 2 dataset inspection. Labels are `apparently_fresh` (0) and `visible_spoilage` (1). Visual condition is not a food-safety or shelf-life determination.

## Start on this laptop

Open a terminal and run:

```bash
cd "/home/sai-woon-tip/Documents/CPS480 Final Project FreshView"
source .venv/bin/activate
python -m streamlit run app/streamlit_app.py
```

Open http://localhost:8501. Stop with Ctrl+C. Activate the environment again in each new terminal. In VS Code, select `.venv/bin/python` using **Python: Select Interpreter**.

The project uses Python 3.12 in `.venv`; the system Python is unchanged. See `docs/day1_verification.md` for actual machine details and test results.

## Re-create the environment on another machine

Install Python 3.12 first. Run these commands from the project folder, substituting your Python 3.12 command if needed:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Select **one** PyTorch installation for your hardware:

```bash
# NVIDIA / Linux: the combination verified on this laptop
python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126

# CPU-only alternative (Linux/Windows)
python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
```

Then install the other dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip check
python scripts/check_environment.py
```

Windows activation: `.venv\Scripts\activate`. For macOS or other GPU platforms, use the [official PyTorch instructions](https://pytorch.org/get-started/previous-versions/) for the matching `torch`/`torchvision` pair. A standalone CUDA toolkit is not needed for the prebuilt PyTorch wheels used here.

`requirements.txt` records direct dependencies. `requirements-lock.txt` records the full tested Linux/Python 3.12/CUDA 12.6 environment, including GPU-specific dependencies. To reproduce that same environment use `python -m pip install -r requirements-lock.txt --extra-index-url https://download.pytorch.org/whl/cu126`; do not use that machine-specific lock unchanged on CPU-only or macOS machines.

## Verify the setup

```bash
python -m pip check
python scripts/check_environment.py --require-cuda
python scripts/test_yolo.py --device cuda
python scripts/test_classifier.py --device cuda
python scripts/test_yolo.py --device cpu
python scripts/test_classifier.py --device cpu
python -m pytest -q
```

On a CPU-only machine omit `--require-cuda` and the CUDA commands. First model use downloads public pretrained weights. YOLO weights go into `models/`; Hugging Face and PyTorch caches default to `.cache/` inside this project. Existing cache environment overrides are respected. `--no-pretrained` runs an offline ConvNeXt architecture check, without verifying pretrained weights.

YOLO's default smoke input is a blank synthetic image: it verifies execution, not produce recognition or mask quality. To test a permitted real photo:

```bash
python scripts/test_yolo.py --image data/raw/test_produce.jpg
```

Inspect annotated output in `results/smoke/yolo*`. The confidence threshold of 0.25 is provisional. No real produce photo or training dataset is bundled.

## Layout and team handoff

| Path | Purpose |
| --- | --- |
| `app/` | Streamlit upload/preview skeleton, for Team Member 2 |
| `src/` | Image handling, shared configuration, runtime helpers, pipeline interface and future module placeholders |
| `scripts/` | Environment/model checks and placeholders for later dataset/training work |
| `configs/` | Class mapping and provisional experiment settings |
| `data/raw/`, `data/processed/` | Local datasets, excluded from Git |
| `data/manifests/` | Trackable dataset metadata and split records |
| `models/` | Downloaded/trained weights, excluded from Git |
| `results/` | Evaluation outputs; temporary smoke results excluded |
| `tests/` | Offline image handling, placeholder contract and app startup checks |
| `docs/` | Interface agreement, dataset worksheet and verification record |
| `notebooks/`, `paper/` | Exploration and paper materials |

`src.pipeline.analyze_image` returns `not_ready` with no fabricated predictions. The proposed eventual interface is documented in `docs/interface_contract.md`. Training, segmentation extraction, fusion and uncertainty logic are later-day work; their placeholders explicitly say so. Uncertainty thresholds remain unset until validation.

## Your manual GitHub step

No repository has been initialized, created, committed, or pushed by this setup. When you are ready, create your repository and add the source/configuration/documentation files yourself. Review the selected files before uploading.

Do not upload `.venv/`, `.cache/`, datasets, model weights, credentials or temporary smoke results. **GitHub's browser upload does not apply this local `.gitignore` automatically.** Include both requirements files, `.python-version`, `.gitignore`, `pytest.ini` and the source folders. Dotfiles may be hidden in your file picker. Empty folders are represented by `.gitkeep` files.

## Day 2 next steps

Use `docs/dataset_sources.md` to record sources, licenses, exact labels and item/view grouping. Agree on supported produce and the interface with your teammate. Detect duplicates and split by physical item/source where applicable before training. Do not group unrelated photographs into artificial multiview items.

## Model references

- [YOLO11 model documentation](https://docs.ultralytics.com/models/yolo11/)
- [ConvNeXt V2 Atto model card](https://huggingface.co/timm/convnextv2_atto.fcmae_ft_in1k)
- [PyTorch installation combinations](https://pytorch.org/get-started/previous-versions/)

Record and review upstream model and dataset license requirements before redistribution; no project license is selected by this starter.
