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
3. Use a single strict release tag:
   - Unified release: `vX.Y.Z`
4. Release tag must point to a commit reachable from `main`.

## Consequences

- Release automation becomes predictable with one release artifact set.
- Build/release trigger failures due to tag mismatch are reduced.
- Version drift between backend and frontend is controlled by default.
