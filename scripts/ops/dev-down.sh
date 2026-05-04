#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
ops_dir="${repo_root}/.ops"

stop_pid_file() {
  local pid_file="$1"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}")"
    kill "${pid}" 2>/dev/null || true
    rm -f "${pid_file}"
  fi
}

stop_pid_file "${ops_dir}/frontend.pid"
stop_pid_file "${ops_dir}/backend.pid"

echo "Local dev processes stopped."
