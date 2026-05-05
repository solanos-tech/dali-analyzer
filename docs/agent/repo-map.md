# Repository Map

## Top-Level Layout

- `backend/` - FastAPI application, packaging, and backend tests
- `frontend/` - React + Vite application
- `.github/workflows/` - CI and release pipelines
- `docs/` - agent-first project documentation

## Backend

- Entry point: `backend/app/main.py`
- Health endpoint: `GET /health`
- Frames endpoint: `GET /api/frames?source=mock|serial`
- Project config: `backend/pyproject.toml`
- Tests: `backend/tests/`

## Frontend

- Entry point: `frontend/src/main.tsx`
- Main component: `frontend/src/App.tsx`

## CI and Release

- CI workflows:
  - `.github/workflows/backend-ci.yml`
  - `.github/workflows/frontend-ci.yml`
  - `.github/workflows/integration-smoke.yml`
- Deployment workflow:
  - `.github/workflows/deploy-dev.yml`
- Release workflow:
  - `.github/workflows/unified-release.yml`
