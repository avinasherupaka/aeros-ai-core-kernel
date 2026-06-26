# 03 Run OPC UA to MQTT Gateway

This runbook demonstrates the Greengrass-style edge gateway pattern: read tags from
an OPC UA server and publish them to the MQTT UNS broker.

## AWS equivalent

```
On-premises:
  BMS OPC UA server (e.g. Siemens S7, Rockwell, Kepware)
    → Greengrass OPC UA collector component
      → Greengrass Stream Manager
        → AWS IoT Core MQTT

Local MVP:
  asyncua server simulator
    → Python edge gateway (poll loop)
      → Mosquitto MQTT
```

---

## Step 1: Start the MQTT broker

```bash
docker compose up mqtt
```

---

## Step 2: Start the OPC UA server simulator (new terminal)

```bash
source .venv/bin/activate
python -m aeros.kernel.ot.opcua_server_sim
```

Expected output:
```
[opcua-server] Endpoint : opc.tcp://0.0.0.0:4840/freeopcua/server/
[opcua-server] Namespace: areos.opcua.sim
[opcua-server] Tags exposed:
  - CompressionRoomMetrics/RelativeHumidity
  - CompressionRoomMetrics/Temperature
  - CompressionRoomMetrics/DifferentialPressure
  - CompressionRoomMetrics/AHUStatus
  - CompressionRoomMetrics/TabletPressState
[opcua-server] Running — press Ctrl-C to stop
```

The simulator cycles through the humidity excursion profile (49 → 63 → 49 %RH).

---

## Step 3: Read tags with the OPC UA client (optional verification)

```bash
source .venv/bin/activate
python -m aeros.kernel.ot.opcua_client
```

Expected output:
```
[opcua-client] Connecting to opc.tcp://localhost:4840/freeopcua/server/
[opcua-client] CompressionRoomMetrics:
  RelativeHumidity               = 49.0
  Temperature                    = 23.0
  DifferentialPressure           = 15.0
  AHUStatus                      = RUNNING
  TabletPressState               = EXECUTE
```

---

## Step 4: Start the MQTT subscriber (new terminal)

```bash
source .venv/bin/activate
python -m aeros.kernel.ot.mqtt_subscriber
```

---

## Step 5: Start the edge gateway (new terminal)

```bash
source .venv/bin/activate
python -m aeros.kernel.ingestion.edge_gateway
```

Expected output:
```
[edge-gateway] MQTT topic   : areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/utility/relative_humidity
[edge-gateway] OPC UA source: opc.tcp://localhost:4840/freeopcua/server/
[edge-gateway] Poll interval: 5.0s
[edge-gateway] Starting loop — press Ctrl-C to stop
[edge-gateway] [2026-...] RH=49.0%  quality=GOOD  seq=0
[edge-gateway] [2026-...] RH=49.0%  quality=GOOD  seq=1
```

---

## Simulation fallback (no OPC UA server needed)

If you don't want to run the OPC UA server:

```bash
python -m aeros.kernel.ingestion.edge_gateway --simulation-fallback
```

This uses the in-process humidity profile instead of reading from OPC UA.
`quality=SIMULATED` in the published envelopes indicates the fallback source.

---

## Data quality and lineage

Every published message from the gateway includes:
- `quality`: `GOOD` (from OPC UA) or `SIMULATED` (fallback)
- `source_protocol`: `opcua` or `simulated`
- `source_system`: `bms`
- `trace_id`: unique UUID per reading for end-to-end tracing

This lineage is required for GxP evidence records — QA must be able to trace
any value back to its original source system and timestamp.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `asyncua` import error | Run `pip install -e ".[dev]"` |
| OPC UA connection refused in gateway | Start server first: `python -m aeros.kernel.ot.opcua_server_sim` |
| MQTT publish failed | Start broker: `docker compose up mqtt` |
| Slow startup (asyncua) | Normal — OPC UA stack initialises in ~2s |
