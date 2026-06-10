# Frontend App Module

## Purpose

Provide the `DALI Protocol Analyzer` browser UI layer for interacting with backend diagnostics features.

## Entrypoint

- `frontend/src/main.tsx`

## Responsibilities

- Display decoded frame traffic, transaction state, and semantic details in a compact analyzer layout.
- Switch between simulated-log and serial-source modes.
- Manage serial session controls through backend APIs.
- Render live updates from SSE with fallback behavior when needed.
- Provide frontend-computed monitor metrics, sticky filters, dense frame inspection, a frame details panel, and preview Timeline/Analytics views from loaded frames.

## Interfaces Consumed

- `GET /api/v2/logs`
- `GET /api/v2/frames`
- `GET /api/v2/stream`
- `GET /api/v2/serial/ports`
- `GET /api/v2/serial/status`
- `POST /api/v2/serial/connect`
- `POST /api/v2/serial/disconnect`
- `POST /api/v2/serial/command`

## Dependencies and Constraints

- React + TypeScript + Vite runtime.
- Frontend does not decode DALI protocol payloads directly; backend remains single decoding authority.
- Contract drift risk: any backend response-model changes require same-PR UI update and module-doc update.
- Timeline and analytics cards currently derive from the loaded frame window; durable aggregate APIs are a future extension, not a current frontend dependency.
