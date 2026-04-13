# dali-analyzer

This repository is prepared for iterative human + AI collaboration.

## Start Here

1. Run backend API.
2. Run frontend UI.
3. Verify `/health` and live frames in the browser.

## Run Backend

- Backend: `cd backend && uv sync && uv run uvicorn app.main:app --reload`

Backend URL: `http://127.0.0.1:8000`

## Run Frontend

- Frontend: `cd frontend && npm install --no-audit --no-fund && npm run dev`

Frontend URL: `http://127.0.0.1:5173`

## Runtime Config

- Frontend API base URL (optional): `VITE_API_BASE_URL`
- Frontend dev proxy target: `VITE_API_PROXY_TARGET` (default `http://127.0.0.1:8000`)
- Backend CORS allow list: `CORS_ALLOW_ORIGINS` (comma-separated)

## Release Tags

- Backend release trigger tag: `backend-vX.Y.Z`
- Frontend release trigger tag: `frontend-vX.Y.Z`
- Informational tag only: `vX.Y.Z`

## Automatic Logs

After merged PRs and successful release workflows, automation creates follow-up docs PRs that update:

- `docs/agent/knowledge-log.md`
- `docs/agent/decision-log.md`

## Documentation

- [agents.md](agents.md) - agent runtime entrypoint and mandatory branch/PR workflow
- [docs/README.md](docs/README.md) - documentation map and structure
- [CHANGELOG.md](CHANGELOG.md) - change history
