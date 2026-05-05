# Release and Versioning Policy

This policy defines mandatory versioning, tagging, and release behavior for agents and contributors.

## Version Bump Rule

For release-related work:

- Update backend version in `backend/pyproject.toml` (`[project].version`).
- Update frontend version in `frontend/package.json` (`version`).
- Keep versions aligned by default (same `X.Y.Z`).

If separate backend/frontend versions are required, this must be explicitly requested and documented in the PR.

## Tag Rule

Release workflow is tag-driven and requires exact pattern:

- Unified release trigger: `vX.Y.Z`
- Tag must point to commit reachable from `main`

Examples:

- `v0.1.6`

Invalid release tags (do not trigger expected workflows):

- `v.0.1.6`
- `backend-v0.1.6`
- `frontend-v0.1.6`

## Release Checklist

1. Confirm branch + PR workflow is used.
2. Bump versions in backend and frontend.
3. Update `CHANGELOG.md`.
4. Merge PR to `main`.
5. Run preflight:
   - `make release-prepare VERSION=X.Y.Z`
6. Publish release:
   - `make release-publish VERSION=X.Y.Z`
7. Verify release status:
   - `make release-status VERSION=X.Y.Z`
8. Ensure follow-up docs PR is generated for:
   - `docs/agent/knowledge-log.md`
   - `docs/agent/decision-log.md`
