# ADR-0005: Agent Learning Loop and Auto Decision Logging

- Status: accepted
- Date: 2026-04-13

## Context

The repository needs durable operational memory after each merged PR and each completed release cycle. Without a standard mechanism, insights and decisions are lost or scattered.

## Decision

1. Maintain two operational logs:
   - `docs/agent/knowledge-log.md` for lessons learned.
   - `docs/agent/decision-log.md` for routine operational decisions.
2. Automatically prepare updates through docs-only follow-up PRs after:
   - merged pull requests on `main`,
   - successful release workflow completions.
3. Keep ADRs for structural/policy decisions only.
4. Never write auto-log updates directly to `main`.

## Consequences

- Repository memory becomes searchable and consistent.
- Post-merge and post-release learnings are preserved with audit trace.
- Additional docs-only PRs increase process overhead slightly but improve long-term quality.
