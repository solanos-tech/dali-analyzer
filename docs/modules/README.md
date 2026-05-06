# Modules

Module-level reference documents live here.

## System Flow

```mermaid
flowchart LR
  A["Sniffer log (.log) or serial stream"] --> B["Backend source registry"]
  B --> C["Decode pipeline (spec-driven)"]
  C --> D["REST/SSE API"]
  D --> E["Frontend monitoring UI"]
```

## Current Modules

- [backend-api.md](backend-api.md)
- [frontend-app.md](frontend-app.md)

## Documentation Expectations

- Keep each module doc focused on responsibilities, interfaces, dependencies, and limits.
- Update module docs in the same PR when contracts or behavior change.
