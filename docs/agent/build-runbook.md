# Build and Run Runbook

## Requirements

- Python 3.12+
- Node.js 20+
- `uv` for backend dependency and command management
- `npm` for frontend dependency and scripts

## Run Backend Locally

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
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
cd frontend
npm install --no-audit --no-fund
npm run dev
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
