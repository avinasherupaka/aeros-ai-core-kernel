# 009 Connector SDK and Industry Pack Strategy

## Objective
Deliver a stable read-only-first connector SDK for OT/IT systems with strong lineage and evidence traceability.

## SDK contracts
- `ConnectorManifest`
- `ConnectorHealth`
- `BaseConnector` lifecycle methods
- Record lineage fields (`tenant_id`, `site_id`, `connector_id`, source, timestamps)

## Industry packs (priority sequence)
1. OPC UA + MQTT + file import (foundation)
2. Historian/BMS/MES adapters
3. QMS/LIMS/CMMS enterprise adapters

## Maturity model
L0 through L6 as described in `docs/architecture/connector_ecosystem_strategy.md`.
