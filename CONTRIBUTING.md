# Working together on FreshView

Start with [Team Member 2 onboarding](docs/team_member_2_onboarding.md) if you have not cloned and verified the project.

## Branches and responsibilities

| Branch | Purpose |
| --- | --- |
| `main` | Shared, reviewed working version |
| `feature/data-model` | Team Member 1: datasets, identification, segmentation, condition classifier |
| `feature/multiview-app` | Team Member 2: multiview, uncertainty, Streamlit |

These are the initial working branches, not already-provisioned accounts or enforced permissions. Create your branch locally from up-to-date `main`. For later separate tasks, use descriptive branch names such as `feature/view-disagreement`.

Discuss shared changes to `src/pipeline.py`, `src/images.py`, `configs/`, and requirements before both people edit them. Keep class order and error handling consistent with [the interface contract](docs/interface_contract.md).

## Before starting a work session

Run `git status`. Commit your intentional changes before switching or merging; do not discard uncommitted work just to make the command succeed.

For Team Member 2, with a clean working folder:

```bash
git switch feature/multiview-app
git fetch origin
```

If `origin/feature/multiview-app` already exists (check with `git branch -r`), first incorporate it using `git merge --no-edit origin/feature/multiview-app`. Then bring in the latest shared work:

```bash
git merge --no-edit origin/main
```

Team Member 1 uses `feature/data-model` instead. If Git reports a conflict, resolve it with your teammate or use `git merge --abort` to return to the pre-merge state. Do not force-push or delete files to bypass a conflict.

## Check and publish your changes

Use the activated project environment:

```bash
python -m pytest -q
git --no-pager diff
git status
git add .
git --no-pager diff --cached --stat
```

Review the staged files. Include source, tests, configs, documentation and reviewed manifests. Keep environments, credentials, datasets, downloaded weights and caches out of commits. Add relevant tests when implementing behavior; run `python -m pip check` and the environment script when changing dependencies.

Then replace the example commit message with a description of your actual work:

```bash
git commit -m "Document multiview dataset feasibility"
git push -u origin feature/multiview-app
```

Subsequent pushes from that branch can use `git push`. Team Member 1 substitutes their branch name.

On GitHub, open a pull request with **base: main** and **compare: your feature branch**. Explain what changed, how you checked it, and any remaining limitation. Ask your teammate to review it. Agree before merging changes to shared interfaces. This follows [GitHub's branch-and-review workflow](https://docs.github.com/en/get-started/using-github/github-flow); no automated checks or branch-protection rules are configured by these instructions.

If a push is rejected, fetch and merge the updated remote version of your own branch, resolve conflicts, retest and push again. The `--allow-unrelated-histories` option used during the original repository setup is not part of the normal team workflow.

## After a pull request is merged

With a clean working folder:

```bash
git switch main
git pull --ff-only origin main
```

Create a new task branch from this updated `main`, or merge `origin/main` into your existing ongoing feature branch before more work. If the old branch was deleted after a merge, create a new task branch rather than recreating an outdated branch from stale files.

## Help each other reproduce results

- Use project-relative dataset paths in manifests and code.
- Keep each person's virtual environment local; use `requirements.txt` for cross-machine setup.
- Do not overwrite the Linux/CUDA lock file with a different platform's package list.
- Record dataset sources, licenses and physical-item grouping before experiments.
- Share required data/checkpoint download instructions; those files do not arrive through Git.
- Treat `not_ready` as expected until model integration is implemented; never fabricate production predictions to make the UI appear complete.
