# dali-analyzer backend

FastAPI backend exposing the DALI frames API.

## Run Backend Locally

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

API URL: `http://127.0.0.1:8000`

## Endpoints

- `GET /health`
- `GET /api/frames?source=mock|serial`

## Quality checks

```powershell
uv run ruff check .
uv run pytest
uv run mypy app
```

## Runtime config

- `CORS_ALLOW_ORIGINS` (comma-separated origins)

## Version and Release

- Source of backend version: `backend/pyproject.toml` (`[project].version`)
- Release tag pattern: `backend-vX.Y.Z`
- Successful release workflow should be followed by auto-log docs PR updates.
