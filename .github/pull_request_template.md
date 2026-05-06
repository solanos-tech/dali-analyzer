## Summary

Briefly describe the change and objective.

## Scope

- In scope:
- Out of scope:

## Documentation Impact (Required)

- Impacted documentation areas:
- Why these docs were updated:
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
- [ ] Updated `docs/tasks/done-log.md` (if any item reached done)
- [ ] Added/updated iteration note in `docs/tasks/iterations/`

## Validation

- [ ] `backend`: `uv run ruff check .`
- [ ] `backend`: `uv run pytest`
- [ ] `backend`: `uv run mypy app`
- [ ] Manual checks completed (described below)

## Manual checks

Describe manual test scenarios and results.

## Docs and registers

- [ ] Documentation in `docs/` updated for impacted areas
- [ ] Mapping validated against `docs/agent/documentation-governance.md`
- [ ] Updated root `README.md` when high-level behavior/onboarding changed
- [ ] Added/updated relevant ADR in `docs/adr/` (if applicable)
- [ ] Updated `CHANGELOG.md`

## Risks

Describe potential risks and rollback plan.
