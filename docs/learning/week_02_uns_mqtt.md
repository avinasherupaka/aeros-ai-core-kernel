# Week 02 — Unified Namespace and MQTT Backbone

## Learning goal

Understand the Unified Namespace (UNS) pattern and how MQTT provides the
data backbone for an industrial plant — and how it maps to AWS IoT Core.

---

## What is a Unified Namespace?

A UNS is a single, hierarchical MQTT topic namespace that represents *all data*
in a plant. Instead of point-to-point connections (BMS → SCADA, SCADA → MES, MES
→ historian — all separate integrations), every system publishes its data to the
UNS and subscribes to what it needs.

```
Before UNS (spaghetti):
  BMS ←→ SCADA ←→ MES ←→ historian ←→ QMS ←→ ERP

After UNS (star):
  All systems → UNS broker ← All consumers
```

The UNS is built on MQTT, which is:
- Lightweight publish/subscribe protocol.
- Originally designed for IoT (satellite-quality bandwidth).
- Topic-based routing: publisher doesn't know who subscribes.
- Used by AWS IoT Core as its primary protocol.

---

## UNS topic structure in Areos

Areos uses an ISA-95-aligned topic hierarchy:

```
areos/{tenant}/{site}/{area}/{room}/{asset}/{data_domain}/{metric}
```

For the AHU-03 humidity tag:
```
areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/utility/relative_humidity
```

This is implemented in `src/aeros/kernel/ot/uns.py`:

```python
from aeros.kernel.ot.uns import build_uns_topic

topic = build_uns_topic(
    tenant="acme_pharma",
    site="hyd_site_01",
    area="osd_manufacturing",
    work_center_or_room="compression_room_1",
    asset="ahu_03",
    data_domain="utility",
    metric="relative_humidity",
)
# → "areos/acme_pharma/hyd_site_01/osd_manufacturing/compression_room_1/ahu_03/utility/relative_humidity"
```

Segment sanitization ensures topic-safe characters.

---

## Sparkplug B inspiration

Sparkplug B is an MQTT payload specification from Eclipse Foundation, widely used
in IIoT. Areos uses a Sparkplug-*inspired* envelope (not full Sparkplug B) that
preserves the key data quality and lineage concepts:

```python
SparkplugInspiredEnvelope(
    tenant_id="acme_pharma",
    site_id="hyd_site_01",
    edge_node_id="edge_hyd_01",   # Greengrass node ID
    device_id="ahu_03",           # source device
    metric="relative_humidity",
    value=63.0,
    unit="%RH",
    quality="GOOD",               # data quality (GOOD / BAD / UNCERTAIN / SIMULATED)
    sequence=20,                  # monotonically increasing
    source_protocol="opcua",      # protocol used to acquire the value
    source_system="bms",          # source system name
    trace_id="uuid-...",          # end-to-end evidence trace ID
)
```

The `trace_id` is critical for GxP: every value that flows from BMS tag → MQTT →
state-of-control engine → evidence dossier can be traced back to its source.

---

## Local MQTT setup

Local broker: Mosquitto (Eclipse) in Docker
AWS equivalent: AWS IoT Core MQTT broker

```bash
docker compose up mqtt
```

The Mosquitto config is at `docker/mosquitto/mosquitto.conf`.

---

## Code walkthrough

| File | Purpose |
|---|---|
| `ot/uns.py` | Build ISA-95 UNS topic strings |
| `ot/sparkplug_envelope.py` | Sparkplug-inspired message payload model |
| `ot/mqtt_publisher.py` | Publish envelopes to Mosquitto |
| `ot/mqtt_subscriber.py` | Subscribe to `areos/#` and print messages |

---

## Run / test

```bash
# Run tests
pytest tests/test_uns.py -v

# Run full MQTT demo (requires Docker)
docker compose up mqtt -d
python -m aeros.kernel.ot.mqtt_subscriber &
python -m aeros.kernel.simulation.humidity_excursion --publish-mqtt
```

---

## AWS equivalent

| Local | AWS |
|---|---|
| Mosquitto broker | AWS IoT Core MQTT endpoint |
| `build_uns_topic()` | IoT Core topic naming policy |
| `SparkplugInspiredEnvelope` | IoT Core message schema (JSON) |
| `MQTTPublisher.publish()` | SDK `IoTDataPlane.publish()` |
| `run_subscriber()` | IoT Core Rule subscription / Lambda trigger |

---

## Why MQTT for pharma?

1. **Low bandwidth** — plants may have limited OT network capacity.
2. **Decoupling** — BMS doesn't need to know about the assurance engine.
3. **Fan-out** — one BMS publish reaches historian, SCADA, Areos simultaneously.
4. **QoS levels** — guaranteed delivery for critical events.
5. **AWS alignment** — IoT Core is MQTT-native; local Mosquitto = production-alike dev.
