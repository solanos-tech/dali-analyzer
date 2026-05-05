# dali-analyzer

This repository is prepared for iterative human + AI collaboration.

## Start Here

1. Select environment context.
2. Run local dev stack or deploy path.
3. Use release commands when publishing from `main`.

## Operational Commands

- Select active environment context (`dev` or `prod`): `make env-use ENV=dev|prod`
- Show active environment context (defaults to `dev` when not set): `make env-show`
- Trigger deploy contract for `dev` context (no local deployment is executed): `make deploy`
- Validate release preconditions (clean `main`, versions, changelog, tag availability): `make release-prepare VERSION=X.Y.Z`
- Publish release tag `vX.Y.Z` (runs preflight first and pushes tag): `make release-publish VERSION=X.Y.Z`
- Check release workflow and GitHub release status for `vX.Y.Z`: `make release-status VERSION=X.Y.Z`

Detailed behavior and step-by-step flows for humans: `docs/ci-cd.md` (section "6. Human Command Reference").

## Local Dev Stack

- Start backend then frontend (parallel runtime): `make dev-up`
- Stop local stack: `make dev-down`
- Smoke local stack: `make dev-check`

Backend URL: `http://127.0.0.1:8000`
Frontend URL: `http://127.0.0.1:5173`

## Runtime Config

- Frontend API base URL (optional): `VITE_API_BASE_URL`
- Frontend dev proxy target: `VITE_API_PROXY_TARGET` (default `http://127.0.0.1:8000`)
- Backend CORS allow list: `CORS_ALLOW_ORIGINS` (comma-separated)

## Release Tags

- Release trigger tag: `vX.Y.Z` (must point to commit on `main`)
- Single release contains frontend and backend artifacts

## Automatic Logs

After merged PRs and successful release workflows, automation creates follow-up docs PRs that update:

- `docs/agent/knowledge-log.md`
- `docs/agent/decision-log.md`

## Documentation

- [agents.md](agents.md) - agent runtime entrypoint and mandatory branch/PR workflow
- [docs/README.md](docs/README.md) - documentation map and structure
- [docs/ci-cd.md](docs/ci-cd.md) - CI/CD pipelines and policy gates overview
- [CHANGELOG.md](CHANGELOG.md) - change history
