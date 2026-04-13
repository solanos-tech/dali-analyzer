# ADR-0002: Central Changelog

- Status: accepted
- Date: 2026-04-13

## Context

Project changes were not tracked in one place, which made release notes and historical traceability harder.

## Decision

Maintain a single `CHANGELOG.md` at repository root and require updates for material process, architecture, and product changes.

## Consequences

- Better release clarity.
- Easier impact analysis for each change set.
- Stronger review discipline across contributors.
