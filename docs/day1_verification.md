# Day 1 verification — November 24, 2026

## Local setup

- Project: `/home/sai-woon-tip/Documents/CPS480 Final Project FreshView`
- Existing state: the requested project folders existed and contained no files. No pre-existing project work was overwritten.
- Operating system: Ubuntu 26.04.1 LTS, Linux x86_64.
- System Python: 3.14.4, left unchanged.
- Project Python: 3.12.14, isolated in `.venv`, using the already installed Python 3.12 interpreter.
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU, 8,188 MiB reported memory.
- NVIDIA driver: 595.99.02. The driver reports CUDA compatibility up to 13.2; the installed PyTorch wheel uses CUDA 12.6.
- PyTorch: 2.14.1+cu126; torchvision: 0.29.1+cu126.
- Direct dependencies are pinned in `requirements.txt`; all 169 installed distributions reported by `pip freeze` are in `requirements-lock.txt`.
- The environment occupies approximately 7.8 GB; local model caches approximately 15 MB and YOLO weights approximately 6 MB, excluding pip's download cache.

## Completed checks

| Check | Observed result |
| --- | --- |
| Python compilation of app, source, scripts and tests | Passed |
| `python -m pip check` | No broken requirements found |
| `python scripts/check_environment.py --require-cuda` | All 17 dependency imports passed; configuration checks and CPU/CUDA matrix arithmetic passed |
| `python scripts/test_yolo.py --device cuda` | Pretrained segmentation model downloaded and inference passed |
| `python scripts/test_yolo.py --device cpu` | CPU inference passed |
| `python scripts/test_classifier.py --device cuda` | Pretrained backbone loaded; finite output shape `(1, 2)` |
| `python scripts/test_classifier.py --device cpu` | Pretrained backbone loaded; finite output shape `(1, 2)` |
| `python -m pytest -q` | 5 passed |
| Temporary Streamlit server | Health endpoint and root page both returned HTTP 200; server was stopped afterward |

The automated tests cover image decoding/RGB conversion, corrupt and oversized uploads, the no-predictions pipeline contract, and Streamlit startup with assessment disabled.

YOLO exposed the expected COCO produce categories: banana (46), apple (47), orange (49), broccoli (50), carrot (51). Both YOLO runs used a blank synthetic image and correctly completed with zero detections. **Produce recognition accuracy and segmentation-mask quality have not been tested on a real photo.** Use the README's `--image` command when a permitted sample is available.

ConvNeXt V2 Atto has 3,388,042 parameters with the two-class head. That head is newly initialized and untrained; the smoke outputs are not freshness predictions. Hugging Face emitted an unauthenticated-download rate-limit advisory, but the public weights downloaded successfully without a token.

## Downloaded model record

- YOLO file: `models/yolo11n-seg.pt`
- Source: `https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11n-seg.pt`
- SHA-256: `55ed65c56c91713d23e8402371c6c49a6fd84f257f7dce452e8d70e41dcbe152`
- ConvNeXt source: `timm/convnextv2_atto.fcmae_ft_in1k` on Hugging Face
- Cached revision: `2de59190576d00653aabde4bcd4af7525a93ad1b`
- `model.safetensors` SHA-256: `6389c2f5a427b01a922e66e6d352c707424cccb62390c6936bc612e3d10b7ebb`

These hashes identify the downloaded artifacts for later comparison; they are not independent signatures. Model weights and caches are excluded by `.gitignore`.

## Remaining project work

The Day 1 local environment and upload skeleton are ready. The user will handle GitHub manually; no `.git` directory, repository, commit, remote, or push was created. No datasets were downloaded. Dataset selection, real-photo inspection, training, extraction, multiview fusion, uncertainty validation and application integration remain later-day work.

See `README.md` for launch/reproduction instructions, `docs/interface_contract.md` for the proposed teammate handoff and `docs/dataset_sources.md` for the Day 2 worksheet.
