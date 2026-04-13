# Feature Flags

## Current State

No formal feature flag system is implemented yet.

## Interim Policy

- Use small, reversible changes until a flag framework exists.
- For risky behavior changes, gate execution behind explicit configuration checks.

## Future Direction

- Add a minimal backend flag source (environment-based).
- Document every flag with owner, default value, and removal target date.
