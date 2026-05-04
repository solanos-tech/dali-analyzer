#!/usr/bin/env bash
set -euo pipefail

version="${1:-}"
if [[ -z "${version}" ]]; then
  echo "ERROR: VERSION is required. Example: make release-status VERSION=0.1.8" >&2
  exit 1
fi
if [[ ! "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: VERSION must match X.Y.Z." >&2
  exit 1
fi

tag="v${version}"
gh run list --workflow "Unified Release" --branch "${tag}" --limit 5
gh release view "${tag}" --repo prudek/dali-analyzer
