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
- Event key: runtime-release-zip-gating-and-wheel-spec-hotfix
- Trigger: Release cycle `v0.9.1` to `v0.9.3` after introducing runtime/source ZIP packaging and blocking acceptance gates.
- What changed: Unified release now creates draft release assets (`runtime-vX.Y.Z.zip`, `source-vX.Y.Z.zip`), runs Linux+Windows acceptance by downloading runtime ZIP, and publishes only on success. Runtime launchers were hardened for Windows stop idempotency, and backend wheel packaging was fixed to include decoder specs (`app/specs/*.json`).
- What improved: Runtime package became reproducible and cross-platform launchable; acceptance catches packaging/runtime faults before final publish; backend `500` failures from missing specs in wheel were eliminated.
- What failed or caused friction: Initial runtime release passed `/health` but failed v2 API with `500` because wheel omitted `app/specs/*.json`; Windows acceptance stop initially produced false failures when tracked PID had already exited.
- Recommendation for next cycle: Keep wheel-installed runtime smoke checks on v2 endpoints (`/api/v2/logs`) as hard gate; retain idempotent launcher stop semantics and draft-first release model.
- Related links:
  - `.github/workflows/unified-release.yml`
  - `.github/workflows/backend-ci.yml`
  - `packaging/runtime/launchers/stop-windows.ps1`
  - `backend/pyproject.toml`
  - `scripts/release/build-runtime-package.sh`
  - `scripts/release/build-source-package.sh`

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

- Date (UTC): 2026-05-05T16:13:09Z
- Event key: pr-18-e16097f466ee55ce87b831804bff882f9bd89f33
- Trigger: merged pull request
- What changed: PR #18 merged to main
- What improved: New increment was integrated and validated through review workflow
- What failed or caused friction: none recorded by automation
- Recommendation for next cycle: keep docs and release metadata updated in the same cycle
- Related links: https://github.com/prudek/dali-analyzer/pull/18, commit e16097f466ee55ce87b831804bff882f9bd89f33
