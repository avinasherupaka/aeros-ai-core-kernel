# 003 OT/IT and Unified Namespace

## OT/IT context

- OT sources: OPC UA tags, BMS/EMS/SCADA, utilities, equipment telemetry.
- IT/GxP context: MES, QMS, CMMS, LIMS, ERP, deviations, APQR.

## Unified Namespace (UNS)

Tenant-aware topic convention:

`areos/{tenant}/{site}/{area}/{work_center_or_room}/{asset}/{data_domain}/{metric}`

Benefits:
- Consistent enterprise-control hierarchy context.
- Easier event-to-impact linking.
- Cross-system subscription patterns.

## Messaging pattern

Sparkplug-inspired envelope is used in this MVP for traceability fields (sequence, quality, source system, trace ID), while full Sparkplug B implementation is out of current scope.

## Edge pattern

Greengrass-style edge gateway pattern:
1. Read-only connectors collect OT signals.
2. Local buffering handles intermittent links.
3. Normalized events publish to UNS topics.
