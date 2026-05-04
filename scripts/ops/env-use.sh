#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/env-lib.sh"

target_env="${1:-}"
if [[ -z "${target_env}" ]]; then
  echo "ERROR: ENV is required. Example: make env-use ENV=dev" >&2
  exit 1
fi

validate_env "${target_env}"
ensure_ops_dir
printf '%s\n' "${target_env}" > "${env_file}"
echo "Active environment set to '${target_env}'."
