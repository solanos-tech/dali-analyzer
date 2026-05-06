# Test Docs

Testing guidance and quality gates for the repository.

## Test Strategy

- Backend correctness: API behavior, decoder semantics, and contract shape.
- Frontend quality: lint/build integrity and runtime compatibility.
- Integration confidence: backend + frontend smoke behavior for merge and release flows.

## Standard Backend Checks

```powershell
cd backend
uv run ruff check .
uv run pytest
uv run mypy app
```

## Standard Frontend Checks

```powershell
cd frontend
npm install --no-audit --no-fund
npm run lint
npm run build
```

## Integration Smoke

- Workflow: `.github/workflows/integration-smoke.yml`
- Validates startup and baseline endpoints:
  - `GET /health`
  - `GET /api/frames?source=mock`

## Definition of Done (Testing)

- Lint/type/test checks pass for impacted runtime areas.
- New or changed behavior has at least one automated test or explicit rationale.
- Docs reflect changed behavior in the same PR.
- Backlog and iteration notes are updated for traceability.

## Scope Notes

- Unit and API behavior checks for backend.
- Type and lint quality gates.
- Smoke-level runtime validation for release workflows.
