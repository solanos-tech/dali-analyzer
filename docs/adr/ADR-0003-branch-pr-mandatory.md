# ADR-0003: Branch and Pull Request Mandatory Workflow

- Status: accepted
- Date: 2026-04-13

## Context

The project requires predictable collaboration across multiple agents and humans. Direct work on `main` creates review gaps and increases coordination risk.

## Decision

For every new functionality or material change:

1. Confirm branch + PR flow with the requester.
2. Create a dedicated branch.
3. Implement and validate on that branch.
4. Push and open a pull request before handoff or merge.

Direct-to-main changes are not allowed.

## Consequences

- Reviewability and traceability improve.
- Handoff quality increases because branch and PR context are explicit.
- Workflow overhead increases slightly, but risk of unreviewed regressions drops.
