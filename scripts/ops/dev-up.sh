#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
ops_dir="${repo_root}/.ops"
mkdir -p "${ops_dir}"

if [[ -f "${ops_dir}/backend.pid" ]] || [[ -f "${ops_dir}/frontend.pid" ]]; then
  echo "ERROR: existing PID files found. Run make dev-down first." >&2
  exit 1
fi

(
  cd "${repo_root}/backend"
  nohup uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 > "${ops_dir}/backend.log" 2>&1 &
  echo $! > "${ops_dir}/backend.pid"
)

for _ in {1..20}; do
  if curl --silent --fail http://127.0.0.1:8000/health >/dev/null; then
    break
  fi
  sleep 1
done

curl --silent --fail http://127.0.0.1:8000/health >/dev/null

(
  cd "${repo_root}/frontend"
  nohup npm run dev -- --host 127.0.0.1 --port 5173 > "${ops_dir}/frontend.log" 2>&1 &
  echo $! > "${ops_dir}/frontend.pid"
)

echo "Backend: http://127.0.0.1:8000"
echo "Frontend: http://127.0.0.1:5173"
