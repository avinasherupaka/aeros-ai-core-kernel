# 02 Run MQTT Simulation

This runbook shows how to run the full MQTT demo end-to-end on macOS.

## What this demonstrates

- Mosquitto MQTT broker running locally in Docker (AWS IoT Core equivalent).
- A subscriber listening on `areos/#` wildcard topic.
- The humidity excursion simulation publishing 60 Sparkplug-inspired messages.
- Each message carries: tenant/site/asset lineage, metric value, quality, trace_id.

---

## Step 1: Start the MQTT broker

```bash
docker compose up mqtt
```

Expected output:
```
areos-mosquitto  | mosquitto version 2.x.x starting
areos-mosquitto  | Opening ipv4 listen socket on port 1883.
```

Mosquitto config: `docker/mosquitto/mosquitto.conf`
This enables anonymous connections on port 1883 (local dev only).

---

## Step 2: Start the subscriber (new terminal)

```bash
source .venv/bin/activate
python -m aeros.kernel.ot.mqtt_subscriber
```

Expected output:
```
[subscriber] Connected to localhost:1883 — subscribing to 'areos/#'
[subscriber] Waiting for messages on 'areos/#' …  (Ctrl-C to stop)
```

The subscriber will print every message as it arrives.

---

## Step 3: Publish the humidity excursion (new terminal)

```bash
source .venv/bin/activate
python -m aeros.kernel.simulation.humidity_excursion --publish-mqtt
```

Expected output:
```
[publish-mqtt] Topic : areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/utility/relative_humidity
[publish-mqtt] Broker: localhost:1883
[publish-mqtt] Events: 60
  [2026-...] RH= 49.0%RH  state=OK
  ...
  [2026-...] RH= 63.0%RH  state=ACTION
  ...
[publish-mqtt] Done — 60 messages published.
```

In the subscriber terminal you will see 60 messages arrive.

---

## Understanding the UNS topic structure

```
areos / {tenant} / {site} / {area} / {room} / {asset} / {data_domain} / {metric}
  areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/utility/relative_humidity
```

This follows the ISA-95 hierarchy. In AWS the topic maps to:
```
AWS IoT Core topic → SiteWise property → EventBridge rule → Lambda handler
```

---

## Understanding the message payload

Each message is a `SparkplugInspiredEnvelope`:
```json
{
  "tenant_id": "acme_pharma",
  "site_id": "hyd_site_01",
  "edge_node_id": "edge_hyd_01",
  "device_id": "ahu_03",
  "metric": "relative_humidity",
  "value": 63.0,
  "unit": "%RH",
  "timestamp": "2026-01-01T08:20:00+00:00",
  "quality": "GOOD",
  "sequence": 20,
  "source_protocol": "simulated",
  "source_system": "bms",
  "trace_id": "uuid-..."
}
```

`trace_id` enables end-to-end evidence tracing from source tag to evidence dossier.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` on publish | Start broker: `docker compose up mqtt` |
| No messages in subscriber | Ensure both terminals use the same `.venv` |
| Docker not found | Install Docker Desktop for Mac |
| Port 1883 in use | Stop conflicting service or change port in `docker-compose.yml` |
