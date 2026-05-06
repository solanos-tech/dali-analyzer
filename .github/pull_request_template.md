## Summary

Briefly describe the change and objective.

## Scope

- In scope:
- Out of scope:

## Documentation Impact (Required)

- Impacted docs:
- Why updated:
- If no docs changed, provide rationale:

## CI Triage (Required for Material Changes)

- Required checks status:
- Workflow run IDs reviewed:
- Failed job IDs (if any):
- Classification: `flaky_suspected` | `deterministic_failure` | `infra_or_permissions`
- Retry used (one max): yes/no
- Root-cause summary:
- Hotfix proposed on current branch: yes/no

## Backlog Update (Required for Material Changes)

- [ ] Updated `docs/tasks/backlog.md`
- [ ] Updated `docs/tasks/done-log.md` (if any item moved to done)
- [ ] Added iteration note in `docs/tasks/iterations/`

## Validation

- [ ] `backend`: `uv run ruff check .`
- [ ] `backend`: `uv run pytest`
- [ ] `backend`: `uv run mypy app`
- [ ] Manual checks completed (described below)

## Manual checks

Describe manual test scenarios and results.

## Docs and registers

- [ ] Documentation in `docs/` updated (if applicable)
- [ ] Updated `docs/tasks/projects.md` (project status, if applicable)
- [ ] Added/updated relevant ADR in `docs/adr/` (if applicable)
- [ ] Updated `CHANGELOG.md`

## Risks

Describe potential risks and rollback plan.
