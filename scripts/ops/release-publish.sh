#!/usr/bin/env bash
set -euo pipefail

version="${1:-}"
if [[ -z "${version}" ]]; then
  echo "ERROR: VERSION is required. Example: make release-publish VERSION=0.1.8" >&2
  exit 1
fi
if [[ ! "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: VERSION must match X.Y.Z." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${repo_root}"

"${repo_root}/scripts/ops/release-prepare.sh" "${version}"

git tag "v${version}"
git push origin "v${version}"
echo "Published tag v${version}. Unified Release workflow should start automatically."
