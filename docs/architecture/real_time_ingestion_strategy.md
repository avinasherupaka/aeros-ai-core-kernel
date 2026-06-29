# Real-Time Ingestion Strategy

## Positioning

Areos is a system of assurance, not a system of record. Ingestion therefore prioritizes timely, attributable, replay-safe evidence capture rather than ownership of the original business transaction.

## Production ingestion priority order

1. native events/webhooks
2. APIs/OData/REST/SOAP
3. OT protocols via Greengrass V2/SiteWise Edge
4. historian streaming/query APIs
5. enterprise event bus
6. managed transfer/SFTP fallback
7. manual file import — legacy onboarding/backfill only

## Why this order matters

### 1. Native events/webhooks
Preferred because they minimize polling lag, preserve source intent, and support near-immediate assurance flows.

### 2. APIs/OData/REST/SOAP
Preferred when webhooks are unavailable but source systems expose supported interfaces for reliable pull or event retrieval.

### 3. OT protocols via Greengrass V2 / SiteWise Edge
Used for industrial telemetry and equipment context at the site edge with read-only-first controls.

### 4. Historian streaming/query APIs
Important for operational reconstruction, bounded replay, and historical context when source equipment integrations are indirect.

### 5. Enterprise event bus
Valuable for enterprise-wide process triggers, status transitions, or asynchronous system-to-system propagation.

### 6. Managed transfer / SFTP fallback
Acceptable where source modernization has not occurred, but lower priority due to latency and operational overhead.

### 7. Manual file import
Only for legacy onboarding, bulk backfill, customer migration, or developer/test harness workflows.

## File connector repositioning

File-backed connectors remain useful in the repository, but only as:
- legacy onboarding support
- bulk historical backfill
- test harness utilities
- sample-data replay tools

They are **not** the production-preferred ingestion pattern.

## Target runtime pattern

### Site edge
- Greengrass V2 core device
- read-only connectors
- local buffering and replay
- UNS/lineage normalization before cloud publication

### Cloud ingress
- IoT Core for telemetry/event entry
- IoT Rules, EventBridge, and SQS/DLQ for routing and durability
- SiteWise for industrial asset/time-series persistence

### Deterministic processing handoff
All ingested events should be transformed into a canonical source event envelope, fingerprinted, checked for idempotency, and passed to deterministic processing services.

## Design safeguards

- tenant/site scoping on every event
- stable ISO-8601 timestamps
- canonical fingerprints for replay safety
- explicit connector/source typing
- raw payload preservation for auditability
- local buffering for intermittent connectivity
- no assumption that semantic retrieval equals regulated truth

## Commercial language

**Do not sell monitoring; sell proof.** The ingestion architecture is valuable because it preserves attributable evidence quickly enough to support real operational decisions while remaining deterministic, governed, and auditable.
