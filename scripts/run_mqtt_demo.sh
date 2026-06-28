#!/usr/bin/env bash
# Run the full MQTT demo:
#   1. Start MQTT broker (Mosquitto via Docker)
#   2. Start subscriber in background
#   3. Publish humidity excursion events
# Usage: ./scripts/run_mqtt_demo.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ ! -f ".venv/bin/activate" ]; then
  echo "[mqtt-demo] Creating virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -e ".[dev]" -q
else
  source .venv/bin/activate
fi

echo "[mqtt-demo] Step 1: Starting MQTT broker..."
docker compose up mqtt -d
sleep 2

echo "[mqtt-demo] Step 2: Starting subscriber (background)..."
python -m aeros.kernel.ot.mqtt_subscriber &
SUBSCRIBER_PID=$!
sleep 1

echo "[mqtt-demo] Step 3: Publishing humidity excursion events..."
python -m aeros.kernel.simulation.humidity_excursion --publish-mqtt

echo "[mqtt-demo] Done. Stopping subscriber..."
kill "$SUBSCRIBER_PID" 2>/dev/null || true
