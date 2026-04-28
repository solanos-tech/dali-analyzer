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
- Added agent learning-loop ADR: `docs/adr/ADR-0005-agent-learning-loop.md`.
- Added operational logs:
  - `docs/agent/knowledge-log.md`
  - `docs/agent/decision-log.md`
- Added automation workflows:
  - `.github/workflows/auto-logs-on-pr-merge.yml`
  - `.github/workflows/auto-logs-on-release-success.yml`
- Added backend DALI decoder v2 architecture driven by JSON spec and schema under `backend/app/specs`.
- Added backend decoder pipeline modules for frame classification, opcode lookup, context handling, and transaction correlation.
- Added new backend v2 endpoints for log listing, decoded snapshot, SSE streaming, and spec reload.
- Added simulated log source mode that replays `sniffer` logs using `ts_ms` timing with loop playback.
- Added backend tests for decoder spec validation and v2 API contracts.
- Added frontend split-view monitoring UI with semantic badges, filters, detail panel, and live SSE fallback.

### Changed

- Converted backend to API-only mode by removing embedded HTML UI routes.
- Added explicit response model and CORS support in backend API.
- Updated backend CI smoke checks to validate frames endpoint.
- Updated backend release tags from `v*` to `backend-v*`.
- Updated agent operating docs (`AGENTS.md`, `docs/agent/interrupt-flow.md`, `docs/tasks/task-template.md`) to enforce branch + PR flow.
- Updated agent docs to enforce synchronized backend/frontend version bumps and strict release tag patterns.
- Updated agent docs and templates to require post-merge and post-release knowledge/decision logging.
- Updated root/backend/frontend README files with clearer run instructions and automatic logging behavior.
- Bumped release versions for backend/frontend to `0.1.7`.
- Fixed malformed backend `pyproject.toml` version field to restore valid TOML parsing for toolchain checks.
- Updated backend and frontend module docs to describe the v2 decoded frame contract and source modes.
