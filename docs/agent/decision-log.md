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

- Date (UTC): 2026-05-05T09:27:49Z
- Event key: pr-13-cbdd9847f26e5efc96e8a309383ababc25eb9447
- Trigger: merged pull request
- Decision: retain branch+PR workflow and create post-merge knowledge artifacts
- Rationale: merged increments should leave audit-ready operational traces
- Impact: improves repository memory and onboarding continuity
- Related links: PR #13 (ci: unify release flow and add operational make commands) by @prudek - https://github.com/prudek/dali-analyzer/pull/13
