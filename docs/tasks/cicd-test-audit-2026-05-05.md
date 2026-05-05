# CI/CD and Test Audit - 2026-05-05

## Purpose

This document audits the current automated test and CI/CD setup. It is intentionally analysis-only: no implementation changes are proposed here as immediate work. The goal is to identify what is healthy, where risk remains, and what metric can be used to judge whether test coverage and automation are sufficient for this repository.

## Current State

### Backend tests and gates

- Backend CI runs `ruff`, `pytest`, and `mypy` on pull requests that touch `backend/**` or the backend workflow.
- Backend pytest currently collects 20 tests:
  - health and legacy frame endpoint shape checks,
  - decoder spec validation,
  - v2 log/frame endpoints,
  - serial connect/status/command behavior with test doubles,
  - streaming event smoke,
  - spec reload endpoint.
- Backend `main` pushes also build the wheel and run an installed-wheel smoke check.
- The wheel smoke now covers `/health`, `/api/frames?source=mock`, and `/api/v2/logs`, which protects against missing package-data regressions like the decoder spec omission found during the `v0.9.2` runtime validation.

### Frontend tests and gates

- Frontend CI runs `npm ci`, `npm run lint`, and `npm run build`.
- There are no application-owned frontend unit, component, interaction, or browser tests.
- TypeScript build and lint are useful structural gates, but they do not validate user workflows such as source switching, live stream state, serial controls, log selection, filter behavior, error messages, or runtime config behavior.

### Integration and release automation

- Integration smoke builds frontend, starts backend, then checks `/health` and the legacy `/api/frames?source=mock`.
- Unified release builds backend and frontend, creates runtime/source ZIP assets, creates a draft release, downloads runtime ZIP assets, and runs blocking Linux and Windows acceptance checks.
- Release acceptance verifies runtime unpack/start/health/UI/stop behavior on both platforms. This is a strong operational gate and has already caught real packaging/runtime issues.
- Dev deploy currently builds and uploads backend/frontend artifacts, then emits a simulation gate message. It is useful as artifact validation, but it is not a true deployment validation.

## What Is Good

- The backend has meaningful behavioral tests around the actual decoder and API contract, not only superficial health checks.
- The repository uses a layered quality model: lint, tests, type checks, build, installed-wheel smoke, integration smoke, and release acceptance.
- Release acceptance tests validate the artifact that users actually download instead of only testing source-tree behavior.
- The draft-first release model is a good practice for this project because broken runtime packages stay unpublished.
- Recent CI hardening directly addressed real observed failures: non-idempotent Windows stop behavior and missing decoder spec files in wheel packages.
- Version parity and tag ancestry checks reduce release drift.

## What Is Weak Or Risky

- Frontend behavior is mostly untested. A build can pass while important UI workflows are broken.
- Integration smoke still uses the legacy `/api/frames?source=mock` endpoint and does not cover the main v2 frontend/backend workflow.
- Release acceptance checks UI availability but not whether the UI can successfully fetch decoded frames from `/api/v2/frames`.
- Backend test count is reasonable for the current size, but decoder edge cases and serial failure modes are still underrepresented relative to protocol complexity.
- CI is path-filtered, which is efficient, but docs/config/release script changes can alter runtime behavior without always exercising the full test matrix unless the path filters include those areas.
- There is no coverage measurement or trend. The project can improve or regress without a numeric signal.
- There is no explicit flaky-test or workflow-duration tracking.

## Recommended Quality Metric

Use a composite "Automation Confidence Score" instead of a raw line coverage target. Raw coverage alone would overvalue shallow tests and undervalue release/runtime gates.

Suggested score: 100 points total.

- Backend behavioral coverage: 25 points
  - pytest coverage for API endpoints, decoder rules, source registry, and error paths.
  - Initial target: line coverage >= 75%, branch coverage >= 60%.
- Frontend workflow coverage: 20 points
  - component/browser tests for source switching, log selection, refresh, live stream, serial mode, filters, and runtime config.
  - Initial target: at least one automated test per critical UI workflow.
- Integration coverage: 20 points
  - CI smoke validates built frontend against backend v2 endpoints, not only legacy endpoints.
  - Initial target: `/api/v2/logs`, `/api/v2/frames`, UI root, and runtime config all exercised.
- Release artifact confidence: 20 points
  - runtime ZIP is downloaded, unpacked, launched, checked, stopped on Linux and Windows.
  - Initial target: acceptance also checks decoded frame retrieval, not only `/health` and `/`.
- CI/CD hygiene: 15 points
  - deterministic dependency installs, clear path filters, bounded workflow time, idempotent cleanup, and documented release/manual commands.
  - Initial target: all required workflows under 10 minutes median, no recurring flaky failure pattern.

Minimum acceptable score before calling the system "well automated": 75/100.

Target score for release confidence: 85/100.

Estimated current score: 65/100.

Rationale: backend and release automation are relatively strong, but frontend workflow tests and v2 end-to-end checks are still missing.

## Suggested Improvements

### P1 - High value, low ambiguity

- Add backend coverage reporting with `pytest-cov`, publish coverage summary in CI, and start with thresholds that reflect current reality rather than blocking immediately.
- Extend integration smoke from legacy `/api/frames` to v2 behavior:
  - `/api/v2/logs`
  - `/api/v2/frames?source=simulated_log&log_name=sniffer_log_example.log`
  - `/api/v2/context/instances`
- Extend release acceptance so Linux and Windows runtime ZIP tests also verify decoded frame retrieval from the packaged app.
- Add a package-content assertion for runtime ZIP:
  - backend wheel exists,
  - frontend `dist/index.html` exists,
  - launchers exist,
  - `logs/sniffer_log_example.log` exists,
  - `config/runtime-config.json` exists.

### P2 - Medium-term quality gain

- Add frontend test runner, preferably Vitest + Testing Library for component tests.
- Add Playwright smoke for the built frontend:
  - loads root UI,
  - selects simulated log,
  - refreshes snapshot,
  - verifies at least one decoded frame is rendered.
- Add tests for frontend runtime config behavior:
  - empty `apiBaseUrl` uses relative API paths,
  - configured `apiBaseUrl` targets remote backend.
- Add backend tests for packaging-sensitive behavior using installed wheel or importlib resources expectations.

### P3 - Operational maturity

- Track workflow duration and flaky failures manually in `docs/agent/knowledge-log.md` or automatically through GitHub Actions summaries.
- Add a small CI/CD dashboard document updated per release with:
  - test count,
  - coverage trend,
  - workflow duration,
  - last release acceptance status,
  - known flaky failures.
- Consider adding path filters for runtime packaging files to release-related validation or an explicit packaging CI workflow.

## Proposed Task Breakdown

1. Add backend coverage instrumentation and reporting.
2. Upgrade integration smoke to v2 endpoints.
3. Expand release acceptance to verify decoded frames from runtime ZIP.
4. Introduce frontend component tests for core UI workflows.
5. Add browser smoke test for built frontend + backend.
6. Add CI/CD metrics summary and trend tracking.

## Acceptance Criteria For This Audit Follow-Up

- A future PR can point to this document and select one or more task breakdown items.
- No code or workflow behavior is changed by this audit document itself.
- Any implementation PR should update this document or link its completed task in `docs/tasks/projects.md` or `docs/tasks/roadmap.md`.
