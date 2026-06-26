#!/usr/bin/env bash
# Run the Dendrix humidity excursion scenario.
# Usage:
#   ./scripts/run_humidity_scenario.sh              # print JSON
#   ./scripts/run_humidity_scenario.sh --publish-mqtt  # publish to MQTT
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f ".venv/bin/activate" ]; then
  echo "[run_humidity] Creating virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]" -q
else
  source .venv/bin/activate
fi

echo "[run_humidity] Running humidity excursion simulation..."
python -m aeros.kernel.simulation.humidity_excursion "$@"
