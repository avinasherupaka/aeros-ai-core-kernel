#!/usr/bin/env bash
# Run the OSD plant topology simulation and print the hierarchy.
# Usage: ./scripts/run_topology.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f ".venv/bin/activate" ]; then
  echo "[run_topology] Creating virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]" -q
else
  source .venv/bin/activate
fi

echo "[run_topology] Running OSD plant topology simulation..."
python -m aeros.kernel.simulation.plant_topology
