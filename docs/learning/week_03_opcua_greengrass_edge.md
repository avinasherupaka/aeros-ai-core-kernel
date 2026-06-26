# Week 03 — OPC UA and Greengrass-style Edge Gateway

## Learning goal

Understand OPC UA as the industrial standard for plant data access, how AWS
IoT Greengrass bridges OT to the cloud, and how the local edge gateway simulates
this pattern.

---

## What is OPC UA?

OPC UA (OPC Unified Architecture) is the dominant industrial protocol for reading
data from PLCs, BMS controllers, SCADA systems, and field devices. It provides:

- **Secure, authenticated** connections (unlike raw Modbus/Profibus).
- **Self-describing** data: you can browse the server's address space to discover
  available tags without a configuration file.
- **Rich data types**: timestamps, data quality, engineering units.
- **Platform-independent**: runs on Windows, Linux, embedded devices.

In pharma plants, the BMS (Building Management System) that monitors humidity,
temperature, and differential pressure typically exposes an OPC UA server. The
EMS (Energy Management System), SCADA, and process historians may also.

---

## What is AWS IoT Greengrass?

Greengrass is AWS's edge computing framework. A Greengrass core device runs
on-premises (on an industrial PC or gateway hardware) and:

1. Runs **components** (Lambda functions or Docker containers) locally.
2. Hosts the **OPC UA collector component** — reads tags from OPC UA servers.
3. Buffers data locally if connectivity is lost (stream manager).
4. Forwards data to **AWS IoT Core MQTT** when connected.
5. Receives configuration updates from the cloud.

```
BMS OPC UA server
  → Greengrass OPC UA collector (reads tags every N seconds)
    → Greengrass Stream Manager (local buffer + ordering)
      → AWS IoT Core MQTT (topic: areos/{hierarchy}/{metric})
        → SiteWise / Lambda / EventBridge
```

The key design principle: **Greengrass is read-only on the OT side**.
It reads data but never writes back to the BMS. This is the "read-only-first" rule.

---

## Local MVP equivalent

```
asyncua OPC UA server simulator
  → Python edge gateway (EdgeGateway class, poll loop)
    → Mosquitto MQTT broker (same topic structure)
```

| AWS component | Local equivalent | Code |
|---|---|---|
| OPC UA endpoint (BMS) | `asyncua` server sim | `ot/opcua_server_sim.py` |
| Greengrass OPC UA collector | `asyncua` client | `ot/opcua_client.py` |
| Greengrass core device | `run_gateway_loop()` | `ingestion/edge_gateway.py` |
| Stream Manager | `publish_many()` batch | `ot/mqtt_publisher.py` |
| IoT Core MQTT | Mosquitto | `docker/mosquitto/` |

---

## The OPC UA address space

The local server sim exposes:
```
Objects/
  CompressionRoomMetrics/
    RelativeHumidity     (float, %RH)
    Temperature          (float, °C)
    DifferentialPressure (float, Pa)
    AHUStatus            (string)
    TabletPressState     (string)
```

Browse and read these with:
```bash
python -m aeros.kernel.ot.opcua_client
```

---

## Data quality propagation

OPC UA provides data quality (Good / Bad / Uncertain) on every tag read. The edge
gateway preserves this in the `quality` field of the Sparkplug envelope:

| Source | Quality value |
|---|---|
| OPC UA Good | `"GOOD"` |
| OPC UA Bad | `"BAD"` |
| Simulation fallback | `"SIMULATED"` |

This quality attribute flows all the way to the `StateOfControlAssessment` and
must be included in any GxP evidence record.

---

## Run / test

```bash
# Terminal 1: OPC UA server
python -m aeros.kernel.ot.opcua_server_sim

# Terminal 2: verify with OPC UA client
python -m aeros.kernel.ot.opcua_client

# Terminal 3: start broker + gateway
docker compose up mqtt -d
python -m aeros.kernel.ingestion.edge_gateway

# Or use simulation fallback (no OPC UA server needed)
python -m aeros.kernel.ingestion.edge_gateway --simulation-fallback
```

---

## Shop-floor context: what "read-only" means

In a pharma plant, the OT network (BMS, SCADA, PLC) is considered a **validated
system**. Any change to validated systems requires:
- Change control documentation
- Impact assessment
- Re-validation testing
- QA approval

Writing data from Areos back to the BMS would constitute a change to a validated
system. This is why Areos is **read-only-first**: it observes and records, but
never modifies the source system's state or configuration.

This is also a commercial argument: customers don't need to validate Areos as
a controller — only as an observer/recorder, which is a much lighter validation burden.

---

## AWS equivalent summary

| Concept | AWS | Local |
|---|---|---|
| OPC UA data source | On-premises BMS/EMS | `asyncua` server sim |
| Protocol bridge | Greengrass OPC UA collector | `asyncua` client in gateway |
| Edge buffering | Greengrass Stream Manager | In-memory list / batch publish |
| Connectivity to cloud | Greengrass MQTT forwarder | Direct Mosquitto publish |
| Data quality | OPC UA Good/Bad/Uncertain | `quality` field in envelope |
| Read-only principle | Greengrass component has read-only IAM | `read_only=True` in EvidenceSource |
