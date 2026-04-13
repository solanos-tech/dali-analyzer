# Agent Operating Guide

This is the single runtime entrypoint for agent and multi-agent work in this repository.

## Latest Accepted Decisions (Read First)

- `docs/adr/ADR-0001-agent-documentation-structure.md`
- `docs/adr/ADR-0002-central-changelog.md`
- `docs/adr/ADR-0003-branch-pr-mandatory.md`

## Branch and PR Rule (Mandatory)

For every new functionality or material change:

1. Ask the user whether to create a branch and PR.
2. After confirmation, always create a branch.
3. Implement only on that branch.
4. Commit, push, and open a PR.

Direct-to-main changes are not allowed.

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
npm ci
npm run lint
npm run build
```

Optional local run:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

```powershell
cd frontend
npm run dev
```

## Safety and Invariants

- Do not break existing API behavior without updating docs and consumers.
- Keep CI and release workflows deterministic.
- Keep edits scoped to the active task; avoid unrelated refactors.
- Update `CHANGELOG.md` for material changes.

## Multi-Agent Working Contract

- Assign explicit ownership per task and file area.
- Use short task leases to avoid edit collisions.
- If blocked, hand off with `done`, `remaining`, `risks`, and `reproduction steps`.
- Do not duplicate work already delegated to another agent.

## Active Work Sources

- Project status: `docs/tasks/projects.md`
- Roadmap: `docs/tasks/roadmap.md`
- Task template: `docs/tasks/task-template.md`
- Handoff template: `docs/tasks/handoff-template.md`

## Where Agents Should Read Next

- `docs/agent/repo-map.md`
- `docs/agent/edit-boundaries.md`
- `docs/agent/build-runbook.md`
- `docs/agent/interrupt-flow.md`
- `docs/agent/feature-flags.md`
- `docs/test/README.md`
- `docs/test/checklist.md`
