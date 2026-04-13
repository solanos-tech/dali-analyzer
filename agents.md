# Agent Collaboration Guide

This file defines the collaboration standard for AI and human contributors in `dali-analyzer`.

## 1. Purpose

- Keep change quality high in short delivery cycles.
- Make task handoff easy without losing context.
- Reduce regression risk through explicit checklists and logs.

## 2. Roles and Responsibility

- `Owner`: defines priorities, approves scope, closes tasks.
- `Implementer`: delivers code and documentation changes.
- `Reviewer`: checks risks, regressions, test coverage, and architecture fit.
- `Release Agent`: owns versioning, changelog quality, and release flow.

One person or one agent can hold multiple roles, but roles must be explicit in the task or PR.

## 3. Task Contract

Each task should include:

- Business or technical objective (1-2 sentences).
- In-scope and out-of-scope definition.
- Acceptance criteria.
- Test plan (manual plus automated).
- Risk assessment and rollback plan.

## 4. Definition of Done

A change is done when:

- Code works locally.
- Checks pass (`ruff`, `pytest`, `mypy` for backend).
- Documentation is updated (`docs/` and `CHANGELOG.md`).
- Key decisions and risks are documented.
- Project status is updated.

## 5. Workflow

1. Pick a task from `docs/tasks/projects.md`.
2. Confirm scope and acceptance criteria.
3. Implement on a working branch.
4. Validate locally.
5. Update documentation and changelog.
6. Review and merge.

## 6. Minimum PR Checklist

- [ ] Scope matches the task objective.
- [ ] No accidental or unrelated changes.
- [ ] Tests pass locally or in CI.
- [ ] Documentation and changelog are updated.
- [ ] Risks and decisions are documented.

## 7. Handoff Convention

When handing work over, include:

- What is done.
- What is still open.
- How to reproduce locally.
- Known risks and blockers.

## 8. Task Priority

- `P0`: Blocks production or release.
- `P1`: High impact, no workaround.
- `P2`: Standard product development.
- `P3`: Improvements and cleanup.
