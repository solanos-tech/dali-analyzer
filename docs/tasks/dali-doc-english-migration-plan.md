# Task Plan: DALI Standard Document English Migration and Structure Optimization

## Meta

- Task ID: DOC-DALI-EN-001
- Date: 2026-04-28
- Owner: team
- Priority: P1
- Target branch name: `codex/dali-doc-english-migration`
- Status: Closed (2026-05-04)

## Objective

Migrate `docs/standards/dali.md` to high-quality English without losing any technical content, then optimize structure for long-term maintainability.

## Scope

- In scope:
  - Full-fidelity English translation of `docs/standards/dali.md`.
  - Content parity validation against Polish source backup.
  - Structural optimization proposal and implementation plan.
- Out of scope:
  - Decoder behavior/code changes.
  - Spec schema changes unrelated to documentation.

## Acceptance Criteria

- [x] Every section, table, example, and note from source exists in the English version.
- [x] No semantic loss in command/opcode definitions, frame rules, and caveats.
- [x] English version passes technical review by one domain reviewer.
- [x] Polish source is archived and immutable for traceability.

## Retention Note

- Keep `docs/standards/dali.pl.md` in the repository as a transitional reference for now.
- Do not delete the Polish version until a separate cleanup task is explicitly approved.

## Translation Strategy (No Content Loss)

1. Freeze source: keep `docs/standards/dali.pl.md` as immutable baseline.
2. Translate by section blocks (not by isolated lines) to preserve technical context.
3. Run parity checklist for each section:
   - headings,
   - tables,
   - code blocks,
   - constraints/warnings,
   - test vectors.
4. Run final side-by-side QA review with domain reviewer.
5. Promote English file as primary:
   - `docs/standards/dali.md` (English),
   - keep `docs/standards/dali.pl.md` as archived reference.

## Structure Optimization Suggestions (Future)

1. Split monolith into modular files:
   - `frames-and-addressing.md`
   - `forward16-gear.md`
   - `forward24-device-instance-events.md`
   - `commissioning-and-special.md`
   - `semantic-levels-and-fallbacks.md`
   - `test-vectors.md`
2. Add a top-level index (`docs/standards/dali.md`) with stable anchors and a navigation map.
3. Introduce a compact glossary for normalized terms (e.g., `decoded_generic`, `instance_aware`, `full`).
4. Add a “normative vs heuristic” marker per rule to separate standard facts from implementation heuristics.
5. Add versioned change notes at section level to track additions and re-interpretations.

## Test/Validation Plan

- Documentation parity review checklist.
- Link and anchor integrity checks.
- Spot-check mapping consistency against decoder spec JSON.
- Reviewer sign-off required before declaring English as the single writing language.

## Risks

- Risk: subtle semantic drift in translated technical phrases.
- Mitigation: section-by-section reviewer validation and parity checklist.

## Rollback

- Keep `docs/standards/dali.pl.md` as source baseline.
- Revert English sections selectively if review flags semantic mismatch.
