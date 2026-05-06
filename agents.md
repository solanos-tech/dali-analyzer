# Agent Operating Guide

This is the single runtime entrypoint for agent and multi-agent work in this repository.

## Latest Accepted Decisions (Read First)

- `docs/adr/ADR-0001-agent-documentation-structure.md`
- `docs/adr/ADR-0002-central-changelog.md`
- `docs/adr/ADR-0003-branch-pr-mandatory.md`
- `docs/adr/ADR-0004-release-versioning-policy.md`
- `docs/adr/ADR-0005-agent-learning-loop.md`
- `docs/adr/ADR-0007-auto-pr-and-ci-supervision-standard.md`

## Branch and PR Rule (Mandatory)

For every new functionality or material change:

1. Ask the user whether to create a branch and PR.
2. After confirmation, always create a branch.
3. Implement only on that branch.
4. Commit, push, and open a PR automatically.

Direct-to-main changes are not allowed.

## Definition of Done for Material Changes

For every material change, done means all of the following are complete:

1. Branch is pushed.
2. Pull request is created and linked.
3. PR template is filled with meaningful technical detail.
4. Required CI checks are monitored to terminal state or explicit timeout.

If required tooling/auth is unavailable, report blocker explicitly and provide manual fallback steps.

## Versioning, Tagging, and Release Rule (Mandatory)

For every release candidate or release-related change:

1. Update backend version in `backend/pyproject.toml` (`[project].version`).
2. Update frontend version in `frontend/package.json` (`version`).
3. Keep both versions aligned unless the user explicitly asks for separate version lines.
4. Update `CHANGELOG.md` with release notes before tagging.
5. Use unified release tag: `vX.Y.Z` (must point to `main`).
6. Use operational commands:
   - `make env-use ENV=dev|prod`
   - `make deploy` (dev context only)
   - `make release-prepare VERSION=X.Y.Z`
   - `make release-publish VERSION=X.Y.Z`
   - `make release-status VERSION=X.Y.Z`

Tags not matching `vX.Y.Z` are invalid for release automation.

## Build and Verification

Run these before handoff or PR:

```powershell
cd backend
uv run ruff check .
uv run pytest
uv run mypy app
```

```powershell
cd frontend
npm install --no-audit --no-fund
npm run lint
npm run build
```

Optional local run:

```powershell
make dev-up
```

```powershell
make dev-check
make dev-down
```

## Safety and Invariants

- Do not break existing API behavior without updating docs and consumers.
- Keep CI and release workflows deterministic.
- Keep edits scoped to the active task; avoid unrelated refactors.
- Update `CHANGELOG.md` for material changes.
- After each merged PR and successful release workflow, update knowledge and decision logs through an auto-generated docs PR.
- Avoid infinite fix loops: at most one CI retry for likely flaky failures, then root-cause analysis.
- Do not apply autonomous multi-iteration hotfix chains without user confirmation.

## Multi-Agent Working Contract

- Assign explicit ownership per task and file area.
- Use short task leases to avoid edit collisions.
- If blocked, hand off with `done`, `remaining`, `risks`, and `reproduction steps`.
- Do not duplicate work already delegated to another agent.

## Active Work Sources

- Active backlog: `docs/tasks/backlog.md`
- Completed items log: `docs/tasks/done-log.md`
- Iteration notes: `docs/tasks/iterations/`
- Project status: `docs/tasks/projects.md`
- Roadmap: `docs/tasks/roadmap.md`
- Task template: `docs/tasks/task-template.md`
- Handoff template: `docs/tasks/handoff-template.md`

## Where Agents Should Read Next

- `docs/agent/repo-map.md`
- `docs/agent/edit-boundaries.md`
- `docs/agent/build-runbook.md`
- `docs/agent/interrupt-flow.md`
- `docs/agent/ci-triage-playbook.md`
- `docs/agent/feature-flags.md`
- `docs/agent/release-versioning.md`
- `Makefile`
- `docs/agent/knowledge-log.md`
- `docs/agent/decision-log.md`
- `docs/test/README.md`
- `docs/test/checklist.md`
