# dali-analyzer backend

FastAPI backend exposing the DALI frames API.

## Endpoints

- `GET /health`
- `GET /api/frames?source=mock|serial`

## Run locally

```powershell
uv sync
uv run uvicorn app.main:app --reload
```

## Quality checks

```powershell
uv run ruff check .
uv run pytest
uv run mypy app
```

## Runtime config

- `CORS_ALLOW_ORIGINS` (comma-separated origins)
