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
  - `docs/tasks/repo-hygiene-closeout-2026-04-28.md`
  - `docs/tasks/dali-doc-english-migration-plan.md`

- Date (UTC): 2026-05-05T15:45:54Z
- Event key: release-25386548668-3f25e3132099827ad303b5b83694770dacc9af41
- Trigger: successful release workflow
- Decision: preserve unified release tag policy and continue post-release logging
- Rationale: successful release events should leave decision traces for future cycles
- Impact: improves reproducibility and release diagnostics
- Related links: workflow Unified Release (https://github.com/prudek/dali-analyzer/actions/runs/25386548668)
