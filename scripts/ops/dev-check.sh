#!/usr/bin/env bash
set -euo pipefail

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

http_probe http://127.0.0.1:8000/health
http_probe "http://127.0.0.1:8000/api/frames?source=mock"
http_probe http://127.0.0.1:5173

echo "dev-check passed."
