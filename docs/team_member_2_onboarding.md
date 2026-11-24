# Team Member 2 — FreshView onboarding

Your goal is to clone the shared project, start the preview app on your computer, and begin multiview/app work on your own branch. You do not need an NVIDIA GPU or a trained condition model to start.

The Linux CPU route below passed a fresh-clone installation, all five tests and both pretrained model checks on November 24, 2026. See the [verification record](day1_verification.md). Windows and macOS still need validation on your machine.

## 1. Get access

Repository: https://github.com/ASaiiWoonT/cps480-final-freshview

The owner should invite your GitHub account through the repository's **Settings → Collaborators → Add people**. Accept the invitation and confirm you can open the repository while signed in. Read access alone does not establish permission to push a branch. See [GitHub's collaborator instructions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository).

Install Git and Python 3.12 from their official installers or your OS package manager. VS Code with the Python extension is optional. On Windows, enable the Python launcher/PATH options during installation. Use a terminal in a directory where you keep your projects.

## 2. Clone once and create your branch

```bash
git clone https://github.com/ASaiiWoonT/cps480-final-freshview.git
cd cps480-final-freshview
git switch -c feature/multiview-app
```

If you already cloned it, open that folder instead of cloning again. If your local branch already exists, use `git switch feature/multiview-app`. If it exists only on GitHub, run `git fetch origin` and `git switch --track origin/feature/multiview-app`.

Set your own commit identity for this repository. Replace the examples with your name and your GitHub email (or GitHub-provided private email):

```bash
git config user.name "Your Name"
git config user.email "YOUR_GITHUB_EMAIL"
```

You are working in the existing shared repository. Do not run `git init` or add another `origin` remote. `git remote -v` should show the repository above.

## 3. Create your Python environment

Run only the block matching your operating system, from inside the cloned project folder.

### Windows — PowerShell

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
```

If PowerShell blocks activation, use Command Prompt with `.venv\Scripts\activate.bat`, or skip activation and replace `python` in all following commands with `.\.venv\Scripts\python.exe`. No change to your computer's execution policy is required.

### Linux or macOS — terminal

```bash
python3.12 --version
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Any compatible Python 3.12 patch release can be used; `.python-version` records the exact patch tested on Team Member 1's laptop. If your version manager requires that exact patch, install it or explicitly select your available Python 3.12 interpreter without changing the shared file.

Verify the interpreter:

```bash
python -c "import sys; print(sys.executable)"
```

Its path should include this project's `.venv`. In VS Code, use **Python: Select Interpreter** and choose that environment. Activate it again whenever you open a new terminal.

## 4. Install dependencies

Choose exactly one PyTorch command below. CPU is the simplest starting point for Team Member 2 on Linux/Windows, including computers that have a GPU.

**Linux or Windows — CPU:**

```bash
python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
```

**Linux or Windows — optional compatible NVIDIA GPU:**

```bash
python -m pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126
```

**macOS — supported hardware:**

```bash
python -m pip install torch==2.14.1 torchvision==0.29.1
```

These version pairs follow the [official PyTorch installation matrix](https://pytorch.org/get-started/previous-versions/). The project's automatic device selection currently supports CUDA or CPU; it does not select Apple's MPS accelerator. Windows/macOS instructions still need verification on the teammate's actual computer. If a wheel is unavailable for your hardware, report the OS, CPU architecture and Python version before changing shared requirements.

Then everyone runs:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

Use `requirements.txt` for cross-machine setup. The full `requirements-lock.txt` is Team Member 1's Linux/CUDA environment record, not the CPU or macOS install list. Do not replace that lock file with your machine's `pip freeze` output.

Allow time and disk space for the first installation; GPU libraries can take several GB. First use of either pretrained model downloads its weights. The app preview and basic tests do not need those weights or any dataset. Do not copy Team Member 1's `.venv` to your computer.

## 5. Verify and launch

```bash
python scripts/check_environment.py
python -m pytest -q
python -m streamlit run app/streamlit_app.py
```

Expected results: `Environment passed.`, all current tests passing, and a FreshView page at http://localhost:8501. CPU-only operation is expected; do not add `--require-cuda` unless you deliberately installed and want to verify CUDA.

Upload one to three JPEG/PNG photos to check previews. The assessment button is intentionally disabled while the condition model is untrained. Stop the server with Ctrl+C.

For the full Day 1 model check, run separately:

```bash
python scripts/test_yolo.py --device cpu
python scripts/test_classifier.py --device cpu
```

These download the public pretrained models if needed. YOLO uses a blank image by default, so zero detections are normal. ConvNeXt should output shape `(1, 2)`; this verifies execution, not freshness accuracy. For an offline architecture-only check, use `python scripts/test_classifier.py --device cpu --no-pretrained`.

## 6. Know where to work

| Responsibility | Files | Current state |
| --- | --- | --- |
| Uploads, previews and eventual results UI | `app/streamlit_app.py`, `src/images.py` | Working preview and image validation |
| Combine 1–3 views of the same item | `src/multiview.py` | Placeholder |
| Disagreement and abstention | `src/uncertainty.py` | Placeholder; thresholds not selected |
| Vision integration boundary | `src/pipeline.py`, `docs/interface_contract.md` | Stub returns `not_ready`, with no predictions |
| App/fusion/uncertainty tests | `tests/` | Five baseline tests; extend as features are implemented |
| Dataset grouping research | `docs/dataset_sources.md`, `data/manifests/` | Worksheet and empty manifest directory |

Team Member 1 owns dataset preparation, identification, segmentation and condition-model training. Coordinate changes to `src/pipeline.py`, `src/images.py`, `configs/`, and shared dependencies with each other.

Read [the interface contract](interface_contract.md) before connecting modules. Class order is `apparently_fresh` (0), `visible_spoilage` (1). Banana is provisional. Do not present test vectors or the untrained classifier as real assessments. Synthetic probability vectors are appropriate in isolated fusion tests, clearly labeled as test data.

Day 2 for you is checking whether public datasets have genuine views of the same physical item and suitable condition labels. Record evidence in the dataset worksheet. Do not construct multiview groups from unrelated images. Model training and final integration are later-day tasks.

## 7. Share changes and stay in sync

Follow [CONTRIBUTING.md](../CONTRIBUTING.md) for updating your branch, committing, pushing and opening a pull request. Your first meaningful contribution can be a documented multiview feasibility finding; do not change application behavior merely to test Git access.

## Troubleshooting

| Symptom | Next action |
| --- | --- |
| Repository not found / permission denied | Check the URL, signed-in account and accepted collaborator invitation; read access may differ from push access. |
| Git asks for an HTTPS password | Use supported GitHub authentication (credential helper, GitHub CLI browser sign-in, or a personal access token); do not use your account password or paste tokens into project files. See [GitHub authentication](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github). |
| `python3.12` or `py -3.12` not found | Install Python 3.12, reopen the terminal, and check the version again. |
| Missing `venv` / `ensurepip` on Linux | Install your distribution's venv package matching Python 3.12, then recreate the unfinished environment. |
| `ModuleNotFoundError` | Confirm the interpreter points into `.venv`, then rerun dependency installation. |
| CUDA unavailable | Use the CPU commands; CUDA is optional for your initial tasks. |
| OpenCV cannot load `libGL.so.1` on Linux | Install your distribution's GL runtime (`libgl1` on Ubuntu/Debian), then rerun the environment check. |
| Port 8501 is already in use | Stop the previous app or run `python -m streamlit run app/streamlit_app.py --server.port 8502`. |
| Git shows a scrolling output viewer | Press `q` to exit; if it says it is waiting for data, press Ctrl+C and then `q`. |
| Push rejected / merge conflict | Follow the update/conflict instructions in CONTRIBUTING.md; preserve both teammates' work. |

## Ready-to-work checklist

- [ ] I can open the shared repository and have accepted collaborator access.
- [ ] My branch is `feature/multiview-app`, not `main`.
- [ ] My interpreter points into my own `.venv`.
- [ ] Dependency and environment checks pass.
- [ ] The current tests pass and the Streamlit preview opens.
- [ ] Both model smoke checks pass, or any download/platform blocker is recorded.
- [ ] We have reviewed labels, image inputs, failure statuses and file responsibilities together.
- [ ] I know how to push my branch and open a pull request.

Tell Team Member 1 your OS, Python version, CPU/GPU choice, check results and any blocker. Do not include credentials.
