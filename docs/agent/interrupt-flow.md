# Interrupt and Handoff Flow

Use this flow when work is interrupted or transferred.

## Branch and PR Protocol

For all new functionality and material changes:

1. Confirm branch + PR flow with the user.
2. Create a dedicated branch.
3. Implement and validate in that branch.
4. Push branch and open PR automatically.
5. Fill PR template with concrete data from the implemented change and validations.
6. Monitor required CI checks to terminal status or timeout.

No direct work on `main` is allowed.

## CI Supervision Protocol

Use `docs/agent/ci-triage-playbook.md` for all CI failures.

1. Fetch commit/PR check status and identify failing jobs.
2. Collect failed job steps and logs.
3. Classify failure as likely `flaky` or `deterministic`.
4. If likely flaky: one retry of failed jobs only.
5. If still failing or deterministic: prepare root-cause summary and hotfix proposal on the same branch.
6. Before additional hotfix commit, present diagnosis and proposed correction to the user.

Never run unbounded retry/fix loops.

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
5. Include CI supervision state (`run_id`, failing job, retry decision, proposed fix).

Template: `docs/tasks/handoff-template.md`.
