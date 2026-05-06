# CI Triage Playbook

Use this playbook after PR creation for material changes.

## Objective

Provide a deterministic, bounded process for monitoring GitHub Actions, diagnosing failures, and proposing safe hotfixes on the same working branch.

## Inputs

- Repository: `prudek/dali-analyzer`
- PR number
- PR head SHA

## Standard Workflow

1. Fetch combined check status for PR head SHA.
2. Fetch workflow runs for that commit.
3. For each failed workflow run, fetch jobs.
4. For each failed job, fetch steps and logs.
5. Classify failure:
   - `flaky_suspected`
   - `deterministic_failure`
   - `infra_or_permissions`

## Classification Guide

Treat as `flaky_suspected` when symptoms include:

- network timeout/transient registry fetch errors
- runner instability messages
- non-reproducible test order/timing failures without consistent stack trace

Treat as `deterministic_failure` when symptoms include:

- assertion/test failures with consistent stack trace
- lint/type/build errors with reproducible output
- missing files/config/schema and contract mismatches

Treat as `infra_or_permissions` when symptoms include:

- missing GitHub token/auth
- denied permissions for actions APIs
- repository/network access blocked

## Decision Policy

1. If `flaky_suspected`:
   - re-run failed jobs once only.
   - if pass: report as flaky with retry used.
   - if fail again: treat as deterministic and continue diagnosis.
2. If `deterministic_failure`:
   - do not retry repeatedly.
   - prepare root-cause summary and propose hotfix.
3. If `infra_or_permissions`:
   - report blocker immediately.
   - provide manual fallback instructions.

## Safety Bounds

- Max retries per failure cycle: `1`.
- Max autonomous hotfix loops without user confirmation: `0`.
- Before next hotfix commit, always present:
  - probable root cause
  - minimal fix proposal
  - expected validation scope

## Required User-Facing Report Format

- `PR`: link/number
- `Head SHA`: value
- `Check status`: pass/fail/pending/timeout
- `Failed runs/jobs`: list
- `Classification`: flaky_suspected/deterministic_failure/infra_or_permissions
- `Retry used`: yes/no
- `Root cause summary`: 1-4 lines
- `Hotfix proposal`: 1-4 lines
- `Blockers`: none or explicit blocker + fallback

## Blockers and Fallback

If auth/token/network tooling is unavailable, report:

- "Cannot supervise CI automatically due to <reason>."
- Manual fallback:
  1. open PR checks tab
  2. open failing job logs
  3. copy failing step name + error excerpt
  4. return excerpt for guided hotfix planning
