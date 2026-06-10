# DALI Protocol Analyzer UI Redesign - Source Audit

## Current frontend architecture

- Framework: React 19 + TypeScript + Vite.
- Entrypoint: `frontend/src/main.tsx`.
- Main monitor view before redesign: `frontend/src/App.tsx`, with styling in `frontend/src/App.css`.
- API client: `frontend/src/api/frames.ts`.
- Shared frontend models: `frontend/src/types.ts`.
- The app did not use routing, Tailwind, CSS modules, or styled components. It used plain CSS variables and component-level React state.

## Current data flow

- Snapshot frames are loaded through `GET /api/v2/frames?source=simulated_log|serial&log_name=<name>&limit=<n>`.
- Live frames are streamed through `GET /api/v2/stream` as SSE `frame` events.
- When SSE fails, the frontend falls back to polling `GET /api/v2/frames` once per second.
- Serial controls use:
  - `GET /api/v2/serial/ports`
  - `GET /api/v2/serial/status`
  - `POST /api/v2/serial/connect`
  - `POST /api/v2/serial/disconnect`
  - `POST /api/v2/serial/command`
- Backend remains the decoding authority. The frontend maps and aggregates already decoded frame records.

## Current frame data model

The v2 frontend model already exposes:

- `raw.ts_ms`
- `raw.direction`
- `raw.bit_length`
- `raw.raw_hex`
- `raw.source`
- `raw.log_name`
- `decoded.frame_class`
- `decoded.name`
- `decoded.status`
- `decoded.addressing`
- `decoded.opcode`
- `decoded.params`
- `decoded.warnings`
- `decoded.confidence`
- `decoded.semantic_level`
- `decoded.semantic_name`
- `decoded.semantic_reason`
- `transaction.correlation_id`
- `transaction.expects_backward`
- `transaction.backward_raw_hex`
- `transaction.latency_ms`

## Available fields

The backend already provides all fields needed for the compact frame table, details panel, sticky filters, status pills, command/response direction styling, warning display, correlation ID, latency, semantic level/name, params JSON, serial connection state, snapshot mode, and live stream mode.

## Missing fields

No backend fields are required for the first redesign phase. The backend does not currently provide dedicated analytics aggregates such as decode-rate windows, top-opcode summaries, active-address summaries, traffic-density buckets, bus-busy ratio, or selected-event correlated response objects. These can be calculated from currently loaded frames for preview purposes, while full analytics can be added later through a dedicated API if needed.

## Filtering implementation

Filtering is frontend-only. Direction, decode status, semantic level, search, error-only, and command-only filters are applied to the in-memory frame list. No backend query contract changes are required.

## SSE / live stream implementation

The frontend creates an `EventSource` using `/api/v2/stream`. Incoming `frame` events are prepended to the local frame list, capped at 500 records. On SSE failure the app switches to polling. Serial live mode first sends the `sniffer_on` command through the existing backend endpoint.

## Recommendation

Use Variant A: frontend-only redesign.

The v2 API already contains the data needed for the requested compact monitor UI. The redesign should avoid backend changes and implement the mini timeline and analytics preview from loaded frontend frames. Larger timeline analytics and richer command-response inspection can be planned separately if they need durable backend aggregation.

## Risks

- Large live sessions can still be bounded by the existing 500-frame cap, so the UI is a monitor rather than a full historical database.
- Frontend-computed decode rate is approximate because it uses the currently loaded frame window.
- Full Timeline and Analytics views remain previews until backend aggregation endpoints exist.
- Sticky offsets are CSS-based and should be checked in desktop and narrow layouts after visual changes.

## Proposed implementation sequence

1. Rename user-facing app text to `DALI Protocol Analyzer`.
2. Keep existing API calls and state behavior intact.
3. Refactor the main view into small React components for header, connection toolbar, filter bar, tabs, table, details panel, mini timeline, analytics preview, and footer.
4. Add compact visual tokens, dense table styling, sticky filters, sticky table header, and sticky details panel.
5. Add frontend-only metrics and timeline calculations from loaded frames.
6. Validate with frontend lint/build and backend regression checks.
