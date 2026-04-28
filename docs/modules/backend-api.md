# Backend API Module

## Purpose

Provide API endpoints and simple UI pages for DALI frame diagnostics.

## Entrypoint

- `backend/app/main.py`

## Main Endpoints

- `GET /health`
- `GET /api/frames?source=mock|serial` (legacy)
- `GET /api/v2/logs`
- `GET /api/v2/frames?source=simulated_log|serial`
- `GET /api/v2/stream?source=simulated_log|serial` (SSE)
- `GET /api/v2/serial/ports`
- `GET /api/v2/serial/status`
- `POST /api/v2/serial/connect`
- `POST /api/v2/serial/disconnect`

## Notes

- v2 decoder is data-driven via JSON spec in `backend/app/specs`.
- `simulated_log` mode replays sniffer logs with timing from `ts_ms`.
- `serial` mode requires active connect/disconnect session before live stream.
