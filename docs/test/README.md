# Test Docs

Testing guidance and quality gates for the repository.

## Standard Backend Checks

```powershell
cd backend
uv run ruff check .
uv run pytest
uv run mypy app
```

## Scope

- Unit and API behavior checks for backend.
- Type and lint quality gates.
- Smoke-level runtime validation for release workflows.
