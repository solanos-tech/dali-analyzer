#!/usr/bin/env bash
set -euo pipefail

version="${1:-}"
if [[ -z "${version}" ]]; then
  echo "ERROR: VERSION is required. Example: make release-prepare VERSION=0.1.8" >&2
  exit 1
fi
if [[ ! "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: VERSION must match X.Y.Z." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${repo_root}"

git diff --quiet
git diff --cached --quiet

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${current_branch}" != "main" ]]; then
  echo "ERROR: release-prepare must run on main. Current branch: ${current_branch}" >&2
  exit 1
fi

backend_version="$(python3 -c "import tomllib; print(tomllib.load(open('backend/pyproject.toml','rb'))['project']['version'])")"
frontend_version="$(node -p "require('./frontend/package.json').version")"

if [[ "${backend_version}" != "${version}" ]]; then
  echo "ERROR: backend version is ${backend_version}, expected ${version}." >&2
  exit 1
fi
if [[ "${frontend_version}" != "${version}" ]]; then
  echo "ERROR: frontend version is ${frontend_version}, expected ${version}." >&2
  exit 1
fi

if ! grep -q "${version}" CHANGELOG.md; then
  echo "ERROR: CHANGELOG.md does not contain version ${version}." >&2
  exit 1
fi

if git rev-parse -q --verify "refs/tags/v${version}" >/dev/null; then
  echo "ERROR: tag v${version} already exists locally." >&2
  exit 1
fi

if git ls-remote --tags origin "refs/tags/v${version}" | grep -q "refs/tags/v${version}$"; then
  echo "ERROR: tag v${version} already exists on origin." >&2
  exit 1
fi

git fetch origin main
local_main_sha="$(git rev-parse main)"
origin_main_sha="$(git rev-parse origin/main)"
if [[ "${local_main_sha}" != "${origin_main_sha}" ]]; then
  echo "ERROR: local main is not synchronized with origin/main." >&2
  exit 1
fi

echo "release-prepare passed for v${version}."
