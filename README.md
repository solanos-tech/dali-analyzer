# dali-analyzer

## Product Overview

`dali-analyzer` provides the DALI Protocol Analyzer, a diagnostics tool for DALI/DALI-2 traffic inspection.
It ingests raw frame streams, classifies and decodes them in the backend, and exposes
REST/SSE data for a browser UI.


<img width="1877" height="860" alt="image" src="https://github.com/user-attachments/assets/f8386249-47fd-4211-aa66-dd9f92344071" />




Primary use cases:

- inspect simulated sniffer logs without hardware
- inspect live serial input from a connected sniffer
- review decoded transactions and protocol semantics for troubleshooting
- monitor compact frame tables, sticky filters, frame details, and frontend-derived bus activity previews

DALI context:

- System is aligned with IEC 62386 concepts (DALI and DALI-2 families).
- Working protocol reference in this repository: [docs/standards/dali.md](docs/standards/dali.md).

Input stream shape:

- Simulated logs: `docs/standards/sniffer_log_example.log`
- Live serial: parsed with this backend pattern:

```text
ts_ms=(?P<ts>\d+)\s+dir=(?P<dir>[a-zA-Z0-9_]+)\s+raw=(?P<raw>0x[0-9A-Fa-f]+)
```

Example line:

```text
[2026-05-05 10:00:00.180] sniffer ts_ms=80 dir=rx_forward24 raw=0x01FE30
```

## Sniffer Hardware Option

Live serial capture requires a DALI sniffer that can observe bus traffic and
emit terminal-friendly frame events. One compatible starting point is
[solanos-tech/dali-tap-bridge-pic18](https://github.com/solanos-tech/dali-tap-bridge-pic18),
which provides firmware for the Microchip `PIC18F47K42 Curiosity Nano`.

That repository focuses on a minimal DALI sniffer / control-device terminal
bridge:

- observes DALI traffic and reports raw forward and backward frame events
- uses `UART1` for DALI transport (`RC2`/`RC3`)
- uses `UART2` as a `115200 8N1` debug terminal (`RD0`/`RD1`)
- supports terminal commands such as `help`, `status`, `sniffer on`,
  `sniffer off`, `dali stats`, `send 16`, and `send 24`
- includes documentation for hardware wiring, terminal commands, and building
  the MPLAB X project

High-level bring-up flow:

1. Get the required hardware: a `PIC18F47K42 Curiosity Nano`, a proper DALI
   physical front-end / driver stage between the MCU and the bus, and a UART
   connection for the debug terminal.
2. Review the sniffer repository documentation, especially
   [`docs/hardware.md`](https://github.com/solanos-tech/dali-tap-bridge-pic18/blob/main/docs/hardware.md)
   and
   [`docs/terminal.md`](https://github.com/solanos-tech/dali-tap-bridge-pic18/blob/main/docs/terminal.md).
3. Build the firmware from the sniffer repository with the documented MPLAB X
   project command:

   ```powershell
   make -f nbproject\Makefile-default.mk SUBPROJECTS= .build-conf
   ```

4. Flash the firmware to the Curiosity Nano using the normal Microchip/MPLAB X
   tooling for that board.
5. Wire the DALI bus through the physical front-end, keeping the debug terminal
   isolated from the DALI bus.
6. Open the terminal at `115200 8N1`, run `sniffer on`, and capture the emitted
   frame lines.
7. Connect DALI Protocol Analyzer to the serial terminal stream, or save the
   terminal output as a log and inspect it through the analyzer's simulated log
   workflow.

The sniffer firmware can report observations such as `rx_forward16`,
`rx_forward24`, `rx_backward`, `tx_forward16_local`, and
`tx_forward24_local`. When integrating new firmware output with this analyzer,
keep the emitted lines aligned with the input stream shape documented above.

## Developer/Repository Guide

### Quick Start

- Start local stack: `make dev-up`
- Smoke-check stack: `make dev-check`
- Stop local stack: `make dev-down`

Launcher equivalents:

- Linux/macOS: `./scripts/ops/dev-up.sh`, `./scripts/ops/dev-down.sh`
- Windows PowerShell: `.\scripts\ops\dev-up.ps1`, `.\scripts\ops\dev-down.ps1`

Default local URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

### Operational Commands

- Set environment context: `make env-use ENV=dev|prod`
- Show current context: `make env-show`
- Dev deploy contract: `make deploy`
- Release preflight: `make release-prepare VERSION=X.Y.Z`
- Publish release tag: `make release-publish VERSION=X.Y.Z`
- Check release status: `make release-status VERSION=X.Y.Z`

Detailed CI/CD and command flow: [docs/cicd/README.md](docs/cicd/README.md).

### Workflow (Minimal)

`branch -> implement -> validate -> PR -> review -> merge`

- Branch + PR workflow is mandatory for material changes.
- Release tags must follow `vX.Y.Z`.

### Repository Map

```text
.
|-- backend/
|-- frontend/
|-- docs/
|   |-- adr/
|   |-- agent/
|   |-- cicd/
|   |-- modules/
|   |-- standards/
|   |-- tasks/
|   `-- test/
|-- packaging/
|-- scripts/
|-- agents.md
`-- CHANGELOG.md
```

### Runtime Config

- Frontend API base URL: `VITE_API_BASE_URL` (optional)
- Frontend dev proxy target: `VITE_API_PROXY_TARGET` (default `http://127.0.0.1:8000`)
- Backend CORS allow list: `CORS_ALLOW_ORIGINS` (comma-separated)

### Versioning and Release

- Unified release tag: `vX.Y.Z` (must point to commit reachable from `main`)
- Release assets:
  - `runtime-vX.Y.Z.zip`
  - `source-vX.Y.Z.zip`

### Documentation Index

- [agents.md](agents.md) - agent runtime entrypoint and mandatory workflow
- [docs/README.md](docs/README.md) - documentation map
- [docs/cicd/README.md](docs/cicd/README.md) - CI/CD overview and policy gates
- [CHANGELOG.md](CHANGELOG.md) - change history

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3).

This means that you may use, study, modify, and redistribute this software under the terms of the AGPLv3. If you modify this software or make it available to users over a network, including as part of a hosted service, SaaS platform, internal web application, commissioning tool, diagnostic system, or product-integrated service, you must make the corresponding source code available under the same license.

For use cases where AGPLv3 obligations are not acceptable, including proprietary or closed-source commercial integrations, please contact the project owner to discuss a separate commercial license.

See the LICENSE file for the full license text.
