# Edit Boundaries

This document defines safe boundaries for edits made by contributors and agents.

## General Rules

- Keep changes scoped to the active task.
- Avoid unrelated refactors in the same change set.
- Do not change generated or lock files unless required by the task.
- For each material PR, include a `Documentation Impact` summary and update impacted docs in the same branch.
- For each material PR, perform backlog maintenance (`docs/tasks/backlog.md`, `docs/tasks/done-log.md`, `docs/tasks/iterations/`).

## Backend Boundaries

- Preserve endpoint contracts unless the task explicitly changes API behavior.
- If an API contract changes, update documentation and dependent frontend usage.

## Frontend Boundaries

- Avoid coupling frontend logic to backend implementation details beyond HTTP contracts.
- Keep visual changes separate from backend protocol changes when possible.

## CI Boundaries

- Keep workflows deterministic and reproducible.
- Any workflow change should include local validation instructions.

## Documentation Boundaries

- Use `docs/agent/documentation-governance.md` as the mapping source for required docs updates.
- If task scope exceeds the current docs tree, signal the gap early and propose the minimal tree extension.
