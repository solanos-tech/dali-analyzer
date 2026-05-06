# Documentation Governance

Use this map in every implementation PR.

## Change-to-Documentation Mapping

| Change Type | Required Documentation Updates |
|---|---|
| Product behavior, onboarding flow, runtime entrypoints, or protocol context | Update root `README.md` (`Product Overview` and/or `Developer/Repository Guide`). |
| Backend API behavior, response shape, serial/source behavior | Update `docs/modules/backend-api.md` and impacted testing docs in `docs/test/README.md`. |
| Frontend behavior, source-mode UX, runtime integration assumptions | Update `docs/modules/frontend-app.md` and root `README.md` if user-facing flow changed. |
| Testing strategy, quality gates, or validation process | Update `docs/test/README.md` and, if needed, `docs/test/checklist.md`. |
| CI/CD or operational command flow | Update `docs/cicd/README.md` and relevant references in root `README.md`. |
| Decision/policy changes for collaboration | Add/update ADR in `docs/adr/` and align `agents.md` / `docs/agent/*`. |
| Major scope expansion that no longer fits current docs tree | Signal the need to extend docs tree during the task and document the adopted structure in `docs/README.md`. |

## Mandatory PR Workflow Steps

1. Fill `Documentation Impact` section in PR description.
2. Update `docs/tasks/backlog.md` for touched tasks.
3. Move completed backlog items to `docs/tasks/done-log.md` when ready.
4. Add one short note in `docs/tasks/iterations/`.
5. Keep `CHANGELOG.md` aligned for material process/product changes.

## Enforcement Model

- This repository uses a soft governance model:
  - enforced by workflow instructions, templates, and review discipline
  - no dedicated hard CI gate for docs/backlog compliance
