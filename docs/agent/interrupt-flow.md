# Interrupt and Handoff Flow

Use this flow when work is interrupted or transferred.

## Branch and PR Protocol

For all new functionality and material changes:

1. Confirm branch + PR flow with the user.
2. Create a dedicated branch.
3. Implement and validate in that branch.
4. Push and open PR before handoff.

No direct work on `main` is allowed.

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

Template: `docs/tasks/handoff-template.md`.
