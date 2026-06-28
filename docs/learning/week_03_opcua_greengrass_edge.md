# Week 03 — OPC UA and Greengrass V2 Edge Gateway

## Learning goal

Understand how the local OPC UA/MQTT simulation maps to an **AWS IoT Greengrass V2** edge pattern.

## What Greengrass V2 means here

A **Greengrass V2 core device** runs local Areos components close to OT systems.

1. Runs **Greengrass V2 components** locally.
2. Hosts read-only OPC UA collector components.
3. Buffers and republishes normalized events to AWS IoT Core UNS topics.
4. Preserves data quality and source lineage.

The local repository simulates that behavior with Python modules, not with a live Greengrass deployment.

## Local-to-AWS mapping

| AWS component | Local equivalent | Code |
|---|---|---|
| Greengrass V2 core device | `run_gateway_loop()` | `ingestion/edge_gateway.py` |
| Greengrass V2 OPC UA component | OPC UA client + gateway loop | `ot/opcua_client.py`, `ingestion/edge_gateway.py` |
| Greengrass V2 MQTT/UNS component | MQTT publisher | `ot/mqtt_publisher.py` |

## OT safety principle

- Read-only-first for OT/GxP safety.
- No inbound cloud-to-PLC control path by default.
- Areos uses Greengrass V2 component/deployment language only.
