# Zero-trust Security Architecture (Phase 1 / Week 3)

Principles:
- No implicit trust between OT LAN, VPN, VPC, or user networks.
- Read-only-first OT integrations.
- No inbound cloud-to-PLC control path by default.
- Strong device identity (certificates, IoT policy scoping).
- Least-privilege IAM and tenant/site isolation.
- Full audit trail targets (CloudTrail/CloudWatch/AWS Config/Security Hub/GuardDuty).
