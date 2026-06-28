# OT/IT Zero Trust Threat Model

Primary threats:
- Credential reuse/shared static secrets.
- Unrestricted broker topics.
- Lateral movement from IT to OT.
- Connector privilege escalation.

Controls:
- Scoped topic policies and identities per tenant/site gateway.
- Secrets rotation and no static shared keys.
- Strict egress controls and connector sandboxing.
- Centralized logging and alerting.
