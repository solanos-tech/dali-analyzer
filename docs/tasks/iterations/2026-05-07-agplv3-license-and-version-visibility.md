# Iteration Note

## Meta

- Date: 2026-05-07
- Branch: `codex/agplv3-license-and-version-visibility`
- PR URL: pending
- Owner: codex

## Done

- Added root `LICENSE` with full AGPLv3 text from FSF source.
- Added AGPLv3 section to root `README.md`.
- Added `LICENSE-FAQ.md` informational guide.
- Updated package metadata licenses:
  - `backend/pyproject.toml`
  - `frontend/package.json`
- Added SPDX headers to maintained source entrypoints:
  - `backend/app/main.py`
  - `frontend/src/App.tsx`
- Added frontend version rendering in UI (`Version: X.Y.Z`) via Vite-injected build constant.
- Added launcher diagnostics output for backend/frontend versions:
  - `packaging/runtime/launchers/start-windows.ps1`
  - `packaging/runtime/launchers/start-linux.sh`
- Updated runtime package README and changelog for licensing/version-visibility changes.

## Blockers

- Frontend checks could not be run in this environment because `npm` is unavailable in PATH.

## Next 3 Tasks

1. Push branch and open PR with `Documentation Impact` details.
2. Run required CI and monitor to terminal status.
3. Confirm runtime launcher diagnostics output in CI/reviewer environment.

## Risks

- Dependency-license compatibility review is best-effort from available local metadata; deeper legal verification may require dedicated tooling in CI or legal review.
