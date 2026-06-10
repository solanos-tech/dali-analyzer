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

- Date (UTC): 2026-06-10
- Event key: dali-protocol-analyzer-ui-redesign-release-0-9-5
- Trigger: Frontend redesign merged and release `v0.9.5` published.
- What changed: The DALI Protocol Analyzer UI redesign was merged, documentation status was refreshed, the backlog item was closed out, and release tag `v0.9.5` was pushed from `main`.
- What improved: Repo history now matches the shipped state, and operational docs no longer imply that the UI redesign or release are still pending.
- What failed or caused friction: None in the final closeout pass beyond earlier GitHub auth limitations for direct PR metadata edits.
- Recommendation for next cycle: Keep backlog, done-log, and iteration notes synchronized immediately after merge and before tagging a release.
- Related links:
  - `CHANGELOG.md`
  - `docs/tasks/backlog.md`
  - `docs/tasks/done-log.md`
  - `docs/tasks/iterations/2026-06-10-dali-protocol-analyzer-ui-redesign.md`
  - `docs/tasks/iterations/2026-06-10-release-0-9-5.md`

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
  - `docs/cicd/README.md`
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
  - `docs/tasks/reports/repo-hygiene-closeout-2026-04-28.md`
  - `docs/tasks/reports/dali-doc-english-migration-plan.md`

- Date (UTC): 2026-06-10T09:40:24Z
- Event key: pr-26-2ed3b7a771190ee3c26a3c28bc6042cf0f195dfd
- Trigger: merged pull request
- What changed: PR #26 merged to main
- What improved: New increment was integrated and validated through review workflow
- What failed or caused friction: none recorded by automation
- Recommendation for next cycle: keep docs and release metadata updated in the same cycle
- Related links: https://github.com/solanos-tech/dali-analyzer/pull/26, commit 2ed3b7a771190ee3c26a3c28bc6042cf0f195dfd
