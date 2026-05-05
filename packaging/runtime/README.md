# DALI Analyzer Runtime Package

## What this package contains

- Backend runtime wheel (`backend/wheels/*.whl`)
- Frontend static bundle (`frontend/dist`)
- Cross-platform launchers (`launchers/`)
- Runtime config (`config/runtime-config.json`)
- Sample simulated log (`logs/sniffer_log_example.log`)

## What this package is for

This package runs the DALI Analyzer in all-in-one mode:

- Backend API and frontend UI are served by one runtime process.
- Default UI URL: `http://127.0.0.1:8000`

You can also point the frontend to a remote backend by editing `config/runtime-config.json` and setting `apiBaseUrl`.

## Prerequisites

- Internet access (first startup installs dependencies in local sandbox).
- Python 3.12+ available in PATH.

## Start / stop

### Linux

```bash
./launchers/start-linux.sh
./launchers/stop-linux.sh
```

### Windows (PowerShell)

```powershell
.\launchers\start-windows.ps1
.\launchers\stop-windows.ps1
```

## Runtime sandbox

Launchers create a local sandbox under `.runtime/` inside this package directory:

- bootstrap tooling environment (including `uv`)
- backend virtual environment
- runtime PID and logs

No global Python environment changes are required.

## Logs

- `.runtime/backend.log`
- `.runtime/backend.err.log`

## Optional: remote backend mode

Edit `config/runtime-config.json`:

```json
{
  "apiBaseUrl": "http://YOUR-BACKEND-HOST:8000"
}
```

Leave `apiBaseUrl` empty to use all-in-one mode.
