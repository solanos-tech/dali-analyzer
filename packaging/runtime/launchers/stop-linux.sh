#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
runtime_dir="${root_dir}/.runtime"
pid_file="${runtime_dir}/backend.pid"

echo "Stopping DALI Analyzer runtime..."

if [[ ! -f "${pid_file}" ]]; then
  echo "No PID file found (${pid_file}). Nothing to stop."
  exit 0
fi

pid="$(cat "${pid_file}")"
if [[ -n "${pid}" ]]; then
  kill "${pid}" 2>/dev/null || true
  sleep 1
  if kill -0 "${pid}" 2>/dev/null; then
    kill -9 "${pid}" 2>/dev/null || true
  fi
fi

rm -f "${pid_file}"
echo "Runtime stopped."
