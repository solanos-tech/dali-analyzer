# Build and Run Runbook

## Requirements

- Python 3.12+
- Node.js 20+
- `uv` for backend dependency and command management
- `npm` for frontend dependency and scripts

## Run Backend Locally

```powershell
make dev-up
```

Default URL: `http://127.0.0.1:8000`.

## Backend Quality Checks

```powershell
cd backend
uv run ruff check .
uv run pytest
uv run mypy app
```

## Build Backend Package

```powershell
cd backend
uv build
```

Build artifacts are generated in `backend/dist/`.

## Run Frontend Locally

```powershell
make dev-check
make dev-down
```

## Environment and Release Commands

```powershell
make env-use ENV=dev
make env-show
make deploy
make release-prepare VERSION=X.Y.Z
make release-publish VERSION=X.Y.Z
make release-status VERSION=X.Y.Z
```

## Branch Hygiene Checklist

```powershell
# before work
git checkout main
git pull --ff-only origin main
git checkout -b codex/<feature-name>

# after merge to main (cleanup merged branches only)
git branch --merged main
git branch -d <local-merged-branch>
git push origin --delete <remote-merged-branch>
```
