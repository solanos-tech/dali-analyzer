# Interrupt and Handoff Flow

Use this flow when work is interrupted or transferred.

## Branch and PR Protocol

For all new functionality and material changes:

1. Confirm branch + PR flow with the user.
2. Create a dedicated branch.
3. Implement and validate in that branch.
4. Complete `Documentation Impact` and `Backlog Review` updates before PR.
5. Push and open PR before handoff.

No direct work on `main` is allowed.

## Documentation and Backlog Review Protocol (Per PR)

1. Map code/process changes to docs updates using `docs/agent/documentation-governance.md`.
2. Update impacted docs in the same PR.
3. Update `docs/tasks/backlog.md`.
4. Move completed items to `docs/tasks/done-log.md` if applicable.
5. Add one short iteration note in `docs/tasks/iterations/`.

## Learning and Decision Log Protocol

After each merged PR and after each successful release workflow:

1. Record lessons learned in `docs/agent/knowledge-log.md`.
2. Record operational decisions in `docs/agent/decision-log.md`.
3. Submit updates as a docs-only follow-up PR.

Direct log updates to `main` are not allowed.

## Required Handoff Fields

- Task ID
- Branch name
- PR URL
- Last commit hash
- Completed work
- Remaining work
- Reproduction and validation steps
- Known risks or blockers

## Flow

1. Save current status to a handoff note.
2. Link touched files and pending decisions.
3. Record known risks.
4. Assign next owner explicitly.

Template: `docs/tasks/templates/handoff-template.md`.
