#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f ".venv/bin/activate" ]; then
  echo "[magic-e2e] Creating virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]" -q
else
  source .venv/bin/activate
fi

echo "[magic-e2e] Running end-to-end validation test pack..."
pytest -q \
  tests/test_e2e_kernel_flow.py \
  tests/test_phase6_live_connectors_and_backbone.py \
  tests/test_event_api_connector_idempotency.py \
  tests/test_state_of_control_engine.py \
  tests/test_event_to_impact_engine.py \
  tests/test_evidence_graph_hardened.py \
  tests/test_dossier_full_package.py \
  tests/test_workflow_views.py \
  tests/test_deterministic_answer.py \
  tests/test_e2e_magic_suite.py

echo "[magic-e2e] Running one-command demo orchestration..."
python -m aeros.kernel.simulation.e2e_magic_suite "$@"
