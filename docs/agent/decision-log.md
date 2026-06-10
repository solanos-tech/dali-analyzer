# Decision Log

Operational decision register updated after merged pull requests and successful release workflows.

## Entry Template

- Date (UTC):
- Event key:
- Trigger:
- Decision:
- Rationale:
- Impact:
- Related links:

## Entries

- Date (UTC): 2026-05-05
- Event key: runtime-release-draft-gate-and-wheel-spec-contract
- Trigger: Runtime package verification and failed post-release diagnostics on `v0.9.2`.
- Decision: Keep release flow as draft-first with blocking Linux/Windows acceptance before final publish; enforce backend wheel contract to include decoder specs (`app/specs/*.json`) and keep wheel-runtime smoke endpoint check in CI (`/api/v2/logs`).
- Rationale: Runtime release must be self-sufficient when started from ZIP package; missing wheel data files or non-idempotent shutdown logic can pass basic health but still break operational API behavior.
- Impact: Release confidence increased for GIS runtime usage, reduced false-positive acceptance failures on Windows, and prevented recurrence of runtime `500` from missing decoder specs.
- Related links:
  - `.github/workflows/unified-release.yml`
  - `.github/workflows/backend-ci.yml`
  - `backend/pyproject.toml`
  - `packaging/runtime/launchers/stop-windows.ps1`

- Date (UTC): 2026-05-05
- Event key: launcher-reliability-and-simulated-log-baseline
- Trigger: Manual sandbox validation revealed silent startup failure patterns and missing default simulated log asset.
- Decision: Enforce readiness-checked launchers on both Linux and Windows, and keep `docs/standards/sniffer_log_example.log` as a versioned baseline fixture for simulated mode.
- Rationale: Contributors need deterministic one-command startup behavior and a guaranteed default dataset to verify UI/backend integration without extra setup.
- Impact: Reduced local setup ambiguity, faster diagnosis when prerequisites are missing, and consistent simulated-mode behavior across environments.
- Related links:
  - `scripts/ops/dev-up.sh`
  - `scripts/ops/dev-up.ps1`
  - `scripts/ops/dev-check.sh`
  - `docs/standards/sniffer_log_example.log`
  - `.gitignore`

- Date (UTC): 2026-04-28
- Event key: dali-doc-language-baseline
- Trigger: Request to standardize documentation workflow and prepare for next cycle.
- Decision: Keep a verbatim Polish archive (`docs/standards/dali.pl.md`) and manage English migration through a dedicated parity-controlled task.
- Rationale: Guarantees no information loss while enabling a future English-first authoring baseline.
- Impact: Immediate traceability preserved; translation execution is now scoped, reviewable, and auditable.
- Related links:
  - `docs/tasks/reports/repo-hygiene-closeout-2026-04-28.md`
  - `docs/tasks/reports/dali-doc-english-migration-plan.md`

- Date (UTC): 2026-06-10T09:17:21Z
- Event key: release-27266149590-33bce26450d9f4e66b231aa356c95764c9e1eba3
- Trigger: successful release workflow
- Decision: preserve unified release tag policy and continue post-release logging
- Rationale: successful release events should leave decision traces for future cycles
- Impact: improves reproducibility and release diagnostics
- Related links: workflow Unified Release (https://github.com/solanos-tech/dali-analyzer/actions/runs/27266149590)
