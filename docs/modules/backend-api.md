# Backend API Module

## Purpose

Provide ingestion, decoding, and delivery APIs for DALI frame diagnostics.

## Entrypoint

- `backend/app/main.py`

## Responsibilities

- Parse incoming frame streams from simulated logs and serial sessions.
- Decode frames with spec-driven rules in `backend/app/specs`.
- Provide snapshot and live stream views for frontend and operators.
- Guard serial operations with explicit connect/disconnect state checks.

## Primary Interfaces

- Health and legacy:
  - `GET /health`
  - `GET /api/frames?source=mock|serial` (legacy v1)
- v2 decoded data:
  - `GET /api/v2/logs`
  - `GET /api/v2/frames?source=simulated_log|serial&log_name=<file>&limit=<n>`
  - `GET /api/v2/stream?source=simulated_log|serial&log_name=<file>` (SSE)
  - `GET /api/v2/context/instances`
- Serial control:
  - `GET /api/v2/serial/ports`
  - `GET /api/v2/serial/status`
  - `POST /api/v2/serial/connect`
  - `POST /api/v2/serial/disconnect`
  - `POST /api/v2/serial/command`

## Data and Dependency Notes

- Decoder behavior is data-driven via `backend/app/specs/dali_decoder.json`.
- Simulated mode defaults to `sniffer_log_example.log` and keeps `ts_ms` timing semantics.
- Serial mode requires an active session before `/api/v2/frames?source=serial` or `/api/v2/stream?source=serial`.

## Constraints and Risks

- API contract changes must be reflected in frontend behavior and module docs in the same PR.
- Serial environments differ by OS and driver availability; failures should remain explicit (`409`/`404`).
