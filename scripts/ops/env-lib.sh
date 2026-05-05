#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ops_dir="${repo_root}/.ops"
env_file="${ops_dir}/active-env"

ensure_ops_dir() {
  mkdir -p "${ops_dir}"
}

resolve_env() {
  if [[ -f "${env_file}" ]]; then
    tr -d '[:space:]' < "${env_file}"
    return
  fi
  echo "dev"
}

validate_env() {
  case "$1" in
    dev|prod) ;;
    *)
      echo "ERROR: invalid environment '$1'. Use dev or prod." >&2
      exit 1
      ;;
  esac
}
