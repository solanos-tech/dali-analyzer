#!/usr/bin/env bash
set -euo pipefail

curl --fail http://127.0.0.1:8000/health >/dev/null
curl --fail "http://127.0.0.1:8000/api/frames?source=mock" >/dev/null
curl --fail http://127.0.0.1:5173 >/dev/null

echo "dev-check passed."
