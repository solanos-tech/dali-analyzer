#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
runtime_dir="${root_dir}/.runtime"
bootstrap_dir="${runtime_dir}/bootstrap"
backend_venv="${runtime_dir}/backend-venv"
pid_file="${runtime_dir}/backend.pid"
backend_log="${runtime_dir}/backend.log"
backend_err_log="${runtime_dir}/backend.err.log"
host="${DALI_RUNTIME_HOST:-127.0.0.1}"
port="${DALI_RUNTIME_PORT:-8000}"
health_url="http://${host}:${port}/health"
ui_url="http://${host}:${port}"

resolve_backend_version() {
  local python_path="$1"
  local version="unknown"
  if version="$("${python_path}" -c "import importlib.metadata as m; print(m.version('dali-analyzer-backend'))" 2>/dev/null)"; then
    if [[ -n "${version}" ]]; then
      echo "${version}"
      return
    fi
  fi
  echo "unknown"
}

resolve_frontend_version() {
  local package_json_path="${root_dir}/frontend/package.json"
  local python_path="$1"
  if [[ -f "${package_json_path}" ]]; then
    "${python_path}" -c "import json; print(json.load(open('${package_json_path}', encoding='utf-8')).get('version', 'unknown'))" 2>/dev/null || true
    return
  fi
  echo "unknown"
}

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "ERROR: required command '${cmd}' not found in PATH." >&2
    exit 1
  fi
}

probe_http() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl --silent --fail "${url}" >/dev/null
    return
  fi
  if command -v wget >/dev/null 2>&1; then
    wget -qO- "${url}" >/dev/null
    return
  fi
  echo "ERROR: neither curl nor wget is available for health checks." >&2
  exit 1
}

find_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return
  fi
  echo ""
}

echo "Starting DALI Analyzer runtime..."
echo "Package root: ${root_dir}"

if [[ -f "${pid_file}" ]]; then
  echo "ERROR: existing PID file found (${pid_file}). Run stop-linux.sh first." >&2
  exit 1
fi

python_cmd="$(find_python)"
if [[ -z "${python_cmd}" ]]; then
  echo "ERROR: Python 3 is required but was not found." >&2
  exit 1
fi

require_cmd "${python_cmd}"
mkdir -p "${runtime_dir}"

if [[ ! -x "${bootstrap_dir}/bin/python" ]]; then
  echo "Creating bootstrap sandbox..."
  "${python_cmd}" -m venv "${bootstrap_dir}"
fi

echo "Installing runtime bootstrap dependencies..."
"${bootstrap_dir}/bin/python" -m pip install --upgrade pip >/dev/null
"${bootstrap_dir}/bin/python" -m pip install --upgrade uv >/dev/null
uv_bin="${bootstrap_dir}/bin/uv"

echo "Preparing backend sandbox..."
"${uv_bin}" venv "${backend_venv}" >/dev/null
wheel_file="$(find "${root_dir}/backend/wheels" -maxdepth 1 -type f -name "*.whl" | head -n 1)"
if [[ -z "${wheel_file}" ]]; then
  echo "ERROR: backend wheel not found in ${root_dir}/backend/wheels." >&2
  exit 1
fi
"${uv_bin}" pip install --python "${backend_venv}/bin/python" --upgrade "${wheel_file}" >/dev/null

export FRONTEND_DIST_DIR="${root_dir}/frontend/dist"
export RUNTIME_CONFIG_DIR="${root_dir}/config"
export SIM_LOG_DIR="${root_dir}/logs"
export CORS_ALLOW_ORIGINS="${CORS_ALLOW_ORIGINS:-${ui_url},http://localhost:${port}}"

echo "Launching backend..."
nohup "${backend_venv}/bin/python" -m uvicorn app.main:app --host "${host}" --port "${port}" >"${backend_log}" 2>"${backend_err_log}" &
echo $! > "${pid_file}"
backend_pid="$(cat "${pid_file}")"
echo "Backend PID: ${backend_pid}"
echo "Waiting for health: ${health_url}"

ready="false"
for _ in {1..60}; do
  if ! kill -0 "${backend_pid}" 2>/dev/null; then
    echo "ERROR: backend process exited before readiness." >&2
    tail -n 80 "${backend_log}" >&2 || true
    tail -n 80 "${backend_err_log}" >&2 || true
    rm -f "${pid_file}"
    exit 1
  fi

  if probe_http "${health_url}"; then
    ready="true"
    break
  fi
  sleep 1
done

if [[ "${ready}" != "true" ]]; then
  echo "ERROR: backend did not become healthy in time." >&2
  tail -n 80 "${backend_log}" >&2 || true
  tail -n 80 "${backend_err_log}" >&2 || true
  exit 1
fi

echo "Runtime is READY"
echo "Diagnostics:"
echo "Backend version: $(resolve_backend_version "${backend_venv}/bin/python")"
echo "Frontend version: $(resolve_frontend_version "${backend_venv}/bin/python")"
echo "UI URL: ${ui_url}"
echo "Health URL: ${health_url}"
echo "Logs: ${backend_log}"
echo "Error logs: ${backend_err_log}"
