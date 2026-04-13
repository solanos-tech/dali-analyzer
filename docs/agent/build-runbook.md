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
npm ci
npm run dev
```
