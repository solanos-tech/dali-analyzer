# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Added

- Added frontend-backend integration in React with API fetching, source switching, and 1-second live polling.
- Added frontend API layer and config support via `VITE_API_BASE_URL` and `VITE_API_PROXY_TARGET`.
- Added frontend CI workflow: `.github/workflows/frontend-ci.yml`.
- Added integration smoke workflow: `.github/workflows/integration-smoke.yml`.
- Added frontend deploy workflow: `.github/workflows/frontend-deploy.yml`.
- Added frontend release workflow with `frontend-v*` tags: `.github/workflows/frontend-release.yml`.
- Added ADR for mandatory branch/PR workflow: `docs/adr/ADR-0003-branch-pr-mandatory.md`.
- Added release/versioning ADR: `docs/adr/ADR-0004-release-versioning-policy.md`.
- Added agent release/versioning policy doc: `docs/agent/release-versioning.md`.

### Changed

- Converted backend to API-only mode by removing embedded HTML UI routes.
- Added explicit response model and CORS support in backend API.
- Updated backend CI smoke checks to validate frames endpoint.
- Updated backend release tags from `v*` to `backend-v*`.
- Updated agent operating docs (`AGENTS.md`, `docs/agent/interrupt-flow.md`, `docs/tasks/task-template.md`) to enforce branch + PR flow.
- Updated agent docs to enforce synchronized backend/frontend version bumps and strict release tag patterns.
