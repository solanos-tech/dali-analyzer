# Knowledge Log

Chronological lessons learned from merged pull requests and completed release cycles.

## Entry Template

- Date (UTC):
- Event key:
- Trigger:
- What changed:
- What improved:
- What failed or caused friction:
- Recommendation for next cycle:
- Related links:

## Entries

- Date (UTC): 2026-05-05
- Event key: cicd-docs-launchers-and-sandbox-validation
- Trigger: End-of-day hardening and verification before PR merge.
- What changed: Added complete CI/CD documentation for humans, introduced Windows launchers, hardened Linux/Windows startup scripts with readiness checks, and synchronized/tested current branch in `/tmp` sandboxes.
- What improved: Startup failures are now explicit and actionable (no false-positive "started" state); CI/CD workflow and policy model is easier to understand at first read; simulated mode works out of the box with bundled sample log.
- What failed or caused friction: Runtime environment initially lacked Node 20 and `uv` in PATH, and the default simulated log file was missing from repository assets.
- Recommendation for next cycle: Keep launcher preflight checks strict, pin dev prerequisites in onboarding docs, and include at least one always-present simulated `.log` fixture in release readiness checks.
- Related links:
  - `docs/ci-cd.md`
  - `README.md`
  - `scripts/ops/dev-up.sh`
  - `scripts/ops/dev-up.ps1`
  - `docs/standards/sniffer_log_example.log`

- Date (UTC): 2026-04-28
- Event key: hygiene-closeout-branch-audit
- Trigger: Repository closeout requested after DALI implementation cycle.
- What changed: Verified merge state against `origin/main`, deleted merged local codex branches, and prepared closeout task documents.
- What improved: Reduced local branch clutter and restored a clean baseline for the next work cycle.
- What failed or caused friction: Full in-session automated translation of `docs/standards/dali.md` was blocked by network policy to translation endpoints.
- Recommendation for next cycle: Execute controlled human-reviewed section translation using the dedicated migration task plan and preserve source parity checks.
- Related links:
  - `docs/tasks/repo-hygiene-closeout-2026-04-28.md`
  - `docs/tasks/dali-doc-english-migration-plan.md`
