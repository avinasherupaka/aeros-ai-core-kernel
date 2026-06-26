#!/usr/bin/env bash
# Start the Areos Kernel API server.
# Usage: ./scripts/run_api.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f ".venv/bin/activate" ]; then
  echo "[run_api] Creating virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]" -q
else
  source .venv/bin/activate
fi

echo "[run_api] Starting Areos Kernel API..."
echo "[run_api] Endpoints:"
echo "  GET http://localhost:8000/health"
echo "  GET http://localhost:8000/topology"
echo "  GET http://localhost:8000/scenario/humidity-excursion"
echo "  GET http://localhost:8000/state-of-control/humidity-excursion"
echo "  GET http://localhost:8000/docs   (Swagger UI)"
echo ""
uvicorn aeros.kernel.api.main:app --reload --host 0.0.0.0 --port 8000
