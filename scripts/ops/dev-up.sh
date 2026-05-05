#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
ops_dir="${repo_root}/.ops"
mkdir -p "${ops_dir}"
backend_pid_file="${ops_dir}/backend.pid"
frontend_pid_file="${ops_dir}/frontend.pid"
backend_log_file="${ops_dir}/backend.log"
frontend_log_file="${ops_dir}/frontend.log"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: required command '${cmd}' is not available in PATH." >&2
    exit 1
  fi
}

http_probe() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl --silent --fail "${url}" >/dev/null
    return
  fi
  if command -v wget >/dev/null 2>&1; then
    wget -qO- "${url}" >/dev/null
    return
  fi
  echo "ERROR: neither curl nor wget is available." >&2
  exit 1
}

cleanup_started_processes() {
  if [[ -f "${frontend_pid_file}" ]]; then
    kill "$(cat "${frontend_pid_file}")" 2>/dev/null || true
    rm -f "${frontend_pid_file}"
  fi
  if [[ -f "${backend_pid_file}" ]]; then
    kill "$(cat "${backend_pid_file}")" 2>/dev/null || true
    rm -f "${backend_pid_file}"
  fi
}

require_cmd uv
require_cmd npm

if [[ -f "${backend_pid_file}" ]] || [[ -f "${frontend_pid_file}" ]]; then
  echo "ERROR: existing PID files found. Run make dev-down first." >&2
  exit 1
fi

(
  cd "${repo_root}/backend"
  nohup uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 > "${backend_log_file}" 2>&1 &
  echo $! > "${backend_pid_file}"
)

backend_ready="false"
for _ in {1..20}; do
  backend_pid="$(cat "${backend_pid_file}")"
  if ! kill -0 "${backend_pid}" 2>/dev/null; then
    echo "ERROR: backend process exited before readiness check passed." >&2
    tail -n 40 "${backend_log_file}" >&2 || true
    cleanup_started_processes
    exit 1
  fi
  if http_probe http://127.0.0.1:8000/health; then
    backend_ready="true"
    break
  fi
  sleep 1
done

if [[ "${backend_ready}" != "true" ]]; then
  echo "ERROR: backend health endpoint did not become ready in time." >&2
  tail -n 40 "${backend_log_file}" >&2 || true
  cleanup_started_processes
  exit 1
fi

(
  cd "${repo_root}/frontend"
  nohup npm run dev -- --host 127.0.0.1 --port 5173 > "${frontend_log_file}" 2>&1 &
  echo $! > "${frontend_pid_file}"
)

frontend_ready="false"
for _ in {1..45}; do
  frontend_pid="$(cat "${frontend_pid_file}")"
  if ! kill -0 "${frontend_pid}" 2>/dev/null; then
    echo "ERROR: frontend process exited before readiness check passed." >&2
    tail -n 60 "${frontend_log_file}" >&2 || true
    cleanup_started_processes
    exit 1
  fi
  if http_probe http://127.0.0.1:5173; then
    frontend_ready="true"
    break
  fi
  sleep 1
done

if [[ "${frontend_ready}" != "true" ]]; then
  echo "ERROR: frontend URL did not become ready in time." >&2
  tail -n 60 "${frontend_log_file}" >&2 || true
  cleanup_started_processes
  exit 1
fi

echo "Backend: http://127.0.0.1:8000"
echo "Frontend: http://127.0.0.1:5173"
