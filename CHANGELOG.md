# Changelog

All notable changes to this project are documented in this file.

The format is inspired by Keep a Changelog and Semantic Versioning.

## [Unreleased]

## [0.9.2] - 2026-05-05

### Fixed

- Fixed Windows runtime stop launcher to be idempotent during acceptance shutdown:
  - `packaging/runtime/launchers/stop-windows.ps1`
- Acceptance stop step no longer fails when tracked backend PID is already gone.

## [0.9.1] - 2026-05-05

### Added

- Unified release now publishes two ZIP artifacts:
  - `runtime-vX.Y.Z.zip`
  - `source-vX.Y.Z.zip`
- Added runtime package template content for release assembly:
  - `packaging/runtime/README.md`
  - `packaging/runtime/config/runtime-config.json`
  - `packaging/runtime/launchers/*`
- Added release packaging scripts:
  - `scripts/release/build-runtime-package.sh`
  - `scripts/release/build-source-package.sh`

### Changed

- Updated `Unified Release` workflow to draft-first publishing with blocking Linux/Windows acceptance checks based on downloaded runtime asset.
- Backend now supports serving frontend static runtime bundle with SPA fallback and runtime config endpoint.
- Frontend now supports runtime API base URL override via `config/runtime-config.json` for split-host deployments.

## [0.9.0] - 2026-05-05

### Changed

- Bumped aligned backend/frontend release version to `0.9.0`.
- Improved Windows local runtime scripts:
  - `scripts/ops/dev-up.ps1`
  - `scripts/ops/dev-down.ps1`

### Added

- Added human-readable CI/CD and policy documentation with Mermaid diagrams:
  - `docs/ci-cd.md`
- Added Windows one-script local launcher support:
  - `scripts/ops/dev-up.ps1`
  - `scripts/ops/dev-down.ps1`
- Added default simulated sniffer log file required by frontend v2 simulated mode:
  - `docs/standards/sniffer_log_example.log`
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
- Added serial port discovery and connection-control API endpoints (`/api/v2/serial/ports`, `/serial/status`, `/serial/connect`, `/serial/disconnect`).
- Added frontend serial connection controls (port refresh/select, connect/disconnect status, and live-stream guard).
- Added serial command endpoint `POST /api/v2/serial/command` with `sniffer_on` support for connected sessions.
- Added frontend status-panel actions to clear in-memory frames and export current log buffer as `.log`.
- Added DALI-2 semantic upgrades for forward24 decoding: `forward24_input_notification`, helper-range classification, and instance query routing.
- Added runtime instance-context endpoint `GET /api/v2/context/instances`.
- Added repository closeout audit report: `docs/tasks/repo-hygiene-closeout-2026-04-28.md`.
- Added future English migration/structure plan for DALI standard doc: `docs/tasks/dali-doc-english-migration-plan.md`.
- Added traceability backup copy for DALI standards source text: `docs/standards/dali.pl.md`.

### Changed

- Updated root README and docs map to include CI/CD overview and launcher usage for Linux and Windows.
- Updated launcher scripts to fail fast with explicit diagnostics when startup requirements are missing or services are not ready:
  - `scripts/ops/dev-up.sh`
  - `scripts/ops/dev-up.ps1`
- Updated Linux startup/check probes to support both `curl` and `wget`:
  - `scripts/ops/dev-up.sh`
  - `scripts/ops/dev-check.sh`
- Updated `docs/agent/repo-map.md` CI/CD section to match current workflow files.
- Updated `.gitignore` to keep `docs/standards/sniffer_log_example.log` versioned.
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
- Updated runbook with branch hygiene checklist for merged-branch cleanup workflow.
- Fixed frontend `Time` column to calculate delta from the oldest visible frame timestamp (after filters), removing all-zero live values.
- Updated live serial start flow to send `Sniffer on` before opening SSE stream.
- Extended decoded frame contract with semantic metadata (`semantic_level`, `semantic_name`, `semantic_reason`) and new decode status `decoded_generic`.
