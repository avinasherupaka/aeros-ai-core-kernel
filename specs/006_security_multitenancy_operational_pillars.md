# 006 Security, Multi-tenancy, Operational Pillars

## Security and data residency

- Read-only OT integration by default.
- No PLC/BMS/SCADA writeback in MVP.
- TLS/mTLS assumed for IoT Core target.
- KMS encryption target for data at rest.
- CloudTrail/CloudWatch target for auditability.
- Initial region strategy: `ap-south-1` where feasible.

## Multi-tenancy and isolation

- Tenant → Site → Area → Room → Asset modeled in IDs/topics/paths.
- Tenant ID included in canonical records and evidence storage paths.
- MVP uses logical isolation.
- Future options: pooled/siloed/hybrid with per-tenant account/VPC/KMS controls.

## Operational efficiency

- Managed-service-first target design.
- Event-driven routing and retry/backpressure planning.
- Edge buffering for network interruption handling.
- Cost-aware persistence and aggregation strategy.
