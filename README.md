# dali-analyzer

This repository is prepared for iterative human + AI collaboration.

## Quick Start

- Backend: `cd backend && uv sync && uv run uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm ci && npm run dev`

## Runtime Config

- Frontend API base URL (optional): `VITE_API_BASE_URL`
- Frontend dev proxy target: `VITE_API_PROXY_TARGET` (default `http://127.0.0.1:8000`)
- Backend CORS allow list: `CORS_ALLOW_ORIGINS` (comma-separated)

## Documentation

- [agents.md](agents.md) - agent runtime entrypoint and mandatory branch/PR workflow
- [docs/README.md](docs/README.md) - documentation map and structure
- [CHANGELOG.md](CHANGELOG.md) - change history
