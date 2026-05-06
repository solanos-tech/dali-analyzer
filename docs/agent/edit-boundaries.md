# Edit Boundaries

This document defines safe boundaries for edits made by contributors and agents.

## General Rules

- Keep changes scoped to the active task.
- Avoid unrelated refactors in the same change set.
- Do not change generated or lock files unless required by the task.
- For material changes, include PR creation and CI supervision as part of completion.

## Backend Boundaries

- Preserve endpoint contracts unless the task explicitly changes API behavior.
- If an API contract changes, update documentation and dependent frontend usage.

## Frontend Boundaries

- Avoid coupling frontend logic to backend implementation details beyond HTTP contracts.
- Keep visual changes separate from backend protocol changes when possible.

## CI Boundaries

- Keep workflows deterministic and reproducible.
- Any workflow change should include local validation instructions.
- Retry policy for CI failures: one retry only when failure is likely flaky.
- When failure looks deterministic, switch immediately to diagnosis and hotfix proposal.
