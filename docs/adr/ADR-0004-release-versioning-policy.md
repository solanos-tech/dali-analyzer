# ADR-0004: Release Versioning and Tagging Policy

- Status: accepted
- Date: 2026-04-13

## Context

Release workflows are tag-based. Inconsistent tag names and unsynchronized frontend/backend versions cause missed releases and confusion.

## Decision

Define repository-level release policy:

1. For release work, update:
   - `backend/pyproject.toml` version
   - `frontend/package.json` version
2. Keep versions aligned by default (`X.Y.Z`).
3. Use strict release tags:
   - Backend: `backend-vX.Y.Z`
   - Frontend: `frontend-vX.Y.Z`
4. Treat `vX.Y.Z` as informational only unless workflows are explicitly changed.

## Consequences

- Release automation becomes predictable.
- Build/release trigger failures due to tag format are reduced.
- Version drift between backend and frontend is controlled by default.
