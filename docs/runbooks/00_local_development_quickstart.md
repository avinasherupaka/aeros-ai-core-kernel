# 00 Local Development Quickstart (macOS)

This runbook gets you from a fresh clone to a running local MVP in under 10 minutes.

## Prerequisites

| Tool | Install | Version check |
|---|---|---|
| Python 3.11+ | `brew install python@3.12` | `python3 --version` |
| Docker Desktop | https://www.docker.com/products/docker-desktop | `docker --version` |
| Git | `brew install git` | `git --version` |

---

## 1. Clone and set up Python environment

```bash
git clone https://github.com/aerup/aeros-ai-core-kernel.git
cd aeros-ai-core-kernel

# Create isolated virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install project + dev dependencies
pip install -e ".[dev]"
```

Expected output:
```
Successfully installed aeros-ai-core-kernel-0.1.0 fastapi pydantic paho-mqtt asyncua uvicorn ...
```

---

## 2. Run the test suite

```bash
pytest
```

Expected output:
```
31 passed in 0.13s
```

---

## 3. Run the plant topology simulation

```bash
python -m aeros.kernel.simulation.plant_topology
```

Expected output (abbreviated):
```json
{
  "tenant_id": "acme_pharma",
  "site": {"site_id": "hyd_site_01", "name": "Hyderabad Site", ...},
  ...
}
--- Summary ---
Tenant      : acme_pharma
Site        : Hyderabad Site (hyd_site_01)
Room        : Compression Room 1 [GMP critical: True]
Active Batch: BATCH-OSD-2026-001 / hygrostatin_10mg_tablet
```

---

## 4. Run the humidity excursion scenario

```bash
python -m aeros.kernel.simulation.humidity_excursion | head -40
```

---

## 5. Start the API server

```bash
uvicorn aeros.kernel.api.main:app --reload
```

Then open: http://localhost:8000/docs (Swagger UI)

Available endpoints:
- `GET /health`
- `GET /topology`
- `GET /scenario/humidity-excursion`
- `GET /state-of-control/humidity-excursion`

---

## 6. Start MQTT and run the MQTT demo

```bash
# Terminal 1: start Mosquitto broker
docker compose up mqtt

# Terminal 2: start subscriber (waits for messages)
python -m aeros.kernel.ot.mqtt_subscriber

# Terminal 3: publish humidity excursion
python -m aeros.kernel.simulation.humidity_excursion --publish-mqtt
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: aeros` | Activate venv: `source .venv/bin/activate` |
| `pip install` fails on `asyncua` | Install build tools: `xcode-select --install` |
| MQTT publish fails | Start broker: `docker compose up mqtt` |
| OPC UA connection refused | Start server: `python -m aeros.kernel.ot.opcua_server_sim` |
| Port 8000 in use | Use `--port 8001` flag with uvicorn |
