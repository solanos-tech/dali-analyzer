# dali-analyzer frontend

React + Vite frontend for DALI frames monitoring.

## Run Frontend Locally

```powershell
npm install --no-audit --no-fund
npm run dev
```

UI URL: `http://127.0.0.1:5173`

## Build and lint

```powershell
npm run lint
npm run build
```

## Runtime config

- `VITE_API_BASE_URL` optional API base URL
- `VITE_API_PROXY_TARGET` dev proxy target (default `http://127.0.0.1:8000`)

## UI modes

- Source mode `simulated_log` with log selector fed from backend `/api/v2/logs`
- Source mode `serial` with backend-driven port discovery (`/api/v2/serial/ports`)
- Serial connect/disconnect flow (`/api/v2/serial/connect`, `/api/v2/serial/disconnect`)
- Live mode via SSE with polling fallback when stream is unavailable

## Version and Release

- Source of frontend version: `frontend/package.json` (`version`)
- Release tag pattern: `vX.Y.Z` (unified release)
- Successful release workflow should be followed by auto-log docs PR updates.
