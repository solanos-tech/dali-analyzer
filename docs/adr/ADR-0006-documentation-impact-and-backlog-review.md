# ADR-0006: Documentation Impact and Backlog Review per Pull Request

- Status: accepted
- Date: 2026-05-06

## Context

The repository needs reliable documentation freshness and backlog traceability in every iteration. A strict CI gate for docs/backlog was considered, but the team prefers a lighter operational model led by agent workflow and review discipline.

## Decision

For every material pull request:

1. Add a `Documentation Impact` statement in PR description.
2. Update impacted docs in the same branch, following `docs/agent/documentation-governance.md`.
3. Update active tasks in `docs/tasks/backlog.md`.
4. Move completed tasks to `docs/tasks/done-log.md` when ready.
5. Add one short iteration note in `docs/tasks/iterations/`.

Enforcement model:

- No dedicated hard CI gate for docs/backlog.
- Enforcement is done through:
  - `agents.md` runtime rules
  - PR template requirements
  - reviewer and maintainer checks

## Consequences

- Lower process friction than CI-based hard blocking.
- Stronger expectation on contributor discipline and review quality.
- Better continuity between implementation, documentation, and next-iteration planning.
