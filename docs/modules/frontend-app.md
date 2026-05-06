# Frontend App Module

## Purpose

Provide the browser UI layer for interacting with backend diagnostics features.

## Entrypoint

- `frontend/src/main.tsx`

## Responsibilities

- Display decoded frame traffic, transaction state, and semantic details.
- Switch between simulated-log and serial-source modes.
- Manage serial session controls through backend APIs.
- Render live updates from SSE with fallback behavior when needed.

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
