# Agent Operating Guide

This is the single runtime entrypoint for agent and multi-agent work in this repository.

## Latest Accepted Decisions (Read First)

- `docs/adr/ADR-0001-agent-documentation-structure.md`
- `docs/adr/ADR-0002-central-changelog.md`
- `docs/adr/ADR-0003-branch-pr-mandatory.md`
- `docs/adr/ADR-0004-release-versioning-policy.md`
- `docs/adr/ADR-0005-agent-learning-loop.md`
- `docs/adr/ADR-0006-documentation-impact-and-backlog-review.md`

## Branch and PR Rule (Mandatory)

For every new functionality or material change:

1. Ask the user whether to create a branch and PR.
2. After confirmation, always create a branch.
3. Implement only on that branch.
4. Commit, push, and open a PR.

Direct-to-main changes are not allowed.

## Documentation and Backlog Rule (Mandatory)

For every material pull request:

1. Complete a `Documentation Impact` note in PR description.
2. Update all impacted docs following `docs/agent/documentation-governance.md`.
3. Update active tasks in `docs/tasks/backlog.md`.
4. Move completed tasks to `docs/tasks/done-log.md` when ready.
5. Add one short iteration note in `docs/tasks/iterations/`.

No hard CI gate enforces this; agents and reviewers must enforce it through workflow discipline.

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

## Multi-Agent Working Contract

- Assign explicit ownership per task and file area.
- Use short task leases to avoid edit collisions.
- If blocked, hand off with `done`, `remaining`, `risks`, and `reproduction steps`.
- Do not duplicate work already delegated to another agent.

## Active Work Sources

- Backlog (active): `docs/tasks/backlog.md`
- Done log (history): `docs/tasks/done-log.md`
- Project register: `docs/tasks/planning/projects.md`
- Roadmap: `docs/tasks/planning/roadmap.md`
- Task template: `docs/tasks/templates/task-template.md`
- Handoff template: `docs/tasks/templates/handoff-template.md`
- Iteration template: `docs/tasks/templates/iteration-review-template.md`

## Where Agents Should Read Next

- `docs/agent/repo-map.md`
- `docs/agent/edit-boundaries.md`
- `docs/agent/build-runbook.md`
- `docs/agent/interrupt-flow.md`
- `docs/agent/feature-flags.md`
- `docs/agent/documentation-governance.md`
- `docs/agent/release-versioning.md`
- `Makefile`
- `docs/agent/knowledge-log.md`
- `docs/agent/decision-log.md`
- `docs/cicd/README.md`
- `docs/test/README.md`
- `docs/test/checklist.md`
