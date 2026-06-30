# Siemens OPC-UA namespace guide

## Goal
Provide a standard namespace approach for Siemens OPC-UA data mapped into Areos UNS topics.

## Suggested namespace shape
- Root: `ns=2;s=Site/<site_id>/Area/<area_id>/Line/<line_id>`
- Equipment nodes: `.../Equipment/<equipment_id>`
- Parameter nodes: `.../Parameters/<parameter_name>`

## Mapping into Areos
1. OPC-UA connector reads node values in read-only mode.
2. Normalize to canonical event fields (`asset_id`, `metric`, `timestamp`, `value`, `unit`).
3. Publish to MQTT/UNS with QoS 1 for critical parameters.

## Validation checklist
- Namespace browsing returns expected hierarchy.
- Node IDs are stable and deterministic across restarts.
- Critical alarm tags are routed with at-least-once delivery semantics.
