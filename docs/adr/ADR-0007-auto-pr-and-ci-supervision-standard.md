# ADR-0007: Auto-PR and CI Supervision Standard

- Status: accepted
- Date: 2026-05-06

## Context

The team needs a consistent end-to-end delivery loop where agents do not stop at code changes, but continue through PR publication, CI monitoring, and bounded remediation guidance.

## Decision

For each material repository change:

1. Agent pushes branch and creates PR automatically.
2. Agent fills PR template with meaningful technical content from implemented changes and validations.
3. Agent monitors required CI checks for PR head SHA to terminal state or explicit timeout.
4. On CI failure:
   - classify as `flaky_suspected`, `deterministic_failure`, or `infra_or_permissions`,
   - retry failed jobs once only when flaky is suspected,
   - otherwise provide root-cause summary and hotfix proposal on current branch.
5. Agent must not execute autonomous multi-iteration hotfix loops without user confirmation.

Backlog closeout rule per material PR:

- update `docs/tasks/backlog.md`,
- move completed items to `docs/tasks/done-log.md` when applicable,
- add short note in `docs/tasks/iterations/`.

## Consequences

- Better traceability from implementation through verification.
- Faster response to CI regressions with bounded risk.
- Higher process discipline required in PR descriptions and task artifacts.
