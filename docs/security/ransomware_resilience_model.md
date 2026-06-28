# Ransomware Resilience Model

- No SMB/network shares as primary integration path.
- Prefer API/OPC UA/MQTT read-only connectors.
- Immutable-style evidence retention strategy.
- Segmented tenant/site blast radius.
- Incident response drill: isolate connector, preserve evidence, fail-safe ingestion.
