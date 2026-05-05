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

- Date (UTC): 2026-05-05T13:26:31Z
- Event key: pr-14-7ac3af34247698a87a0fea62fc23ba6fc6db75ee
- Trigger: merged pull request
- Decision: retain branch+PR workflow and create post-merge knowledge artifacts
- Rationale: merged increments should leave audit-ready operational traces
- Impact: improves repository memory and onboarding continuity
- Related links: PR #14 (fix(windows): improve dev-up/dev-down process handling and diagnostics) by @prudek - https://github.com/prudek/dali-analyzer/pull/14
