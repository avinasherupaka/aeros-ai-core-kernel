#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TF_ROOT="$ROOT_DIR/environments"

if ! command -v terraform >/dev/null 2>&1; then
  echo "terraform not installed; skipping terraform validation"
  exit 0
fi

terraform -chdir="$TF_ROOT" fmt -check -recursive

for env in dev qa prod; do
  echo "[terraform] validating env: $env"
  terraform -chdir="$TF_ROOT/$env" init -backend=false -input=false >/dev/null
  terraform -chdir="$TF_ROOT/$env" validate
done
