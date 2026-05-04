#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/env-lib.sh"

current_env="$(resolve_env)"
validate_env "${current_env}"

if [[ "${current_env}" == "prod" ]]; then
  echo "ERROR: deploy is disabled for 'prod'. Use release-prepare and release-publish." >&2
  exit 1
fi

echo "Deploy trigger contract for '${current_env}' is CI/CD-driven on push to main."
echo "No local deploy action is executed by this command."
