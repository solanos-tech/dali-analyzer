#!/usr/bin/env bash
set -euo pipefail

tag="${1:-}"
source_ref="${2:-HEAD}"
if [[ -z "${tag}" ]]; then
  echo "ERROR: tag is required. Example: ./scripts/release/build-source-package.sh v0.9.0 HEAD" >&2
  exit 1
fi
if [[ ! "${tag}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: tag must match vX.Y.Z." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${repo_root}"

artifacts_dir="${repo_root}/release-artifacts"
mkdir -p "${artifacts_dir}"
source_zip="${artifacts_dir}/source-${tag}.zip"
rm -f "${source_zip}"

git archive --format=zip --output "${source_zip}" "${source_ref}"

echo "Created ${source_zip}"
