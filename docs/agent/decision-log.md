# Decision Log

Operational decision register updated after merged pull requests and successful release workflows.

## Entry Template

- Date (UTC):
- Event key:
- Trigger:
- Decision:
- Rationale:
- Impact:
- Related links:

## Entries

- Date (UTC): 2026-04-28
- Event key: dali-doc-language-baseline
- Trigger: Request to standardize documentation workflow and prepare for next cycle.
- Decision: Keep a verbatim Polish archive (`docs/standards/dali.pl.md`) and manage English migration through a dedicated parity-controlled task.
- Rationale: Guarantees no information loss while enabling a future English-first authoring baseline.
- Impact: Immediate traceability preserved; translation execution is now scoped, reviewable, and auditable.
- Related links:
  - `docs/tasks/repo-hygiene-closeout-2026-04-28.md`
  - `docs/tasks/dali-doc-english-migration-plan.md`

- Date (UTC): 2026-04-28T15:32:58Z
- Event key: pr-12-cb50d07f8034fcdb8ef95e60c6dcbfde6cbb93ac
- Trigger: merged pull request
- Decision: retain branch+PR workflow and create post-merge knowledge artifacts
- Rationale: merged increments should leave audit-ready operational traces
- Impact: improves repository memory and onboarding continuity
- Related links: PR #12 (docs: add repository hygiene closeout audit and DALI english migratio…) by @prudek - https://github.com/prudek/dali-analyzer/pull/12
