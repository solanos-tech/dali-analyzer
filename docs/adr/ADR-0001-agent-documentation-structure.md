# ADR-0001: Agent-First Documentation Structure

- Status: accepted
- Date: 2026-04-13

## Context

The repository needed a clear documentation model for AI and human collaboration. The prior structure mixed operational notes with project tracking and did not separate architecture decisions from workflow rules.

## Decision

Use a dedicated structure:

- `docs/adr/` for architecture and process decisions
- `docs/agent/` for collaboration and execution guidance
- `docs/test/` for quality and validation guidance
- `docs/tasks/` for delivery planning and tracking
- `docs/modules/` for module-level technical reference

## Consequences

- Faster onboarding and cleaner handoff between contributors.
- Clear ownership boundaries for docs updates.
- Easier auditability of decisions and process evolution.
