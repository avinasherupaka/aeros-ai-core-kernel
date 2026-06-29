# Resilience and Scale Test Plan

- Re-run connector replay windows with bounded `max_records`.
- Exercise local API endpoints under repeated calls.
- Validate dossier regeneration is idempotent for the same event.
- Future AWS-native work: multi-cell load, queue backpressure, regional failover, and Bedrock rate-limit testing.
