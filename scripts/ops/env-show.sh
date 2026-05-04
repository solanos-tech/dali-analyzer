#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/env-lib.sh"

current_env="$(resolve_env)"
validate_env "${current_env}"
echo "${current_env}"
