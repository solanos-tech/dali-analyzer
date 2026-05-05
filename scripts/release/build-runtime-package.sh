#!/usr/bin/env bash
set -euo pipefail

tag="${1:-}"
if [[ -z "${tag}" ]]; then
  echo "ERROR: tag is required. Example: ./scripts/release/build-runtime-package.sh v0.9.0" >&2
  exit 1
fi
if [[ ! "${tag}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: tag must match vX.Y.Z." >&2
  exit 1
fi

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${repo_root}"

runtime_name="runtime-${tag}"
artifacts_dir="${repo_root}/release-artifacts"
stage_dir="${artifacts_dir}/${runtime_name}"
zip_path="${artifacts_dir}/${runtime_name}.zip"

rm -rf "${stage_dir}"
rm -f "${zip_path}"
mkdir -p "${stage_dir}/launchers" "${stage_dir}/backend/wheels" "${stage_dir}/frontend" "${stage_dir}/config" "${stage_dir}/logs"

cp backend/dist/*.whl "${stage_dir}/backend/wheels/"
cp -R frontend/dist "${stage_dir}/frontend/"
cp packaging/runtime/launchers/start-linux.sh "${stage_dir}/launchers/start-linux.sh"
cp packaging/runtime/launchers/stop-linux.sh "${stage_dir}/launchers/stop-linux.sh"
cp packaging/runtime/launchers/start-windows.ps1 "${stage_dir}/launchers/start-windows.ps1"
cp packaging/runtime/launchers/stop-windows.ps1 "${stage_dir}/launchers/stop-windows.ps1"
cp packaging/runtime/config/runtime-config.json "${stage_dir}/config/runtime-config.json"
cp docs/standards/sniffer_log_example.log "${stage_dir}/logs/sniffer_log_example.log"
cp packaging/runtime/README.md "${stage_dir}/README.md"

chmod +x "${stage_dir}/launchers/start-linux.sh" "${stage_dir}/launchers/stop-linux.sh"

(
  cd "${artifacts_dir}"
  zip -rq "${runtime_name}.zip" "${runtime_name}"
)

echo "Created ${zip_path}"
