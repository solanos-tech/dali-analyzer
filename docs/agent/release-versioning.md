# Release and Versioning Policy

This policy defines mandatory versioning, tagging, and release behavior for agents and contributors.

## Version Bump Rule

For release-related work:

- Update backend version in `backend/pyproject.toml` (`[project].version`).
- Update frontend version in `frontend/package.json` (`version`).
- Keep versions aligned by default (same `X.Y.Z`).

If separate backend/frontend versions are required, this must be explicitly requested and documented in the PR.

## Tag Rule

Release workflows are tag-driven and require exact patterns:

- Backend release trigger: `backend-vX.Y.Z`
- Frontend release trigger: `frontend-vX.Y.Z`

Optional informational tag:

- `vX.Y.Z` (does not trigger release workflows)

Examples:

- `backend-v0.1.6`
- `frontend-v0.1.6`
- `v0.1.6` (informational only)

Invalid release tags (do not trigger expected workflows):

- `v.0.1.6`
- `backend-0.1.6`
- `frontend_0.1.6`

## Release Checklist

1. Confirm branch + PR workflow is used.
2. Bump versions in backend and frontend.
3. Update `CHANGELOG.md`.
4. Merge PR to `main`.
5. Create and push release tags:
   - `backend-vX.Y.Z`
   - `frontend-vX.Y.Z`
6. Verify release workflows completed successfully.
