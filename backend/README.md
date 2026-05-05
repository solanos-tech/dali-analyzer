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
- `GET /api/frames?source=mock|serial` (legacy v1)
- `GET /api/v2/logs`
- `GET /api/v2/frames?source=simulated_log|serial&log_name=<file>&limit=<n>`
- `GET /api/v2/stream?source=simulated_log|serial&log_name=<file>` (SSE)
- `GET /api/v2/serial/ports`
- `GET /api/v2/serial/status`
- `POST /api/v2/serial/connect`
- `POST /api/v2/serial/disconnect`
- `POST /api/v2/admin/reload-specs`

## Quality checks

```powershell
uv run ruff check .
uv run pytest
uv run mypy app
```

## Runtime config

- `CORS_ALLOW_ORIGINS` (comma-separated origins)
- `SIM_LOG_DIR` optional directory for simulated sniffer log files
- `SERIAL_PORT` optional serial device (for hardware mode)
- `SERIAL_BAUDRATE` optional baud rate (default `115200`)

## Version and Release

- Source of backend version: `backend/pyproject.toml` (`[project].version`)
- Release tag pattern: `vX.Y.Z` (unified release)
- Successful release workflow should be followed by auto-log docs PR updates.
