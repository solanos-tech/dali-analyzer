# Repository Map

## Top-Level Layout

- `backend/` - FastAPI application, packaging, and backend tests
- `frontend/` - React + Vite application
- `.github/workflows/` - CI and release pipelines
- `packaging/runtime/` - Runtime package templates (launchers, config, README)
- `scripts/release/` - Runtime/source archive build scripts for release workflow
- `docs/` - agent-first project documentation
  - `docs/cicd/README.md` - CI/CD flow and release policy map
  - `docs/tasks/backlog.md` - active backlog
  - `docs/tasks/done-log.md` - completion history
  - `docs/tasks/iterations/` - per-iteration notes

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
- CI triage guidance:
  - `docs/agent/ci-triage-playbook.md` (read first after PR creation)
- Deployment workflow:
  - `.github/workflows/deploy-dev.yml`
- Release workflow:
  - `.github/workflows/unified-release.yml`
  - Draft-first release with blocking acceptance (Linux + Windows) before publish
  - Release assets: `runtime-vX.Y.Z.zip`, `source-vX.Y.Z.zip`
